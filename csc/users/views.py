from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, logout
from datetime import datetime
from django.db.models import Q
import logging
import re

from payment.models import Payment
from authentication.models import User
from posters.models import Poster, PosterFooter
from products.models import Product, ProductEnquiry
from services.models import Service, ServiceEnquiry
from csc_center.models import (CscCenter, SocialMediaLink, State,
                                District, Block, CscKeyword,
                                CscNameType, Banner)

logger = logging.getLogger(__name__)

def check_payment(center, data):
    try:
        if not center.is_active:
            payment_url = reverse_lazy("payment:payment", kwargs = {'slug' : center.slug})
            print(payment_url)
            if center.live_days < 15:
                data['light_warning_message'] = f"You are on the 15 days trail period. Please make the payment in the next {15 - center.live_days} days to avoid suspension of your account. &nbsp;<span style='display: inline-block;'>Click <a href='{payment_url}' style='color: blue; text-decoration: underline;'>Pay Now</a> for payment</span>"
            else:
                data['hard_warning_message'] = f"Your account is in danger. Please make the payment as soon as possible to avoid suspension of your account. <span style='display: inline-block;'>Click <a href='{payment_url}' style='color: blue; text-decoration: underline;'>Pay Now</a> for payment</span>"
            
        return data
    except Exception as e:
        logger.error(f"Error in check_payment: {e}")
        return data

def check_payment_response(request):
    center_slug = request.GET.get('center_slug')
    data = {}

    try:
        center = get_object_or_404(CscCenter, slug=center_slug)
        data = check_payment(center, data)
    
    except Http404:
        data['error'] = 'CSC center not found'
    
    return data


class BaseUserView(LoginRequiredMixin, View):
    login_url = reverse_lazy('authentication:login')

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                return redirect(self.login_url)
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.exception("Error in base admin view: %s", e)
            return redirect(self.login_url)

    def get_context_data(self, **kwargs):
        # context = {}    
        context = super().get_context_data(**kwargs)
        try:            
            centers = CscCenter.objects.filter(email = self.request.user.email)
            context["csc_center"] = CscCenter.objects.filter(email = self.request.user.email).first()
            context['centers'] = centers
            context['center'] = centers.first() if centers.first().is_active else None
            context['services_left'] = Service.objects.all()
            context['user_csc_centers'] = centers

        except Exception as e:
            print(e)

        return context


