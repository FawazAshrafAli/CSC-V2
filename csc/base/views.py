from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import View
import logging

from services.models import Service
from csc_center.models import CscCenter

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name="dispatch")
class BaseView(View):
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            services = Service.objects.all()
            context["service_group_1"] = services[:6] if len(services) > 0 else None
            context["service_group_2"] = services[6:12] if len(services) > 6 else None
            context["service_group_3"] = services[12:18] if len(services) > 12 else None
            context['services'] = services

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

            return context
        except Exception:
            logger.exception("Error in fetching base context data")
            return {}
    

