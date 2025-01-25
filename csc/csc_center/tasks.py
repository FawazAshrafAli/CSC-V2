from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from celery.utils.log import get_task_logger
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.mail import send_mail

from .models import CscCenter, ExpiredCscCenter, ExpiringCscCenter

logger = get_task_logger(__name__)

@shared_task
def send_expired_notification_mail(center):
    try:
        email, owner, center_slug, center_name, expiration_date = center

        subject = 'Your Csc Center Account is Expired'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]

        html_content = render_to_string('email_templates/csc_expired.html', {
            'owner_name': owner,
            'expiration_date': expiration_date,
            'support_email': from_email,
            'center_name': center_name,
            'renew_link': f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/payment/{center_slug}"                
        })

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        
        # email.send()

        csc_center = get_object_or_404(ExpiredCscCenter, csc_center__slug = center_slug)
        csc_center.sent_expiry_email = True
        csc_center.save()

    except Http404:
        logger.error("Invalid CSC Center")

    except Exception as e:
        logger.exception(f"Error in send_expired_notification_mail function of csc_center/tasks.py: {e}")

@shared_task
def send_expiry_warning_mail(center):
    try:
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
        
        # email.send()

        csc_center = get_object_or_404(ExpiringCscCenter, csc_center__slug = center_slug)
        csc_center.sent_expiring_email = True
        csc_center.save()

    except Http404:
        logger.error("Invalid CSC Center")

    except Exception as e:
        logger.exception(f"Error in send_expiry_warning_mail function of csc_center/tasks.py: {e}")


@shared_task
def check_validity():
    try:
        current_day = timezone.now().date()
        
        logger.info("Validity check initiated.")

        new_expired_csc_centers = CscCenter.objects.filter(is_active=True, next_payment_date__lte = current_day)

        for csc_center in new_expired_csc_centers:
            # Remove from expiring csc center model
            ExpiringCscCenter.objects.filter(csc_center = csc_center).delete()

            # Add to expired csc center model
            ExpiredCscCenter.objects.update_or_create(
                csc_center = csc_center, defaults={"expired_date": csc_center.next_payment_date}
            )

        new_expired_csc_centers.update(is_active = False)

        logger.info(f"{new_expired_csc_centers.count()} CSC centers marked as inactive.")            

        expired_csc_centers = ExpiredCscCenter.objects.filter(sent_expiry_email = False)

        for obj in expired_csc_centers:
            center = (obj.csc_center.email, obj.csc_center.owner, obj.csc_center.slug, obj.csc_center.name, obj.csc_center.next_payment_date)
            send_expired_notification_mail.delay(center)

        # Notify every month after expiry
        notified_csc_center = ExpiredCscCenter.objects.filter(sent_expiry_email = True, updated__lte = current_day - timedelta(days=30))
        
        for obj in notified_csc_center:
            center = (obj.csc_center.email, obj.csc_center.owner, obj.csc_center.slug, obj.csc_center.name, obj.csc_center.next_payment_date)
            send_expired_notification_mail.delay(center)
            obj.updated = timezone.now()
            obj.save()

        logger.info(f"Triggered expiry email tasks for {expired_csc_centers.count()} CSC centers.")
    except Exception as e:
        logger.exception(f"Error checking validity: {e}")

@shared_task
def check_expiring_centers():
    try:
        current_day = timezone.now().date()
        date_after_30_days = current_day + timedelta(days=30)        

        new_expiring_csc_centers = CscCenter.objects.filter(is_active = True, next_payment_date__gt = current_day, next_payment_date__lte = date_after_30_days)

        for csc_center in new_expiring_csc_centers:
            ExpiringCscCenter.objects.update_or_create(
                csc_center = csc_center, defaults={"expiration_date": csc_center.next_payment_date}
            )

        expiring_csc_centers = ExpiringCscCenter.objects.filter(sent_expiring_email = False)

        for obj in expiring_csc_centers:
            center = (obj.csc_center.email, obj.csc_center.owner, obj.csc_center.slug, obj.csc_center.name, obj.csc_center.next_payment_date)
            if current_day < obj.csc_center.next_payment_date:
                send_expiry_warning_mail.delay(center)
            else:
                obj.delete()
        logger.info("Checked for expiring csc centers and expiry warning message has been forwarded to the expiring csc centers.")
    except Exception as e:
        logger.exception(f"Error in checking expiring csc centers: {e}")

@shared_task
def send_dummy_email():
    subject = "Test Mail"
    message = "This is a test mail. Don't respond to this."
    from_mail = settings.DEFAULT_FROM_EMAIL
    to_email = ["w3digitalpmna@gmail.com"]

    try:
        send_mail(subject, message, from_mail, to_email)
        logger.info("Test email sent successfully.")
        return {"status": "success", "message": "Test email sent successfully."}
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        return {"status": "error", "message": str(e)}