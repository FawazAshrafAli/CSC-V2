from django.urls import path
from .views import AddCscCenterView, RemoveCscCenterBannerView

app_name = "csc_center"

urlpatterns = [
    path('', AddCscCenterView.as_view(), name="add_csc"),
    path('remove_banners/<str:slug>', RemoveCscCenterBannerView.as_view(), name="remove_banners")
]
