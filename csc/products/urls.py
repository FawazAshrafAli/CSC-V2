from django.urls import path
from .views import ProductListView, CategoryFilteredProductsListView, CreateProductEnquiryView

app_name = "products"

urlpatterns = [
    path('', ProductListView.as_view(), name="products"),
    path('tags/<str:slug>', CategoryFilteredProductsListView.as_view(), name="category"),
    path('request_product/<str:slug>', CreateProductEnquiryView.as_view(), name="request_product"),
]
