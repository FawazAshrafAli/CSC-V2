from django.urls import path
from .views import FaqListView

app_name = "faq"

urlpatterns = [
    path('', FaqListView.as_view(), name="faqs"),
]
