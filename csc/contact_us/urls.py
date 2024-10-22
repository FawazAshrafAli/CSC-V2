from django.urls import path
from .views import ContactUsView, SubmitEnquiryView

app_name = "contact_us"

urlpatterns = [
    path('', ContactUsView.as_view(), name = "view"),
    path('submit_enquiry/', SubmitEnquiryView.as_view(), name="submit_enquiry"),
]
