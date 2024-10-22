from django.urls import path
from .views import (
    Error404,
    HomePageView, SearchCscCenterView,
    FilterAndSortCscCenterView, CscCenterDetailView,
    NearMeCscCenterView, ServiceRequestView, ProductRequestView, 
    KeywordsBasedCscCentersView, PrivacyPolicyView, TermAndConditionView,
    ShippingAndDeliveryPolicyView, CancellationAndRefundPolicyView
)

app_name = "home"

urlpatterns = [
    path('', HomePageView.as_view(), name="view"), 

    path('privacy_policy/', PrivacyPolicyView.as_view(), name="privacy_policy"),
    path('terms_and_conditions/', TermAndConditionView.as_view(), name="terms_and_conditions"),
    path('shipping_and_delivery_policy/', ShippingAndDeliveryPolicyView.as_view(), name="shipping_and_delivery_policy"),
    path('cancellation_and_refund_policy/', CancellationAndRefundPolicyView.as_view(), name="cancellation_and_refund_policy"),

    path('error404/', Error404.as_view(), name="error404"),

    path('tags/<str:slug>/', KeywordsBasedCscCentersView.as_view(), name="tags"),

    path('service_request/<str:slug>', ServiceRequestView.as_view(), name="service_request"),
    path('product_request/<str:slug>', ProductRequestView.as_view(), name="product_request"),
    path('centers_near_me/<latitude>/<longitude>', NearMeCscCenterView.as_view(), name="centers_near_me"),

    path('csc_centers/', SearchCscCenterView.as_view(), name="csc_centers"),
    path('filter_and_sort_centers/', FilterAndSortCscCenterView.as_view(), name="filter_and_sort_csc"),
    path("<str:slug>/", CscCenterDetailView.as_view(), name="csc_center"),

]