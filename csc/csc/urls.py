"""
URL configuration for csc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django_admin/', admin.site.urls),
    path('about_us/', include('about_us.urls', namespace='about_us')), # About_us app url
    path('authentication/', include('authentication.urls', namespace='authentication')),
    path('services/', include('services.urls', namespace='services')), # Services app url
    path('products/', include('products.urls', namespace='products')), # Products app url
    path('posters/', include('posters.urls', namespace='posters')), # Poster app url
    path('contact_us/', include('contact_us.urls', namespace='contact_us')), # Contact_us app url
    path('blog/', include('blog.urls', namespace='blog')), # Blog app url
    path('csc_center/', include('csc_center.urls', namespace = "csc_center")), # CSC Center app url
    path('users/', include('users.urls', namespace = "users")), # Users app url
    path('faq/', include('faq.urls', namespace = "faq")), # Faq app url
    path('payment/', include('payment.urls', namespace = "payment")), # Payment app url

    path('admin/', include('csc_admin.urls', namespace='csc_admin')), # CSC Admin app url

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('home.urls', namespace='home')), # Home app url
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