class CheckPaymentView(BaseUserView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            data = check_payment_response(request)

            return JsonResponse(data)
        return super().get(request, *args, *kwargs)


class HomeView(BaseUserView, TemplateView):
    template_name = 'user_home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        center_slug = self.request.GET.get('center_slug')     
        if center_slug:
            try:
                csc_center = get_object_or_404(CscCenter, slug = center_slug)
                context["csc_center"] = csc_center
            except Http404:
                pass
        
        context["service_enquiries"] = ServiceEnquiry.objects.filter(csc_center = context["csc_center"]).order_by('-created')
        context["product_enquiries"] = ProductEnquiry.objects.filter(csc_center = context["csc_center"]).order_by('-created')
        context["home_page"] = True
        return context

class GetCenterDataView(BaseUserView, View):
    def get(self, request, *args, **kwargs):
        center_slug = request.GET.get('center_slug')

        data = {}

        try:
            center = get_object_or_404(CscCenter, slug = center_slug)

            data = check_payment(center, data)

            data['services_count'] = center.services.all().count()
            data['products_count'] = center.products.all().count()            

            service_enquiries = ServiceEnquiry.objects.filter(csc_center = center)
            product_enquiries = ProductEnquiry.objects.filter(csc_center = center)

            data["service_enquiries_count"] = service_enquiries.count()
            data["product_enquiries_count"] = product_enquiries.count()

            service_enquiry_list = []
            for enquiry in service_enquiries:
                service_enquiry_list.append({
                    "applicant_name": enquiry.applicant_name,
                    "service": enquiry.service.first_name,
                    "slug": enquiry.slug,                    
                })
                
            data['service_enquiries'] = service_enquiry_list

            product_enquiry_list = []
            for enquiry in product_enquiries:
                product_enquiry_list.append({
                    "applicant_name": enquiry.applicant_name,
                    "product": enquiry.product.name,
                    "slug": enquiry.slug
                })

            data['product_enquiries'] = product_enquiry_list

        except Http404:
            data = {"error": "Selected center is not yet active."}
                
        return JsonResponse(data)


# Service
class BaseServiceView(BaseUserView, View):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context


class ServiceEnquiryListView(BaseServiceView, ListView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_list.html'
    context_object_name = 'enquiries'

    def get_queryset(self):
        center = CscCenter.objects.filter(email = self.request.user.email, is_active = True).first()
        enquiries = self.model.objects.filter(csc_center = center).order_by('-created') if center else None
        return enquiries
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiries'] = self.get_queryset()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            data = {}
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)

                data = check_payment(center, data)

                enquiries = self.model.objects.filter(csc_center = center)
                enquiries_list = []
                for count, enquiry in enumerate(enquiries):
                    enquiries_list.append({                        
                        'applicant_name': enquiry.applicant_name, 
                        'applicant_email': enquiry.applicant_email, 
                        'applicant_phone': enquiry.applicant_phone,
                        'message': enquiry.message, 
                        'service': enquiry.service.first_name,
                        'created': datetime.strftime(enquiry.created, "%b %d, %Y %I:%M %p"),
                        'slug': enquiry.slug, 'count': count+1})
                    
                data['enquiries'] = enquiries_list
            except Http404:
                data['error'] = 'Not an active csc center.'
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


class DeleteServiceEnquiryView(BaseServiceView, View):
    model = ServiceEnquiry
    success_url = reverse_lazy('users:service_enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(ServiceEnquiry, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Enquiry deleted successfully')
        return redirect(self.success_url)


# Products
class ProductBaseView(BaseUserView):
    model = CscCenter
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_page'] = True
        context['products'] = Product.objects.all()
        return context  
    

class ProductEnquiryListView(ProductBaseView, ListView):
    model = ProductEnquiry
    template_name = 'user_products/enquiry_list.html'
    context_object_name = 'enquiries'

    def get_queryset(self):
        center = CscCenter.objects.filter(email = self.request.user.email, is_active = True).first()
        enquiries = self.model.objects.filter(csc_center = center).order_by('-created') if center else None
        return enquiries
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')

            data = {}
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)

                data = check_payment(center, data)

                enquiries = self.model.objects.filter(csc_center = center)
                enquiries_list = []
                for count, enquiry in enumerate(enquiries):
                    enquiries_list.append({
                        'applicant_name': enquiry.applicant_name, 
                        'applicant_email': enquiry.applicant_email, 
                        'applicant_phone': enquiry.applicant_phone, 
                        'message': enquiry.message,
                        'product': enquiry.product.name, 
                        'slug': enquiry.slug,
                        'created': datetime.strftime(enquiry.created, "%b %d, %Y %I:%M %p"),
                        'count': count+1})
                    
                data['enquiries'] = enquiries_list
            except Http404:
                data['error'] = 'Not an active csc center.'
                
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


class DeleteProductEnquiryView(ProductBaseView, View):
    model = ProductEnquiry
    success_url = reverse_lazy('users:product_enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(ProductEnquiry, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Enquiry deleted successfully')
        return redirect(self.success_url)

# CSC Centers2
class CscCenterBaseView(BaseUserView):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['center_page'] = True        
        return context
    

class GetCurrentCscCenterView(CscCenterBaseView, View):
    def get(self, request, *args, **kwargs):
        center_slug = request.GET.get('center_slug')
        data = {}

        try:
            center = get_object_or_404(CscCenter, slug = center_slug)
            data.update({
                'current_center_name': center.name
                })
            
        except Http404:
            data = {"error": "Invalid csc center"}

        return JsonResponse(data)
            

class CscCenterListView(CscCenterBaseView, ListView):
    template_name = 'user_csc_center/list.html'
    context_object_name = 'centers'

    def get_queryset(self):
        return CscCenter.objects.filter(email = self.request.user.email)
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            data = check_payment_response(request)

            return JsonResponse(data)

        return super().get(request, *args, **kwargs)
    

