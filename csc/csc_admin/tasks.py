from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_confirm_creation(center, payment_link):
    try:
        subject = 'Welcome to Our Website'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [center["email"]]
        
        html_content = render_to_string('admin_email_templates/csc_approve.html', {'name': center["name"], 'owner': center["owner"], 'payment_link': payment_link})
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
         logger.error(f'Error sending confirmation mail: {e}')

@shared_task
def send_offer_mail(center, price):
    try:
        subject = 'Exclusive Offer for CSC Center Registration'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [center.email]

        html_content = render_to_string('admin_email_templates/offer.html', {
            'customer_name': center.owner,
            'offer_price': price.offer_price,
            'offer_start_date': price.from_date,
            'offer_expiry_date': price.to_date,
            'sender_mail': from_email
        })

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        
        email.send()
    except Exception as e:
        logger.error(f'Error sending offer mail: {e}')