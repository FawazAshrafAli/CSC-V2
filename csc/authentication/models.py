from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    image = models.ImageField(upload_to="profile_pic/", blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    notes = models.TextField(null=True, blank=True)
    twitter = models.URLField(max_length=150, null=True, blank=True)
    facebook = models.URLField(max_length=150, null=True, blank=True)
    google = models.URLField(max_length=150, null=True, blank=True)

    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    


    @property
    def full_name(self):
        if self.first_name:
            full_name = self.first_name
            if self.last_name:
                full_name += f" {self.last_name}"

            return full_name
    

class UserOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length = 7, blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)