class DetailCscCenterView(CscCenterBaseView, DetailView):
    template_name = "user_csc_center/detail.html"
    context_object_name = 'center_obj'
    slug_url_kwarg = 'slug'

    def get_object(self):
        try:
            return get_object_or_404(CscCenter, slug = self.kwargs['slug'])
        except Http404:
            messages.error(self.request, 'Invalid CSC center')
            return redirect(reverse_lazy('users:csc_centers'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['center_obj'] = self.get_object()
        return context
    

class AddCscCenterView(CscCenterBaseView, CreateView):
    template_name = 'user_csc_center/create.html'
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy("users:add_csc")
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['services'] = Service.objects.all()
        context['states'] = State.objects.all()
        context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]

        time_data = []
        for i in range(1, 25):
            if i < 13:
                str_time = f"{i} AM"
            else:
                str_time = f"{i-12} PM"            
            time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
            time_data.append({"str_time": str_time, "time": time})
            context['time_data'] = time_data

        return context

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            type = request.POST.get('type')
            csc_reg_no = request.POST.get('csc_reg_no')
            keywords = request.POST.getlist('keywords')

            state = request.POST.get('state')
            district = request.POST.get('district')
            block = request.POST.get('block')
            location = request.POST.get('location')
            zipcode = request.POST.get('zipcode')
            landmark_or_building_name = request.POST.get('landmark_or_building_name')
            street = request.POST.get('address')
            logo = request.FILES.get('logo')
            banners = request.FILES.getlist('banner')
            description = request.POST.get('description')
            owner = request.POST.get('owner')
            email = request.POST.get('email')
            website = request.POST.get('website')
            contact_number = request.POST.get('contact_number')
            mobile_number = request.POST.get('mobile_number')
            whatsapp_number = request.POST.get('whatsapp_number')
            services = request.POST.getlist('services')
            products = request.POST.getlist('products')

            show_opening_hours = request.POST.get('show_opening_hours')
            if show_opening_hours: 
                show_opening_hours = show_opening_hours.strip()

            mon_opening_time = request.POST.get('mon_opening_time')
            tue_opening_time = request.POST.get('tue_opening_time')
            wed_opening_time = request.POST.get('wed_opening_time')
            thu_opening_time = request.POST.get('thu_opening_time')
            fri_opening_time = request.POST.get('fri_opening_time')
            sat_opening_time = request.POST.get('sat_opening_time')
            sun_opening_time = request.POST.get('sun_opening_time')

            mon_closing_time = request.POST.get('mon_closing_time')
            tue_closing_time = request.POST.get('tue_closing_time')
            wed_closing_time = request.POST.get('wed_closing_time')
            thu_closing_time = request.POST.get('thu_closing_time')
            fri_closing_time = request.POST.get('fri_closing_time')
            sat_closing_time = request.POST.get('sat_closing_time')
            sun_closing_time = request.POST.get('sun_closing_time')

            mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
            tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
            wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
            thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
            fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
            sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
            sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
    
            mon_closing_time =         mon_closing_time.strip() if mon_closing_time else None
            tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
            wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
            thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
            fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
            sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
            sun_closing_time = sun_closing_time.strip() if sun_closing_time else None

            show_social_media_links = request.POST.get('show_social_media_links')
            if show_social_media_links:
                show_social_media_links = show_social_media_links.strip()

            social_medias = request.POST.getlist('social_medias', None)
            social_links = request.POST.getlist('social_links', None)

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                type = get_object_or_404(CscNameType, slug = type.strip())
            except Http404:
                messages.error(request, 'Invalid CSC Name Type')
                return redirect(self.redirect_url)

            try:
                state = get_object_or_404(State, state = state.strip())
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.redirect_url)

            try:
                district = get_object_or_404(District, district = district.strip())
            except Http404:
                messages.error(request, 'Invalid District')
                return redirect(self.redirect_url)
            
            try:
                block = get_object_or_404(Block, block = block.strip())
            except Http404:
                messages.error(request, 'Invalid Block')
                return redirect(self.redirect_url)
            
            self.object = CscCenter.objects.create(
                name = name.strip() if name else None, type = type, csc_reg_no = csc_reg_no.strip() if csc_reg_no else None, 
                state = state, district = district, block = block, location = location.strip() if location else None,
                zipcode = zipcode.strip() if zipcode else None, landmark_or_building_name = landmark_or_building_name.strip() if landmark_or_building_name else None,
                street = street.strip() if street else None, logo = logo, description = description.strip() if description else None, contact_number = contact_number.strip() if contact_number else None,
                owner = owner.strip() if owner else None, email = email.strip() if email else None, website = website.strip() if website else None, 
                mobile_number = mobile_number.strip() if mobile_number else None, whatsapp_number = whatsapp_number.strip() if whatsapp_number else None,
                mon_opening_time = mon_opening_time, tue_opening_time = tue_opening_time, 
                wed_opening_time = wed_opening_time, thu_opening_time = thu_opening_time, 
                fri_opening_time = fri_opening_time, sat_opening_time = sat_opening_time, 
                sun_opening_time = sun_opening_time, mon_closing_time = mon_closing_time, 
                tue_closing_time = tue_closing_time, wed_closing_time = wed_closing_time, 
                thu_closing_time = thu_closing_time, fri_closing_time = fri_closing_time, 
                sat_closing_time = sat_closing_time, sun_closing_time = sun_closing_time, 
                latitude = latitude.strip() if latitude else None, longitude = longitude.strip() if longitude else None
            )
            
            # after creation of object
            self.object.keywords.set(keywords)
            self.object.services.set(services)
            self.object.products.set(products)
            self.object.save()

            current_keywords = self.object.keywords.all()
            keyword_count = current_keywords.count()
            keywords_needed = 4 - keyword_count

            if keywords_needed > 0:
                additional_keywords = CscKeyword.objects.exclude(id__in=current_keywords.values_list('id', flat=True))
                keywords_to_add = additional_keywords[:keywords_needed]
                self.object.keywords.add(*keywords_to_add)
                self.object.save()

            current_services = self.object.services.all()
            service_count = current_services.count()
            services_needed = 20 - service_count

            if services_needed > 0:
                additional_services = Service.objects.exclude(id__in=current_services.values_list('id', flat=True))

                services_to_add = additional_services[:services_needed]
                
                self.object.services.add(*services_to_add)

                self.object.save()

            if banners:
                for banner in banners:
                    banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                    self.object.banners.add(banner_obj)
                self.object.save()

            if social_medias and social_links:
                social_media_length = len(social_medias)
                if social_media_length > 0:
                    social_media_list = []
                    for i in range(social_media_length):
                        if social_medias[i] and social_links[i]:
                            social_media_link, created = SocialMediaLink.objects.get_or_create(
                                csc_center_id = self.object,
                                social_media_name = social_medias[i].strip(),
                                social_media_link = social_links[i].strip()
                            )
                            social_media_list.append(social_media_link)
                    
                        self.object.social_media_links.set(social_media_list)
                        self.object.save()

            messages.success(request, "Added CSC center")

            if not User.objects.filter(email = email).exists():
                logout(request)        
                return redirect(reverse('authentication:user_registration', kwargs={'email': self.object.email}))
            elif request.user.email and request.user.email == email:
                return redirect(reverse_lazy("users:home"))
            else:
                logout(request)
            
            return redirect(self.success_url)
            
        except Exception as e:
            msg = "Failed to add csc center"
            logger.exception(f"{msg}: {e}")
            messages.error(request, msg)
            return redirect(self.redirect_url)
    

