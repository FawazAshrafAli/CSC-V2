from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from csc_center.models import CscCenter
from django.urls import reverse

from services.models import Service
from csc_center.models import State

class Poster(models.Model):
    title = models.CharField(max_length=100)
    poster = models.ImageField(upload_to="posters/")
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Poster.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['title']
        db_table = 'poster'


    def __str__(self):
        return self.title


class PosterFooter(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="poster_footer/", null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"{slugify(self.csc_center.name)}-footer"
            slug = base_slug
            count = 1
            while PosterFooter.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["created"]
        db_table = "poster_footer"
    