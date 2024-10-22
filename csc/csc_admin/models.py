from django.db import models
from django.utils.text import slugify

from csc_center.models import CscCenter
from services.models import Service

class CscCenterAction(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    rejection_reason = models.TextField()
    feedback = models.TextField()

    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.csc_center.name)
            self.slug = base_slug
            count = 1
            while CscCenter.objects.filter(slug = self.slug).exists():
                self.slug = f"{self.slug}-{count}"
                count += 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-updated"]
        db_table = 'csc_center_action'

    def __str__(self):
        return self.csc_center.name
    

class ServiceEnquiry(models.Model):    
    applicant_name = models.CharField(max_length=150)
    applicant_email = models.EmailField(max_length=254)
    applicant_phone = models.CharField(max_length=20)
    service = models.ForeignKey("services.Service", on_delete=models.CASCADE, related_name="admin_service_enquiry_service")
    location = models.TextField()
    message = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.applicant_email+ '-' + self.service.name)
            self.slug = base_slug

            count = 1
            while ServiceEnquiry.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
        
        return super().save(*args, **kwargs)            
    
    def __str__(self):
        return f"From {self.applicant_email} to {self.csc_center.name}"
    
    class Meta:
        db_table = 'admin_service_enquiry'
        ordering = ['-created']


class ProductEnquiry(models.Model):
    applicant_name = models.CharField(max_length=150)
    applicant_email = models.EmailField(max_length=254)
    applicant_phone = models.CharField(max_length=20)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="admin_product_enquiry_product")
    location = models.TextField()
    message = models.TextField()
    
    is_viewed = models.BooleanField(default= False)

    slug = models.SlugField(blank=True, null=True, max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.applicant_email+ '-' + self.product.name)
            self.slug = base_slug

            count = 1
            while ProductEnquiry.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1

            print(self.slug)
        
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"From {self.applicant_email} to {self.csc_center.name}"
    
    class Meta:
        db_table = 'admin_product_enquiry'
        ordering = ['-created']