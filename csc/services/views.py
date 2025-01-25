from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
import logging
import sys

from .models import Service
from csc_admin.models import ServiceEnquiry
from base.views import BaseView

logger = logging.getLogger(__name__)
class BaseServiceView(BaseView):
    model = Service
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['service_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of base service view: {e}")

        return context

@method_decorator(never_cache, name="dispatch")
class ListServiceView(BaseServiceView, ListView):
    queryset = Service.objects.all()
    template_name = 'services/list.html'
    context_object_name = "services"


@method_decorator(never_cache, name="dispatch")
class DetailServiceView(BaseServiceView, DetailView):
    template_name = 'services/detail.html'
    context_object_name = "current_service"
    slug_url_kwarg = 'slug'


class CreateServiceEnquiryView(DetailServiceView, CreateView):
    success_url = redirect_url = reverse_lazy('services:services')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('services:service', kwargs={'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url of create service enquiry view: {e}")
            return redirect(self.success_url)
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of create service enquiry view: {e}")
            return redirect(self.redirect_url)
    
    def post(self, request, *args, **kwargs):
        try:
            service = self.get_object()
            applicant_name = request.POST.get("name", "").strip()
            applicant_email = request.POST.get("email", "").strip()
            applicant_phone = request.POST.get("phone", "").strip()
            location = request.POST.get("location", "").strip()
            message = request.POST.get("message", "").strip()

            required_fields = {
                "Name": applicant_name,
                "Email": applicant_email,
                "Phone": applicant_phone,
                "location": location,
                "message": message
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.warning(request, f"{field_name} is required")
                    return redirect(self.get_redirect_url())

            enquiry_obj = ServiceEnquiry.objects.create(
                applicant_name=applicant_name, applicant_email=applicant_email,
                applicant_phone=applicant_phone, location=location, message=message,
                service = service
                )
            print(enquiry_obj)
            messages.success(request, "Service Enquiry submitted successfully")
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.exception(f"Error in creating service enquiry: {e}")
            messages.error(request, "Failed to submit service enquiry")
            return redirect(self.get_redirect_url())


def remove_duplicate_services():
    try:
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        sys.stdout.write("\nRemoving duplicate services. . .\n")

        services = Service.objects.all()
        service_slugs = [service.slug for service in services]

        for service_slug in service_slugs:
            services_with_current_slug = Service.objects.filter(slug = service_slug)
            current_service_count = services_with_current_slug.count()
            if current_service_count > 1:

                service_ids = [service.id for service in services_with_current_slug][1:]

                deleting_services = Service.objects.filter(id__in = service_ids)
                deleting_services.delete()

                sys.stdout.write(f"{GREEN}\nRemoved duplicate service with slug: {service_slug}\n{RESET}")

        sys.stdout.write(f"{GREEN}\nCompleted! Removed duplicate services.\n{RESET}")
    
    except Exception as e:
        logger.exception(f"Error in removing duplicate services: {e}")
        sys.stdout.write(f"{RED}\nAn unexpected error occured.\n{RESET}")

    


