from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import CscKeyword, CscCenter
from services.models import Service
from django.db.models import Count


@receiver(post_migrate)
def create_initial_keywords(sender, **kwargs):
    keywords = ["CSC", "Common Service Center", "Online Services", "Digital Seva (CSC)"]
    if sender.name == "csc_center":
        for keyword in keywords:
            if CscKeyword.objects.count() < 4:
                if not CscKeyword.objects.filter(keyword=keyword).exists():
                    CscKeyword.objects.create(keyword=keyword)
            else:
                break


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

        csc_centers_without_services = CscCenter.objects.filter(services=None)
        
        for csc_center in csc_centers_without_services:
            csc_center.services.add(*services_qs)
        
        through_model = CscCenter.services.through
        bulk_entries = [
            through_model(csccenter_id=csc_center.id, service_id=service.id)
            for csc_center in csc_centers_without_services
            for service in services_qs
        ]
        
        through_model.objects.bulk_create(bulk_entries, ignore_conflicts=True)