@method_decorator(never_cache, name="dispatch")
class UpdateCscCenterView(CscCenterBaseView, UpdateView):
    model = CscCenter
    template_name = 'user_csc_center/update.html'
    context_object_name = 'center_obj'
    fields = "__all__"
    slug_url_kwarg = 'slug'
    success_url = redirect_url = reverse_lazy("users:csc_centers")

    def get_object(self, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs['slug'])
            return self.object
        except Http404:
            messages.error(self.request, "Invalid CSC center")
            return redirect(self.redirect_url)
        
    def get_success_url(self):
        try:
            return reverse_lazy('users:csc_center', kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in fetching success url of update csc center view: {e}")            
            return redirect(self.success_url)
    
    def get_redirect_url(self):
        try:
            return reverse_lazy('users:update_csc', kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception("Error in fetching redirect url of update csc center view: {e}")
            return redirect(self.redirect_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['states'] = State.objects.all()
        context['services'] = Service.objects.all()
        context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]
        self.object = self.get_object()
        context['center_obj'] = self.object
        context['selected_districts'] = District.objects.filter(state = self.object.state)
        context['selected_blocks'] = Block.objects.filter(district = self.object.district)

        time_data = []
        for i in range(1, 25):
            if i < 13:
                str_time = f"{i} AM"
            else:
                str_time = f"{i-12} PM"            
            time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
            time_data.append({"str_time": str_time, "time": time})
            context['time_data'] = time_data

        return context
    
    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            type = request.POST.get('type')
            csc_reg_no = request.POST.get('csc_reg_no')
            keywords = request.POST.getlist('keywords')

            state = request.POST.get('state')
            district = request.POST.get('district')
            block = request.POST.get('block')
            location = request.POST.get('location')
            zipcode = request.POST.get('zipcode')
            landmark_or_building_name = request.POST.get('landmark_or_building_name')
            street = request.POST.get('address')
            logo = request.FILES.get('logo')
            banners = request.FILES.getlist('banner')
            description = request.POST.get('description')
            owner = request.POST.get('owner')
            website = request.POST.get('website')
            contact_number = request.POST.get('contact_number')
            mobile_number = request.POST.get('mobile_number')
            whatsapp_number = request.POST.get('whatsapp_number')        
            services = request.POST.getlist('services')
            products = request.POST.getlist('products')

            show_opening_hours = request.POST.get('show_opening_hours')

            if show_opening_hours:
                show_opening_hours = show_opening_hours.strip()

            mon_opening_time = request.POST.get('mon_opening_time')
            tue_opening_time = request.POST.get('tue_opening_time')
            wed_opening_time = request.POST.get('wed_opening_time')
            thu_opening_time = request.POST.get('thu_opening_time')
            fri_opening_time = request.POST.get('fri_opening_time')
            sat_opening_time = request.POST.get('sat_opening_time')
            sun_opening_time = request.POST.get('sun_opening_time')

            mon_closing_time = request.POST.get('mon_closing_time')
            tue_closing_time = request.POST.get('tue_closing_time')
            wed_closing_time = request.POST.get('wed_closing_time')
            thu_closing_time = request.POST.get('thu_closing_time')
            fri_closing_time = request.POST.get('fri_closing_time')
            sat_closing_time = request.POST.get('sat_closing_time')
            sun_closing_time = request.POST.get('sun_closing_time')

            mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
            tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
            wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
            thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
            fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
            sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
            sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
            
            mon_closing_time = mon_closing_time.strip() if mon_closing_time else None
            tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
            wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
            thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
            fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
            sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
            sun_closing_time = sun_closing_time.strip() if sun_closing_time else None

            show_social_media_links = request.POST.get('show_social_media_links')

            show_social_media_links = show_social_media_links.strip() if show_social_media_links else None

            if show_social_media_links:
                show_social_media_links = show_social_media_links.strip()

            social_medias = request.POST.getlist('social_medias')
            social_links = request.POST.getlist('social_links')

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                type = get_object_or_404(CscNameType, slug = type.strip())
            except Http404:
                messages.error(request, 'Invalid CSC Name Type')
                return redirect(self.get_redirect_url())

            try:
                state = get_object_or_404(State, state = state.strip())
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.get_redirect_url())

            try:
                district = get_object_or_404(District, district = district.strip())
            except Http404:
                messages.error(request, 'Invalid District')
                return redirect(self.get_redirect_url())
            
            try:
                block = get_object_or_404(Block, block = block.strip())
            except Http404:
                messages.error(request, 'Invalid Block')
                return redirect(self.get_redirect_url())
            
            self.object = self.get_object()

            if name:
                self.object.name = name.strip()
            if type:
                self.object.type = type
            self.object.csc_reg_no = csc_reg_no.strip() if csc_reg_no else None
            if state:
                self.object.state = state
            if district:
                self.object.district = district
            if block:
                self.object.block = block
            if location:
                self.object.location = location.strip()
            if zipcode:
                self.object.zipcode = zipcode.strip()
            if landmark_or_building_name:
                self.object.landmark_or_building_name = landmark_or_building_name.strip()
            if street:
                self.object.street = street.strip()
                
            if logo:
                self.object.logo = logo

            if banners:
                self.object.banners.clear()
                for banner in banners:
                    banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                    self.object.banners.add(banner_obj)

            if description:
                self.object.description = description.strip()
            if owner:
                self.object.owner = owner.strip()
                            
            self.object.website = website.strip() if website else None
            if contact_number:
                self.object.contact_number = contact_number.strip()
            if mobile_number:
                self.object.mobile_number = mobile_number.strip()
            if whatsapp_number:
                self.object.whatsapp_number = whatsapp_number.strip()

            self.object.show_opening_hours = True if show_opening_hours else False
            self.object.show_social_media_links = True if show_social_media_links else False

            if show_opening_hours:
                self.object.mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
                self.object.tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
                self.object.wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
                self.object.thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
                self.object.fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
                self.object.sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
                self.object.sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
                self.object.mon_closing_time = mon_closing_time.strip() if mon_closing_time else None
                self.object.tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
                self.object.wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
                self.object.thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
                self.object.fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
                self.object.sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
                self.object.sun_closing_time = sun_closing_time.strip() if sun_closing_time else None


            self.object.latitude = latitude.strip() if latitude else None
            self.object.longitude = longitude.strip() if longitude else None
            
            self.object.keywords.set(keywords)
            self.object.services.set(services)
            self.object.products.set(products)
            self.object.save()

            if social_medias and social_links:
                social_media_length = len(social_medias)
                if social_media_length > 0:
                    social_media_list = []
                    for i in range(social_media_length):
                        if social_medias[i] and social_links[i]:
                            social_media_link, created = SocialMediaLink.objects.get_or_create(
                                csc_center_id = self.object,
                                social_media_name = social_medias[i].strip(),
                                social_media_link = social_links[i].strip()
                            )
                            social_media_list.append(social_media_link)
                    
                        self.object.social_media_links.set(social_media_list)
                        self.object.save()
                else:
                    self.object.social_media_links.clear()
                    self.object.save()
            else:
                self.object.social_media_links.clear()
                self.object.save()

            messages.success(request, "Updated CSC Center Details")      
            
            return redirect(self.get_success_url())
        except Exception as e:
            msg = "Error in updating csc center"
            logger.exception(f"{msg}: {e}")
            messages.error(request, msg)
            return redirect(self.redirect_url)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)
    

