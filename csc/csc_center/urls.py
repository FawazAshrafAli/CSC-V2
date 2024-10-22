from django.urls import path
from .views import AddCscCenterView

app_name = "csc_center"

urlpatterns = [
    path('', AddCscCenterView.as_view(), name="add_csc"),
]
