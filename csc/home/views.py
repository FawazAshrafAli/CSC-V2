import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404
from django.views.generic import TemplateView, View, DetailView, ListView, CreateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib import messages
from urllib.parse import quote
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
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
        # context = {}
        context = super().get_context_data(**kwargs)

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
    

class SearchCscCenterView(BaseHomeView, ListView):
    model = CscCenter
    template_name = 'home/list.html'
    paginate_by = 9
    context_object_name = "centers"

    def encode_parameter(self, param):
        if param:
            return quote(param)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            pincode = self.request.GET.get('pincode')
            state_name = self.request.GET.get('state')
            district_name = self.request.GET.get('district')
            block_name = self.request.GET.get('block')
            listing = self.request.GET.get('listing', 'name')
            services = self.request.GET.getlist('service', None)

            context["service_list"] = services

            context['listing'] = listing

            if pincode:
                context['pincode'] = pincode

            state_obj, district_obj, block_obj = None, None, None

            if state_name:
                state_obj = get_object_or_404(State, state=state_name)

            if district_name:
                district_obj = get_object_or_404(District, district=district_name)

            if block_name:
                block_obj = get_object_or_404(Block, block=block_name)

            location = block_obj or district_obj or state_obj

            context.update({
                'state_obj': state_obj,
                'district_obj': district_obj,
                'block_obj': block_obj,
                'meta_state': self.encode_parameter(state_obj.state) if state_obj else None,
                'meta_district': self.encode_parameter(district_obj.district) if district_obj else None,
                'meta_block': self.encode_parameter(block_obj.block) if block_obj else None,
                'location': location,
                'districts': District.objects.filter(state=state_obj) if state_obj else None,
                'blocks': Block.objects.filter(state=state_obj, district=district_obj) if state_obj and district_obj else None,
            })
        except Exception as e:
            logger.exception(f"Error in fetching context data of search csc center view: {e}")

        return context

    
    def get_queryset(self):
        try:
            pincode = self.request.GET.get('pincode')
            state_name = self.request.GET.get('state')
            district_name = self.request.GET.get('district')
            block_name = self.request.GET.get('block')
            listing = self.request.GET.get('listing', 'name')
            services = self.request.GET.getlist('service', None)        

            service_list = []

            if services:
                for service in services:
                    try:
                        service_obj = get_object_or_404(Service, slug = service)            
                        service_list.append(service_obj.id)
                    except Http404:
                        continue
            
            filters = {'is_active': True}

            if pincode:
                centers = CscCenter.objects.filter(zipcode=pincode, **filters)

                if services:
                    centers = centers.filter(services__in=service_list).annotate(matched_services=Count('services')).filter(matched_services=len(service_list))

                if centers.exists() or not (state_name or district_name or block_name):
                    return centers.order_by(listing)

            if state_name:
                state = get_object_or_404(State, state=state_name)
                filters['state'] = state

            if district_name:
                district = get_object_or_404(District, district=district_name)
                filters['district'] = district

            if block_name:
                block = get_object_or_404(Block, block=block_name)
                filters['block'] = block

            centers = CscCenter.objects.filter(**filters).order_by(listing)

            if services:
                centers = centers.filter(services__in=service_list).annotate(matched_services=Count('services')).filter(matched_services=len(service_list))

            return centers
        
        except Exception as e:
            logger.exception(f"Error in fetching queryset of search csc center view: {e}")
            messages.error(self.request, "Server Error! Please try again later.")
            return None

@method_decorator(never_cache, name="dispatch")
class NearMeCscCenterView(BaseHomeView, ListView):
    model = CscCenter
    template_name = 'home/list.html'
    paginate_by = 9
    context_object_name = "centers"    
    redirect_url = reverse_lazy('home:view')

    def get_county(self):
        latitude = self.kwargs['latitude']
        longitude = self.kwargs['longitude']

        if latitude and longitude:            
            api_key = 'ed920c06eb494333b0bb90f234ad6553'

            url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}'

            response = requests.get(url)
            print(response)
            data = response.json()

            if data['results']:
                county = data['results'][0]['components']['county']


                return county
            
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            services = self.request.GET.getlist('service', None)

            context["service_list"] = services

            county = self.get_county()

            if county:
                context.update({
                    'location': county,
                    'states': State.objects.all(),
                    'latitude': self.kwargs['latitude'],
                    'longitude': self.kwargs['longitude']
                })
        except Exception as e:
            logger.exception(f"Error in fetching context data of near me csc center view: {e}")

        return context
    
    def get_queryset(self):
        try:
            county = self.get_county()

            services = self.request.GET.getlist('service', None)

            service_list = []

            if services:
                for service in services:
                    try:
                        service_obj = get_object_or_404(Service, slug = service)            
                        service_list.append(service_obj.id)
                    except Http404:
                        continue
            
            if county:
                centers = CscCenter.objects.filter(block__block = county, is_active = True)  

                if services:
                    centers = centers.filter(services__in=service_list).annotate(matched_services=Count('services')).filter(matched_services=len(service_list))

                return centers
        except Exception as e:
            logger.exception(f"Error in fetching queryset of near me csc center view: {e}")
            messages.error(self.request, "Server Error! Please try again later.")
        
        return None

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