###################### Posters ################################

class BasePosterView(BaseUserView, View):
    model = Poster
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster_page'] = True
        if CscCenter.objects.filter(email = self.request.user.email).count() > 1:
            context['multi_center_owner'] = True
        return context


class AvailablePosterView(BasePosterView, ListView):
    model = Poster
    queryset = model.objects.all()
    context_object_name = 'posters'
    template_name = "user_posters/available_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.all()
        return context

    def get_queryset(self):
        center = CscCenter.objects.filter(email = self.request.user.email, is_active = True).first()
        if center:
            return self.model.objects.filter(Q(state = center.state) | Q(state__isnull = True))
        return None
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {}
            center_slug = request.GET.get('center_slug')
            service_slug = request.GET.get('service_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)

                data["centerName"] = f"{center.name} {center.type.type}"

                center_street = []
                if center.landmark_or_building_name:
                    center_street.append(center.landmark_or_building_name)
                if center.street:
                    center_street.append(center.street)

                center_street = list(set(center_street))

                data["centerStreet"] = ", ".join(center_street) if center_street else None

                data["centerLocation"] = f"{center.location}, {center.block.block}" if center.location else center.block.block

                contact_numbers = [f"{center.contact_number}", f"{center.mobile_number}", f"{center.whatsapp_number}"]
                
                for i in range(len(contact_numbers)):
                    contact_numbers[i] = re.sub(r"^(\+91-|\+|-|91)", "", contact_numbers[i])

                    if not contact_numbers[i].startswith("0"):
                        contact_numbers[i] = contact_numbers[i][-10:]

                contact_numbers = list(set(contact_numbers))
                if contact_numbers:
                    contact_numbers = " | ".join(contact_numbers[:2]) if len(contact_numbers) > 1 else contact_numbers[0]

                data["centerContacts"] = contact_numbers if contact_numbers else None


                data["centerLogo"] = center.logo.url if center.logo else None


                data["centerQrCode"] = center.qr_code_image.url if center.qr_code_image else None
                
                poster_objs = PosterFooter.objects.filter(csc_center = center)
                
                data["centerFooter"] = poster_objs.first().image.url if poster_objs.exists() else None

                data = check_payment(center, data)

                posters = self.model.objects.filter(Q(state = center.state) | Q(state__isnull = True)) if center else None

                if service_slug:
                    try:
                        service = get_object_or_404(Service, slug = service_slug)
                        posters = posters.filter(service = service) if posters else None
                    except Http404:
                        pass

                if posters:
                    list_posters = []
                    for poster in posters:
                        list_posters.append({"title": poster.title, "slug": poster.slug, "service": poster.service.slug, "poster": poster.poster.url if poster.poster else None})
                    data["posters"] = list_posters
                else:
                    data["posters"] = []
            except Http404:
                data = {'error': 'Not an active csc center'}

            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

    
class BasePosterFooterView(BasePosterView, View):
    model = PosterFooter
    success_url = redirect_url = reverse_lazy("users:add_footer")


class AddPosterFooterView(BasePosterFooterView, CreateView):
    template_name = "user_posters/create_footer.html"
    fields = ["csc_center", "image"]

    def post(self, request, *args, **kwargs):
        try:
            center_slug = request.POST.get("center")
            center = get_object_or_404(CscCenter, slug = center_slug)
            footer = request.FILES.get("footer")

            if not footer:
                messages.error(request, "Error! Please provide a footer image and try again")
                return redirect(self.redirect_url)
            
            self.model.objects.update_or_create(csc_center = center, defaults={"image" : footer})
            messages.success(request, "Success! Added poster footer.")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Error in identifying your csc center.")

        except Exception as e:
            logger.exception(f"Error in post function of add poster footer function: {e}")

        return redirect(self.success_url)


def get_footer(request):
    data = {}
    try:
        center_slug = request.GET.get("center_slug")
        center = get_object_or_404(CscCenter, slug = center_slug)


        try:
            footer = get_object_or_404(PosterFooter, csc_center = center)
            data = {
                "footer": footer.image.url,
                "footer_name": footer.image.name,
                "footer_slug": footer.slug
            }
        except Http404:
            data = {"message": "Footer not found."}
    
        data = check_payment(center, data)
    except Http404:
        data = {"message": "Failed to identify the csc center."}

    except Exception as e:
        logger.exception(f"Error in getting footer: {e}")
        data = {"message": "Error in getting footer"}

    return JsonResponse(data)


class RemoveFooterView(BasePosterFooterView, View):
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Invalid footer.")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Deleted footer image")
            return redirect(self.success_url)
        except Exception as e:
            messages.error("Failed! Footer image deletion failed")
            logger.exception(f"Error in deleting footer image: {e}")
            return redirect(self.redirect_url)
    

