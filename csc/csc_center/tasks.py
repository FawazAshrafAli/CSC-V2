from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from payment.models import Payment
from django.conf import settings
from celery.utils.log import get_task_logger

from .models import CscCenter

logger = get_task_logger(__name__)

def send_expired_notification_mail(center):
    subject = 'Your  Csc Center Account is Expired'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [center.email]

    html_content = render_to_string('email_templates/csc_expired.html', {
        'owner_name': center.owner,
        'expiration_date': timezone.now().date(),
        'support_email': from_email
    })

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    
    email.send()


@shared_task
def check_validty():
    try:
        for csc_center in CscCenter.objects.filter(is_active = True):
            payment_count = Payment.objects.filter(csc_center = csc_center, payment = "Completed").count()

            days_elapsed = (timezone.now().date() - csc_center.created.date()).days
            years_elapsed = days_elapsed / 365

            if years_elapsed > payment_count:
                csc_center.is_active = False
                csc_center.save()
                send_expired_notification_mail(csc_center)
    except Exception as e:
        logger.error(f"Error checking validity: {e}")
        