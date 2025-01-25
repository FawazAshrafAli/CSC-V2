from django.core.mail import send_mail
from celery import shared_task
from celery.utils.log import get_task_logger
from django.urls import reverse_lazy
from django.conf import settings
from authentication.models import User

logger = get_task_logger(__name__)

@shared_task
def send_otp_email(email, otp):
    try:
        subject = 'OTP for setting password'
        message = f'Your OTP code is {otp}. It is valid for the next 5 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        receipient_list = [email]

        send_mail(subject, message, from_email, receipient_list)
    except Exception as e:
        logger.error(f'Error sending OTP email: {e}')


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def send_verification_otp(self, otp, email):
    try:
        subject = "OTP for Verifying Your Email"
        plain_message = f"Your OTP code is {otp}. It is valid for the next 5 minutes."
        html_message = f"""
        <html>
            <body>
                <p>Your OTP code is <strong>{otp}</strong>.</p>
                <p>It is valid for the next <strong>5 minutes</strong>.</p>
            </body>
        </html>
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
        )
    except Exception as e:
        logger.exception(f"Error in sending verification OTP to {email}: {e}")
        raise self.retry(exc=e)
