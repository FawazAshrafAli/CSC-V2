from django.db import models
from django.utils.text import slugify

class Enquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone = models.TextField(max_length=20)
    location = models.TextField(max_length=150)
    message = models.TextField()

    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.email}")
            self.slug = base_slug
            count = 1
            while Enquiry.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
            
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created']
        db_table = 'enquiry'


