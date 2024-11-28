from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from payment.models import Payment
from django.conf import settings
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from math import ceil

from .models import CscCenter

logger = get_task_logger(__name__)

@shared_task
def send_expired_notification_mail(center):
    email, owner, center_slug = center

    subject = 'Your  Csc Center Account is Expired'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    html_content = render_to_string('email_templates/csc_expired.html', {
        'owner_name': owner,
        'expiration_date': timezone.now().date(),
        'support_email': from_email,
        'renew_link': f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/payment/{center_slug}"                
    })

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    
    email.send()


@shared_task
def check_validty():
    try:
        current_day = timezone.now().date()

        for csc_center in CscCenter.objects.filter(is_active = True):
            payment_count = Payment.objects.filter(csc_center = csc_center, payment = "Completed").count()

            days_elapsed = (current_day - csc_center.payment_implemented_date).days
            years_elapsed = ceil(days_elapsed / 365)

            if years_elapsed > payment_count:
                previous_day = current_day - timedelta(days=1)
                csc_center.is_active = False
                csc_center.inactive_date = previous_day
                csc_center.save()                

                center = (csc_center.email, csc_center.owner, csc_center.slug)
                send_expired_notification_mail.delay(center)
        logger.info("Validity check completed successfully.")
    except Exception as e:
        logger.error(f"Error checking validity: {e}")


@shared_task
def check_validty_for_old_centers():
    try:
        payment_due_date = timezone.datetime(2024, 12, 30, tzinfo=timezone.get_current_timezone()).date()
        current_day = timezone.now().date()

        for csc_center in CscCenter.objects.filter(is_active = True, payment_implemented_date = payment_due_date):
            payment_count = Payment.objects.filter(csc_center = csc_center, payment = "Completed").count()

            days_elapsed = (current_day - csc_center.payment_implemented_date).days
            years_elapsed = ceil(days_elapsed / 365)

            if years_elapsed > payment_count:
                previous_day = current_day - timedelta(days=1)
                csc_center.is_active = False
                csc_center.inactive_date = previous_day
                csc_center.save()

                center = (csc_center.email, csc_center.owner, csc_center.slug)
                send_expired_notification_mail.delay(center)
        logger.info("Task completed successfully for old centers.")
    except Exception as e:
        logger.error(f"Error in check_validity_for_old_centers task function: {e}")
        