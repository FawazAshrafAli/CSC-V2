from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
import logging

from .models import Enquiry
from base.views import BaseView

logger = logging.getLogger(__name__)
class BaseContactView(BaseView):
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["contact_us_page"] = True
            return context
        except Exception as e:
            logger.exception(f"Error in fetchin base contact context data: {e}")
            return {}
        

class ContactUsView(BaseContactView, TemplateView):
    template_name = "contact_us/contact_us.html"


class SubmitEnquiryView(ContactUsView, CreateView):
    model = Enquiry
    fields = ["name", "email", "phone", "location", "message"]
    success_url = reverse_lazy("contact_us:view")
    redirect_url = success_url

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Enquiry Submitted")
            return response
        except Exception as e:
            logger.exception(f"Error in submitting enquiry for admin: {e}")
            return redirect(self.redirect_url)
    
    def form_invalid(self, form):
        try:
            messages.error(self.request, "Enquiry Submission Failed")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error on field - {field}: {error}")
            return super().form_invalid(form)
        except Exception as e:
            logger.exception(f"Error in submitting enquiry for admin: {e}")
            return redirect(self.redirect_url)
