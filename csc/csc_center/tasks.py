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
    email, owner, center_slug, center_name = center

    subject = 'Your Csc Center Account is Expired'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    html_content = render_to_string('email_templates/csc_expired.html', {
        'owner_name': owner,
        'expiration_date': timezone.now().date(),
        'support_email': from_email,
        'center_name': center_name,
        'renew_link': f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/payment/{center_slug}"                
    })

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    
    email.send()


@shared_task
def send_expiry_warning_mail(center):
    email, owner, center_slug, center_name, expiration_date = center

    subject = 'Csc Center Expiry Warning'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    html_content = render_to_string('email_templates/csc_expiry_warning.html', {
        'owner_name': owner,
        'expiration_date': expiration_date,
        'support_email': from_email,
        'center_name': center_name,
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
            if current_day >= csc_center.next_payment_date:
                csc_center.is_active = False
                csc_center.save()                

                center = (csc_center.email, csc_center.owner, csc_center.slug, csc_center.name)
                send_expired_notification_mail.delay(center)
        logger.info("Validity check completed successfully.")
    except Exception as e:
        logger.error(f"Error checking validity: {e}")

@shared_task
def check_expiring_centers():
    try:
        date_after_30_days = timezone.now().date() + timedelta(days=30)

        for csc_center in CscCenter.objects.filter(is_active = True):          
            if date_after_30_days >= csc_center.next_payment_date:                    
                center = (csc_center.email, csc_center.owner, csc_center.slug, csc_center.name)
                send_expiry_warning_mail.delay(center)
        logger.info("Checked for expiring csc centers and expiry warning message has been forwarded to the expiring csc centers.")
    except Exception as e:
        logger.error(f"Error in checking expiring csc centers: {e}")
