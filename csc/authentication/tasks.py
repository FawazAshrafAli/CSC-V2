from django.core.mail import send_mail
from celery import shared_task
from celery.utils.log import get_task_logger
from django.urls import reverse_lazy
from django.conf import settings

logger = get_task_logger(__name__)


@shared_task
def send_verification_email(self, user):
    try:
        verification_link = self.request.build_absolute_uri(
            reverse_lazy('authentication:verify_email', kwargs = {"token": user.verification_token})
        )

        sender = settings.DEFAULT_FROM_EMAIL

        send_mail(
            'Verify your email',
            f'Click the link to verify your email: {verification_link}',
            sender,
            [user.email],
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")


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