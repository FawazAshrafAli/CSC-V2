from django.urls import path
from .views import PaymentView, PaymentSuccessView, get_price

app_name = "payment"

urlpatterns = [
    path("<str:slug>", PaymentView.as_view(), name="payment"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("get_price/", get_price, name="get_price"),
]
