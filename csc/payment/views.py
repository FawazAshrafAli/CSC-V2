from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, View
from django.conf import settings
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from django.templatetags.static import static
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import razorpay
import logging

from .models import Payment, Price
from csc_center.models import CscCenter, ExpiredCscCenter, ExpiringCscCenter
from home.views import BaseHomeView

from .tasks import send_payment_success_email

logger = logging.getLogger(__name__)


@method_decorator(never_cache, name="dispatch")
class PaymentView(BaseHomeView, CreateView):
    model = Payment
    fields = "__all__"
    template_name = 'payment.html'    
    redirect_url = reverse_lazy('users:home')

    def get_redirect_url(self):
        try:
            if get_object_or_404(CscCenter, slug = self.kwargs.get('slug'), status = "Approved"):
                return reverse_lazy('payment:payment', kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in fetching the redirect url of payment view: {e}")

        return self.redirect_url

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

            amount_in_paisa = amount * 100
                
            currency = "INR"

            payment_data = {
                "amount": amount_in_paisa,
                "currency": "INR",
                "payment_capture": "1"
            }        

            order = client.order.create(data=payment_data)

            try:
                csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'), status = "Approved")
            except Http404:
                return redirect(self.get_redirect_url())

            self.model.objects.create(csc_center = csc_center, order_id = order['id'], amount = amount, status = "Created")

            context.update({
                "razorpay_order_id": order['id'],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount": amount,
                "amount_in_paisa": amount_in_paisa,
                "currency": currency,
                "csc_center": csc_center,            
            })
        
        except Exception as e:
            logger.exception(f"Error in fetching context data in payment view: {e}")

        return context
    
    def get(self, request, *args, **kwargs):
        try:
            csc_center = get_object_or_404(CscCenter, slug = self.kwargs.get('slug'), status = "Approved")

            date_after_30_days = timezone.now().date() + timedelta(days=30)            
            payment_link_active = bool(date_after_30_days >= csc_center.next_payment_date)

            if csc_center.is_active == True and not payment_link_active:                
                return redirect(reverse_lazy('home:error404'))            

        except Http404:
            return redirect(self.get_redirect_url())
        except Exception as e:
            logger.exception("Error in fetching csc center object: %s", e)
            messages.error(request, "Error in fetching csc center object")
            return redirect(self.get_redirect_url())
        return super().get(request, *args, **kwargs)
    

@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(never_cache, name="dispatch")
class PaymentSuccessView(BaseHomeView, View):
    success_url = redirect_url = reverse_lazy('users:home')
    error_msg = "Payment Failed!"            
    
    def post(self, request, *args, **kwargs):
        try:            

            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            csc_center = request.POST.get('csc_center')

            try:
                csc_center = get_object_or_404(CscCenter, slug = csc_center, status = "Approved")
            except Http404:
                pass

            if not razorpay_payment_id or not razorpay_order_id or not csc_center:
                messages.error(request, self.error_msg)
                return redirect(self.redirect_url)        

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
                csc_center.last_paid_date = payment.updated.date()
                csc_center.save()

                relative_image_url = static('images/logo.png')
                full_image_url = request.build_absolute_uri(relative_image_url)

                send_payment_success_email.delay(payment.id, full_image_url)

                ExpiringCscCenter.objects.filter(csc_center = csc_center).delete()
                ExpiredCscCenter.objects.filter(csc_center = csc_center).delete()

                messages.success(request, "Payment Completed. Your account is now activated.")
                return redirect(self.success_url)
            else:
                messages.error(request, self.error_msg)
                return redirect(self.redirect_url)        
                
        except Http404:
            messages.error(request, self.error_msg)
            return redirect(self.redirect_url)        
        
        except Exception as e:
            logger.exception(f"Error in payment completion: {e}")
            messages.error(request, self.error_msg)
            return redirect(self.redirect_url)        



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