from django.views.generic import TemplateView
import logging

from services.models import Service
from base.views import BaseView

logger = logging.getLogger(__name__)

class AboutUsView(BaseView, TemplateView):
    template_name = 'about_us/about_us.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['services'] = Service.objects.all()
            context['about_us_page'] = True
            return context
        except Exception as e:
            logger.exception("An error occurred while fetching context data of about us")
            return {}