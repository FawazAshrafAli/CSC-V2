import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse, Http404
from django.views.generic import TemplateView, View, DetailView, ListView, CreateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib import messages
from urllib.parse import quote
from django.conf import settings
import logging


from blog.models import Blog
from csc_center.models import CscCenter, State, District, Block, CscKeyword
from services.models import Service, ServiceEnquiry
from products.models import Product, ProductEnquiry
from faq.models import Faq
from base.views import BaseView

logger = logging.getLogger(__name__)

class Error404(TemplateView):
    template_name = "error404.html"


@method_decorator(never_cache, name="dispatch")
class BaseHomeView(View):
    def get_context_data(self, **kwargs):
        context = {}

        try:
            services = Service.objects.all()
            context["service_group_1"] = services[:6] if len(services) > 0 else None
            context["service_group_2"] = services[6:12] if len(services) > 6 else None
            context["service_group_3"] = services[12:18] if len(services) > 12 else None
            context['services'] = services
            
            states = State.objects.all()
            context['states'] = states
            context['footer_states'] = states.exclude(state = "nan")
            context['faqs'] = Faq.objects.all()
            context['home_page'] = True

            user = self.request.user
            if user.is_authenticated:
                context['username'] = user.username
                if not user.is_superuser:
                    try:
                        if user.email:
                            user_center = CscCenter.objects.filter(email=user.email).first()
                            if user_center:
                                context['user_center'] = user_center
                    except Exception as e:
                        logger.error(f"Error retrieving CSC Center for user {user.username}: {e}")
        
        except Exception as e:
            logger.exception("Error in fetchin base hom view context data: %s", e)

        return context


class HomePageView(BaseHomeView, TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['products'] = Product.objects.all()
            context['blogs'] = Blog.objects.all()
            context["keywords"] = CscKeyword.objects.all()
        except Exception as e:
            logger.exception("Error in fetching home page context data: %s", e)
        return context
    

class SearchCscCenterView(HomePageView, ListView):
    model = CscCenter
    template_name = 'home/list.html'
    redirect_url = reverse_lazy('home:view')

    def encode_parameter(self, param):
        if param:
            return quote(param)
        return None
    
    def initial(self, request, *args, **kwargs):
        try:
            pincode = request.GET.get('pincode', None)
            state = request.GET.get('state', None)
            district = request.GET.get('district', None)
            block = request.GET.get('block', None)

            context = self.get_context_data(**kwargs)

            if pincode:
                centers = CscCenter.objects.filter(zipcode = pincode, is_active = True)
                context['pincode'] = pincode

                if len(centers) > 0 or (not state and not district and not block):
                    return centers, context

            if state:
                try:
                    state = get_object_or_404(State, state=state)
                    kwargs['state'] = state
                except Http404:
                    pass

            if district:
                try:
                    district = get_object_or_404(District, district=district)
                    kwargs['district'] = district
                except Http404:
                    pass

            if block:
                try:
                    block = get_object_or_404(Block, block=block)
                    kwargs['block'] = block
                except Http404:
                    pass

            kwargs['is_active'] = True
            centers = CscCenter.objects.filter(**kwargs)

            if block:
                location = block
            elif district:
                location = district
            elif state:
                location = state
            else:
                location = None

            context.update({
                'state_obj': state if state else None,
                'district_obj': district if district else None,
                'block_obj': block if block else None,
                "meta_state": self.encode_parameter(state.state) if state else None,
                "meta_district": self.encode_parameter(district.district) if district else None,
                "meta_block": self.encode_parameter(block.block) if block else None,
                'location': location,
                'districts': District.objects.filter(state = state) if state else None,
                'blocks': Block.objects.filter(state = state, district = district) if state and district else None,
                })

            return centers, context
        except Exception as e:
            logger.exception("Error in getting center dat and context data in csc center search view, %s", e)
            return [], {}
    
    def get(self, request, *args, **kwargs):
        try:            
            centers, context = self.initial(request, *args, **kwargs)
            centers = centers.order_by('name')
            context.update({
                'centers': centers,          
                })
            return render(request, self.template_name, context)
        except Exception as e:
            logger.exception("Error in rendering csc center search view: %s", e)
            messages.error(request, "Something went wrong")
            return redirect(self.redirect_url)    


class FilterAndSortCscCenterView(SearchCscCenterView):
    def get(self, request, *args, **kwargs):
        try:
            services = request.GET.getlist('services[]', None)
            listing = request.GET.get('listing', None)

            centers, context = self.initial(request, *args, **kwargs)

            filtered_centers = centers

            for center in centers:
                set_services = set()
                for service in center.services.all():
                    set_services.add(service.slug)
                if not set(services).issubset(set_services):
                    filtered_centers = filtered_centers.exclude(pk=center.pk)

            filtered_centers = filtered_centers.order_by(listing)

            list_centers = []
            for center in filtered_centers:
                list_centers.append({
                    "pk": center.pk,
                    "full_name": center.full_name,
                    "logo": center.logo.url if center.logo else None,
                    "absolute_url": center.get_absolute_url,
                    "partial_address": center.partial_address
                })

            data = {
                'message': 'success',
                "centers": list_centers,
            }

            return JsonResponse(data)
        
        except Exception as e:
            logger.exception("Error in rendering filtered csc center search view: %s", e)
            return JsonResponse({"error": "Error in rendering filtered csc center search view."})


@method_decorator(never_cache, name="dispatch")
class NearMeCscCenterView(BaseHomeView, View):
    model = CscCenter
    template_name = 'home/list.html'
    redirect_url = reverse_lazy('home:view')

    def get(self, request, *args, **kwargs):
        try:
            latitude = self.kwargs['latitude']
            longitude = self.kwargs['longitude']

            context = self.get_context_data(**kwargs)


            if latitude and longitude:            
                api_key = '1b4ea0d7dc5f4cffb9dbd971a896a71c'

                url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}'

                response = requests.get(url)
                data = response.json()

                if data['results']:
                    county = data['results'][0]['components']['county']
                    
                    context.update({
                        'location': county,
                        'states': State.objects.all()
                    })

                    if county:
                        centers = CscCenter.objects.filter(block__block = county, is_active = True)
                        context['centers'] = centers
                        return render(request, self.template_name, context)
                    
        except Exception as e:
            logger.exception("Error in getting location data: %s", e)
            messages.warning(request, "Failed to load your location data.")
            return redirect(self.redirect_url)  


