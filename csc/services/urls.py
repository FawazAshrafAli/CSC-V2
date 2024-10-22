from django.urls import path
from .views import ListServiceView, DetailServiceView, CreateServiceEnquiryView

app_name = "services"

urlpatterns = [
    path("", ListServiceView.as_view(), name="services"),
    path("service/<str:slug>", DetailServiceView.as_view(), name="service"),
    path("request_service/<str:slug>", CreateServiceEnquiryView.as_view(), name="request_service"),
]
