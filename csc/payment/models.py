from django.db import models
from django.utils.text import slugify

from csc_center.models import CscCenter

class Price(models.Model):
    price = models.FloatField()
    offer_price = models.FloatField(null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)    

class Payment(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    status = models.CharField(max_length=100, default='pending')
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.payment_id} - {self.status}"

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.csc_center.name}-{self.order_id}")
            self.slug = base_slug
            count = 1
            while Payment.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1
            
        super().save(*args, **kwargs)

# class PaymentHistory(models.Model):
#     csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
#     transaction_id = models.CharField(max_length=100, unique=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=50, default="Pending")
#     payment_method = models.CharField(max_length=50, blank=True, null=True)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Transaction {self.transaction_id} - {self.status}"

#     class Meta:
#         ordering = ['-created']