class CscCenterDetailView(BaseHomeView, DetailView):
    model = CscCenter
    template_name = 'home/detail.html'
    context_object_name = 'center'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['center'] = self.get_object()
        except Exception as e:
            logger.exception("Error in fetching context data in csc center detail view")
        return context


class KeywordsBasedCscCentersView(BaseHomeView, ListView):
    model = CscCenter
    template_name = 'home/list.html'
    context_object_name = 'centers'
    queryset = CscCenter.objects.all()
    ordering = ["name"]

    def get_queryset(self):
        try:
            slug = self.kwargs.get('slug')
            if slug:
                csc_centers = self.queryset.filter(keywords__slug = slug).order_by(*self.ordering)
                return csc_centers
        except Exception as e:
            logger.exception(f"Error in fetching csc centers based on keywords slug: {e}")

        return self.model.objects.none()

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["centers"] = self.get_queryset()
        except Exception as e:
            logger.exception(f"Error in fetching context data in keywords based csc centers view: {e}")
        return context
    

class ServiceRequestView(BaseHomeView, CreateView):
    model = ServiceEnquiry
    fields = ('csc_center', 'applicant_name', 'applicant_email', 'applicant_phone', 'service', 'message')
    redirect_url = reverse_lazy('home:view')

    def get_success_url(self):
        try:
            return reverse_lazy('home:csc_center', kwargs={'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in getting success url in service request view")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            applicant_name = request.POST.get('applicant_name')
            applicant_email = request.POST.get('applicant_email')
            applicant_phone = request.POST.get('applicant_phone')
            service = request.POST.get('service')
            message = request.POST.get('message')
            try:
                service = get_object_or_404(Service, slug = service)
            except Http404:
                messages.warning(request, "Invalid service selected.")
                return redirect(self.get_success_url())
            try:
                csc_center = get_object_or_404(CscCenter, slug = kwargs['slug'])
            except Http404:
                messages.warning(request, "Invalid center selected.")
                return redirect(self.get_success_url())
            
            ServiceEnquiry.objects.create(
                applicant_name = applicant_name,
                applicant_email = applicant_email,
                applicant_phone = applicant_phone,
                service = service,
                csc_center = csc_center,
                message = message
            )
            messages.success(request, "Request submitted")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception("Error in creating service request in service request view: %s", e)
            messages.error(request, "Error in submitting request")
            return redirect(self.redirect_url)


class ProductRequestView(BaseHomeView, CreateView):
    model = ProductEnquiry
    fields = ('csc_center', 'applicant_name', 'applicant_email', 'applicant_phone', 'product', 'message')
    redirect_url = reverse_lazy('home:view')

    def get_success_url(self):
        try:
            return reverse_lazy('home:csc_center', kwargs={'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in getting success url in product request view")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            applicant_name = request.POST.get('applicant_name')
            applicant_email = request.POST.get('applicant_email')
            applicant_phone = request.POST.get('applicant_phone')
            product = request.POST.get('product')
            message = request.POST.get('message')
            try:
                product = get_object_or_404(Product, slug = product)
            except Http404:
                messages.warning(request, "Invalid product selected.")
                return redirect(self.get_success_url())
            try:
                csc_center = get_object_or_404(CscCenter, slug = kwargs['slug'])
            except Http404:
                messages.warning(request, "Invalid center selected.")
                return redirect(self.get_success_url())
            
            ProductEnquiry.objects.create(
                applicant_name = applicant_name,
                applicant_email = applicant_email,
                applicant_phone = applicant_phone,
                product = product,
                csc_center = csc_center,
                message = message
            )
            messages.success(request, "Request submitted")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception("Error in creating product request in product request view: %s", e)
            messages.error(request, "Error in submitting request")
            return redirect(self.redirect_url)
    

class PrivacyPolicyView(BaseView, TemplateView):
    template_name = "custom/privacy_policy.html"


class TermAndConditionView(BaseView, TemplateView):
    template_name = "custom/terms_and_conditions.html"


class ShippingAndDeliveryPolicyView(BaseView, TemplateView):
    template_name = "custom/shipping_and_delivery_policy.html"
    

class CancellationAndRefundPolicyView(BaseView, TemplateView):
    template_name = "custom/cancellation_and_refund_policy.html"