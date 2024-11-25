from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, View
from django.conf import settings
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from django.templatetags.static import static
import razorpay
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import logging

from .models import Payment, Price
from csc_center.models import CscCenter
from users.views import BaseUserView

from .tasks import send_payment_success_email

logger = logging.getLogger(__name__)


@method_decorator(never_cache, name="dispatch")
class PaymentView(BaseUserView, CreateView):
    model = Payment
    fields = "__all__"
    template_name = 'payment.html'
    redirect_url = reverse_lazy('payment:payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            price_obj = Price.objects.all().first()
            amount = price_obj.price

            today = timezone.now().date()

            if price_obj.offer_price:
                if today >= price_obj.from_date and today <= price_obj.to_date:
                    amount = price_obj.offer_price
                
            currency = "INR"

            payment_data = {
                "amount": amount * 100,
                "currency": "INR",
                "payment_capture": "1"
            }        

            order = client.order.create(data=payment_data)

            try:
                csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
            except Http404:
                return redirect(self.redirect_url)

            self.model.objects.create(csc_center = csc_center, order_id = order['id'], amount = amount, status = "Created")

            context.update({
                "razorpay_order_id": order['id'],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "currency": currency,
                "csc_center": csc_center,
                "user_center": csc_center,
            })
        
        except Exception as e:
            logger.exception("Error in fetching context data in payment view")

        return context
    
    def get(self, request, *args, **kwargs):
        try:
            csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
            if csc_center.is_active == True:
                return redirect(reverse_lazy('home:error404'))
            
            session_expiry = request.session.get_expiry_age()            
            cache.set('current_session_expiry', session_expiry, timeout=None)            
            request.session.set_expiry(2419200)

        except Http404:
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception("Error in fetching csc center object: %s", e)
            messages.error(request, "Error in fetching csc center object")
            return redirect(self.redirect_url)
        return super().get(request, *args, **kwargs)
    

@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(never_cache, name="dispatch")
class PaymentSuccessView(BaseUserView, View):
    success_url = reverse_lazy('users:home')
    
    def post(self, request, *args, **kwargs):
        try:            
            session_expiry = cache.get('current_session_expiry')
            request.session.set_expiry(session_expiry)

            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            csc_center = request.POST.get('csc_center')

            try:
                csc_center = get_object_or_404(CscCenter, slug = csc_center)
            except Http404:
                pass
                
            if not razorpay_payment_id or not razorpay_order_id or not csc_center:
                return JsonResponse({"status": "Payment failed!", "message": "Missing payment or order ID"}, status=400)    

            payment = get_object_or_404(Payment, order_id = razorpay_order_id)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment_details = client.payment.fetch(razorpay_payment_id)

            payment_method = payment_details['method']
            card_last4 = payment_details.get('card', {}).get('last4', None)     

            if razorpay_payment_id:
                payment.payment_id = razorpay_payment_id
                payment.status = "Completed"
                payment.payment_method = str(payment_method).capitalize()
                if card_last4:
                    payment.card_last4 = card_last4
                payment.save()

                csc_center.is_active = True
                csc_center.status = "Paid"
                csc_center.save()

                relative_image_url = static('images/logo.png')
                full_image_url = request.build_absolute_uri(relative_image_url)

                send_payment_success_email.delay(payment.id, full_image_url)
                messages.success(request, "Payment Completed. Your account is now activated.")
                return redirect(self.success_url)
            else:
                return JsonResponse({"status": "Payment failed!"})        
                
        except Http404:            
            return JsonResponse({"status": "Invalid order!"})
        
        except Exception as e:
            logger.exception(f"Error in payment completion: {e}")
            return JsonResponse({"error": "Error in payment completion"})


def get_price(request):
    try:
        price = Price.objects.all().first()
        if price:
            data = {"price": price.price}
            if price.offer_price:
                today = timezone.now().date()
                if today <= price.from_date and price.from_date < price.to_date:
                    data = {
                    "price": price.offer_price,
                    "from_date": price.from_date if price.from_date else None,
                    "to_date": price.to_date if price.to_date else None,
                    "description": price.description if price.description else None,
                }
        else:
            data = {"error": "No price found!"}

        return JsonResponse(data)
    except Exception as e:
        logger.exception("Error in getting price: %s", e)
        return JsonResponse("Error in getting price")