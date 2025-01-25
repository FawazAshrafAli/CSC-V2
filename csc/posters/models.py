from django.db import models
from django.utils.text import slugify
from csc_center.models import CscCenter

from services.models import Service
from products.models import Product
from csc_center.models import State

class Poster(models.Model):
    title = models.CharField(max_length=100)
    poster = models.ImageField(upload_to="posters/")
    states = models.ManyToManyField(State)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

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
    
    @property
    def get_states(self):
        if self.states.count() > 0:
            states = [state.state for state in self.states.all()]
            return ", ".join(states)

        return "All States"


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
    