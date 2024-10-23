from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import CscKeyword, CscCenter
from services.models import Service
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_initial_keywords(sender, **kwargs):
    try:
        keywords = ["CSC", "Common Service Center", "Online Services", "Digital Seva (CSC)"]
        if sender.name == "csc_center":
            if CscKeyword.objects.count() < 4:
                for keyword in keywords:                    
                    CscKeyword.objects.get_or_create(keyword=keyword)
                    logger.info(f"Created keyword: {keyword}")

            csc_centers = CscCenter.objects.annotate(keywords_count = Count('keywords')).filter(keywords_count__lt = 4).order_by('name')
            keyword_objects = CscKeyword.objects.all()[:4]
            if csc_centers.exists():
                for csc_center in csc_centers:
                    csc_center.keywords.set(keyword_objects)
                    csc_center.save()
                    logger.info(f"Assigned keywords to CSC Center: {csc_center.name}")
    except Exception as e:
        logger.exception(f"Error creating initial keywords for csc centers: {str(e)}")



@receiver(post_migrate)
def create_initial_services_for_center(sender, **kwargs):
    services = [
            'Aadhaar Enrollment', 'Aadhaar Updation', 'Agriculture Tele Consultation', 'Banking & Money Transfer', 'Banking and Money Transfer',
            'BAR CODE', 'BIS Registration', 'Digital Signature', 'DRIVING LICENCE', 'Driving Licence Related Services',
            'Driving License', 'eDistrict Services', 'Educational Registrations', 'FSSAI (Foscos) Registrations', 'Government Job Registrations',
            'Government Registration', 'Govt Job Applications', 'GST Services', 'HealthCare Services', 'INCOME TAX'
            ]
    if sender.name == "csc_center":
        for service in services:
            if Service.objects.count() < 20:
                if not Service.objects.filter(name=service).exists():
                    Service.objects.create(name=service)
            else:
                break

        services_qs = Service.objects.all()[:20]

        csc_centers_without_services = CscCenter.objects.annotate(services_count = Count('services')).filter(services_count__lt = 20)
        
        for csc_center in csc_centers_without_services:
            csc_center.services.add(*services_qs)
        
        through_model = CscCenter.services.through
        bulk_entries = [
            through_model(csccenter_id=csc_center.id, service_id=service.id)
            for csc_center in csc_centers_without_services
            for service in services_qs
        ]
        
        through_model.objects.bulk_create(bulk_entries, ignore_conflicts=True)