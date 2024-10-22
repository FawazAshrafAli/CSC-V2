from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'product_category'
        ordering = ['name']
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.CASCADE, related_name="product_category")
    slug = models.SlugField(unique=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Product'
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
    

class ProductEnquiry(models.Model):
    csc_center = models.ForeignKey("csc_center.CscCenter", on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=150)
    applicant_email = models.EmailField(max_length=254)
    applicant_phone = models.CharField(max_length=20)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
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
    
    @property
    def get_absolute_url(self):
        return reverse("users:product_enquiry", kwargs={"slug": self.slug})
    
    
    def __str__(self):
        return f"From {self.applicant_email} to {self.csc_center.name}"
    
    class Meta:
        db_table = 'product_enquiry'
        ordering = ['-created']

