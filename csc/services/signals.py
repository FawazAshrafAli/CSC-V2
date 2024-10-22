from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Service
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_initial_services(sender, **kwargs):
    try:
        services = [
            'Aadhaar Enrollment', 'Aadhaar Updation', 'Agriculture Tele Consultation', 'Banking & Money Transfer', 'Banking and Money Transfer',
            'BAR CODE', 'BIS Registration', 'Digital Signature', 'DRIVING LICENCE', 'Driving Licence Related Services',
            'Driving License', 'eDistrict Services', 'Educational Registrations', 'FSSAI (Foscos) Registrations', 'Government Job Registrations',
            'Government Registration', 'Govt Job Applications', 'GST Services', 'HealthCare Services', 'INCOME TAX'
            ]
        if sender.name == "services":
            for service in services:
                if Service.objects.count() < 20:
                    if not Service.objects.filter(name=service).exists():
                        Service.objects.create(name=service)
                else:
                    break
    except Exception as e:
        logger.exception(f"Error creating initial services: {e}")
