from django.db import models
import uuid

def generate_csc_id():
    uuid_str = str(uuid.uuid4().int)
    return uuid_str[:12]


class Banner(models.Model):
    image = models.ImageField(upload_to="home_page_banner_image/")

    class Meta:
        db_table = "home_page_banner_image"

class HomePageBanner(models.Model):
    name = models.CharField(max_length=50, default="Home Page Banners")
    images = models.ManyToManyField(Banner)

    class Meta:
        db_table = "home_page_banners"

    @property
    def get_banners(self):
        banner_obj = HomePageBanner.objects.first()
        if banner_obj and banner_obj.images.count() > 0:        
            list_banners = [f"<a href='{banner.image.url}' target='_blank' style='color:blue'>{(banner.image.name.replace('home_page_banner_image/', ''))}</a>" for banner in banner_obj.images.all()]
            return ', '.join(list_banners)
        return None