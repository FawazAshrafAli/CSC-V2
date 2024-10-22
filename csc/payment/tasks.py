from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import Http404
from celery.utils.log import get_task_logger

from payment.models import Payment

logger = get_task_logger(__name__)

def html_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = HttpResponse(content_type="application/pdf")
    pdf = pisa.CreatePDF(html, dest=result)
    if not pdf.err:
        return result.content
    return None

@shared_task
def send_payment_success_email(payment_id, full_image_url):
    try:
        payment = get_object_or_404(Payment, pk = payment_id)
        
        subject = "Payment Successfull and CSC Center Account Activated"

        total = payment.amount
        
        pdf_data = {
            "payment": payment,
            "image": full_image_url,
            "total": total
        }

        pdf_content = html_to_pdf("invoice/invoice.html", pdf_data)

        email_context = {
            "csc_center_name": payment.csc_center.name,
            "owner": payment.csc_center.owner,
            "amount": payment.amount
        }

        email_body = render_to_string('payment_email_templates/payment_successful.html', email_context)

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.csc_center.email]
        )

        email.content_subtype = 'html'

        if pdf_content:
            email.attach('invoice.pdf', pdf_content, 'application/pdf')

        email.send()
        
        return "Email sent successfully"

    except Http404:
        return f"Payment with ID {payment_id} does not exist"
    
    except Exception as e:
        logger.error(f"Error in sending payment success email: {e}")