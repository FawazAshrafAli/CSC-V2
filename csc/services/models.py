from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.urls import reverse

class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to="service_image/", null=True, blank=True)
    description = RichTextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=150)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def first_name(self):
        if self.name.endswith(' in India'):
            return self.name.split(' in India')[0]
        return self.name
        
    @property
    def tailing_name(self):
        if self.name.endswith(' in India'):
            return 'in India'
        

    @property
    def get_absolute_url(self):
        return reverse("services:service", kwargs={"slug": self.slug})
    

    def __str__(self):
        return self.name
    

class ServiceEnquiry(models.Model):
    csc_center = models.ForeignKey("csc_center.CscCenter", on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=150)
    applicant_email = models.EmailField(max_length=254)
    applicant_phone = models.CharField(max_length=20)
    service = models.ForeignKey("services.Service", on_delete=models.CASCADE)
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
        db_table = 'service_enquiry'
        ordering = ['-created']