class CreatePosterView(BasePosterView, CreateView):
    model = Poster
    template_name = "user_posters/create.html"
    success_url = reverse_lazy('users:available_posters')
    redirect_url = success_url
    fields = ["csc_center", "poster", "title", "service"]

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(self.model, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster'] = self.get_object()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Successfully created custom poster.")
        return response
    
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Created Poster')
        return redirect(self.get_success_url())


class GetQrCodeView(BasePosterView, DetailView):
    model = CscCenter

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        qr_code = self.object.qr_code_image.url
        center = self.object.name

        return JsonResponse({'qr_code': qr_code, 'center': center})    


########## Poster End ##########

########## My Profile Start ##########

class BaseMyProfileView(BaseUserView):
    model = User


class MyProfileView(BaseMyProfileView, TemplateView):
    template_name = 'user_profile/my_profile.html'
    redirect_url = reverse_lazy('authentication:login')

    def get_object(self):
        try:
            return get_object_or_404(self.model, email = self.request.user.email)
        except Http404:
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            data = check_payment_response(request)

            return JsonResponse(data)
        return super().get(request, *args, *kwargs)


class UpdateProfileView(MyProfileView, UpdateView):
    success_url = reverse_lazy('users:my_profile')
    redirect_url = success_url
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            image = request.FILES.get('image')
            name = request.POST.get('name').strip().title()
            phone = request.POST.get('phone').strip()
            email = request.POST.get('email').strip().lower()
            notes = request.POST.get('notes').strip()
            twitter = request.POST.get('twitter').strip().lower()
            facebook = request.POST.get('facebook').strip().lower()
            google = request.POST.get('google').strip().lower()

            required_fields = {
                "Name": name,
                "Phone": phone,
                "Email": email
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"{field_name} is required")
                    return redirect(self.redirect_url)

            name_parts = name.split(' ')

            first_name = name_parts[0] if len(name_parts) > 0 else None
            self.object.first_name = first_name

            if len(name_parts) > 1:
                last_name = " ".join(name_parts[1:])
                self.object.last_name = last_name            

            self.object.notes = notes
            self.object.twitter = twitter
            self.object.facebook = facebook
            self.object.google = google

            
            if  phone.isnumeric():
                self.object.phone = phone
            
            if image:
                self.object.image = image

            self.object.save()

            current_email = self.object.email

            if email != current_email:
                user_csc_centers = CscCenter.objects.filter(email = current_email)
                for csc_center in user_csc_centers:
                    csc_center.email = email
                    csc_center.save()
                self.object.email = email
                self.object.save()

            messages.success(request, "Updated user profile details.")
            return redirect(self.get_success_url())
        except Exception as e:
            logger.exception(f"Error in updating profile view: {e}")
            return redirect(self.redirect_url)
        

class ChangePasswordView(MyProfileView, UpdateView):
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('users:my_profile')

    def get_object(self):
        try:
            return get_object_or_404(User, email = self.request.user.email)
        except Http404:
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            user = authenticate(request, username = request.user.username, password = current_password)

            if user is not None and new_password == confirm_password:
                self.object.set_password(new_password)
                self.object.save()
                messages.success(request, "Password Updated. Please login again with your new password")
                logout(request)
                return redirect(self.get_success_url())
            
            if user is None:
                error_msg = "The current password you entered is incorrect"
            elif new_password != confirm_password:
                error_msg = "New passwords are not matching"
            else:
                error_msg = "Something went wrong."

            messages.error(request, error_msg)
            return redirect(self.redirect_url)
        
        except Exception as e:
            logger.exception(f"Error in change password view: {e}")
            return redirect(self.redirect_url)

# Order History
class OrderHistoryBaseView(BaseUserView):
    model = Payment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_page"] = True
        return context

class OrderHistoryListView(OrderHistoryBaseView, ListView):
    model = Payment
    template_name = "user_order_history/list.html"    
        
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = {}
            try:
                data = check_payment_response(request)
                center_slug = request.GET.get('center_slug')

                payments = self.model.objects.filter(csc_center__slug = center_slug, status = "Completed").order_by("-created")
                print(payments)

                list_payments = []

                for payment in payments:
                    list_payments.append({
                        "center" : payment.csc_center.full_name,
                        "order_id": payment.order_id,
                        "payment_id": payment.payment_id,
                        "amount": payment.amount,
                        "created": datetime.strftime(payment.created, "%d-%b-%Y")
                    })

                data["payments"] = list_payments


            except Exception as e:
                logger.exception(f"Error in fetching order history: {e}")
                data["error"] = f"{e}"

            return JsonResponse(data)

        return super().get(request, *args, **kwargs)



class OrderHistoryDetailView(OrderHistoryBaseView, DetailView):
    model = Payment
    template_name = "user_order_history/detail.html"
    context_object_name = "payment"

    def get_object(self):
        try:
            
            return get_object_or_404(self.model, payment_id = self.kwargs.get('payment_id'))
        except Http404:
            messages.warning(self.request, "Invalid payment object")
            return redirect(reverse_lazy('users:order_histories'))
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()
            context["payment"] = self.object
            service_charge = 50
            context["service_charge"] = service_charge
            context["total"] = self.object.amount + service_charge
        except Exception as e:
            logger.exception(f"Error in fetching context data of order history detail view: {e}")
        return context
