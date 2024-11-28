from django.db import models
from django.utils.text import slugify
from services.models import Service
from products.models import Product
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64
from django.conf import settings
from django.utils import timezone
from django.db.models import Max
from django.urls import reverse
import uuid

class State(models.Model):
    state = models.CharField(max_length=150)
    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.state)
            slug = base_slug
            count = 1
            while State.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return self.state

    class Meta:
        ordering = ['state']

class District(models.Model):
    district = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.district)
            slug = base_slug
            count = 1
            while State.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'districts'
        ordering = ["district"]

    def __str__(self):
        return self.district


class Block(models.Model):
    block = models.CharField(max_length=150)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.block)
            slug = base_slug
            count = 1
            while State.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'blocks'
        ordering = ["block"]

    def __str__(self):
        return self.block

class CscNameType(models.Model):
    type = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'csc_name_type'
        ordering = ["type"]

    def __str__(self):
        return self.type


class CscKeyword(models.Model):
    keyword = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.keyword)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'csc_keywords'
        ordering = ["keyword"]

    def __str__(self):
        return self.keyword

class SocialMediaLink(models.Model):
    csc_center_id = models.ForeignKey('CscCenter', on_delete=models.CASCADE)
    social_media_name = models.CharField(max_length=150)
    social_media_link = models.URLField()

    def __str__(self):
        return f"{self.social_media_name} for {self.csc_center_id.name}"
    

class Banner(models.Model):
    csc_center = models.ForeignKey('CscCenter', on_delete=models.CASCADE, related_name = "banner_csc_center")
    banner_image = models.ImageField(upload_to='csc_center_banners/')

def csc_id_generator():
    str_id = "CSC"
    
    last_center = CscCenter.objects.aggregate(Max('id'))
    max_id = last_center['id__max']

    max_id = max_id[3:] if type(max_id) == str and max_id.startswith('CSC') else max_id
    
    if max_id is not None and int(max_id) > 22789:
        int_id = int(max_id) + 1
    else:
        int_id = 22800
    
    combined_id = f"{str_id}{int_id}"

    while CscCenter.objects.filter(id=combined_id).exists():
        int_id += 1 
        combined_id = f"{str_id}{int_id}"

    return combined_id

class CscCenter(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=csc_id_generator)
    csc_reg_no = models.CharField(max_length = 50, null=True, blank=True)
    qr_code_image = models.ImageField(upload_to='csc_qr_codes/', blank=True, null=True)

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=250)
    type = models.ForeignKey(CscNameType, on_delete=models.CASCADE, null=True)
    
    keywords = models.ManyToManyField(CscKeyword)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    location = models.TextField()
    zipcode = models.CharField(max_length=15)
    landmark_or_building_name = models.CharField(max_length=100, null=True, blank=True)
    street = models.CharField(max_length=500)
    
    logo = models.ImageField(upload_to='csc_center_logos/', blank=True, null=True)
    banners = models.ManyToManyField(Banner)

    description = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    website = models.URLField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=100, null=True, blank=True)
    services = models.ManyToManyField(Service)
    products = models.ManyToManyField(Product)

    show_opening_hours = models.BooleanField(default=True)

    mon_opening_time = models.TimeField(null=True, blank=True)
    tue_opening_time = models.TimeField(null=True, blank=True)
    wed_opening_time = models.TimeField(null=True, blank=True)
    thu_opening_time = models.TimeField(null=True, blank=True)
    fri_opening_time = models.TimeField(null=True, blank=True)
    sat_opening_time = models.TimeField(null=True, blank=True)
    sun_opening_time = models.TimeField(null=True, blank=True)

    mon_closing_time = models.TimeField(null=True, blank=True)
    tue_closing_time = models.TimeField(null=True, blank=True)
    wed_closing_time = models.TimeField(null=True, blank=True)
    thu_closing_time = models.TimeField(null=True, blank=True)
    fri_closing_time = models.TimeField(null=True, blank=True)
    sat_closing_time = models.TimeField(null=True, blank=True)
    sun_closing_time = models.TimeField(null=True, blank=True)

    show_social_media_links = models.BooleanField(default = True)

    social_media_links = models.ManyToManyField(SocialMediaLink)

    latitude = models.CharField(max_length=100, null=True)
    longitude = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    payment_implemented_date = models.DateField(blank=True, null=True)
    inactive_date = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=False)

    status = models.CharField(max_length=100, default="Not Viewed")

    def save(self, *args, **kwargs):
        self.generate_qr_code_image()

        if not str(self.pk).startswith("CSC"):
            try:
                base_id = int(self.pk)
                while CscCenter.objects.filter(pk = f"CSC{str(base_id)}").exists():
                    base_id += 1
                self.pk = f"CSC" + str(base_id)
            except Exception as e:
                print("Error: {e}")

        if not str(self.pk).startswith("CSC"):
            base_id = int(self.pk)
            while CscCenter.objects.filter(pk = f"CSC{str(base_id)}").exists():
                base_id += 1
            self.pk = f"CSC{str(base_id)}"

        if self.keywords.all().count() < 1:
            self.keywords.add(CscKeyword.objects.earliest('created'))        

        if not self.slug:
            if self.name:
                base_slug = slugify(self.name)

                if not base_slug or base_slug == "":
                    self.slug = str(uuid.uuid4())
                
                else:
                    slug = base_slug
                    count = 1
                    while CscCenter.objects.filter(slug = slug).exists():
                        slug = f"{base_slug}-{count}"
                        count += 1
                    self.slug = slug
            else:
                self.slug = str(uuid.uuid4())

        if not self.logo:
            self.logo = "../static/w3/images/csc_default.jpeg"

        if not self.payment_implemented_date:
            self.payment_implemented_date = self.created.date()

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        if self.name and self.name != "nan" and self.type and self.type != "nan" and self.location and self.location != "nan":
            return f"{self.name} {self.type} {self.location}"
        elif self.name and self.name != "nan" and self.street and self.street != "nan" :
            return f"{self.name} {self.street}"
        return self.name

    @property
    def type_and_location(self):
        if self.type and self.location:
            return f"{self.type} {self.location}"
        elif self.type:
            return self.type
        elif self.location:
            return self.location
        return None
    
    @property
    def partial_address(self):
        block = self.block.block if self.block and self.block.block != "nan" else None
        district = self.district.district if self.district and self.district.district != "nan" else None
        state = self.state.state if self.state and self.state.state != "nan" else None

        parts = [block, district, state]
        address = ", ".join(part for part in parts if part)
        return address if address else None

    @property
    def get_vertical_partial_address(self):
        block = self.block.block if self.block and self.block.block != "nan" else None
        district = self.district.district if self.district and self.district.district != "nan" else None
        state = self.state.state if self.state and self.state.state != "nan" else None

        parts = [block, district, state]
        address = ",<br>".join(part for part in parts if part)
        return address if address else None
        
    
    @property
    def full_address(self):
        return f"{self.landmark_or_building_name}, {self.street}, {self.location} {self.zipcode}, {self.block}, {self.district}, {self.state}"
    
    @property
    def get_absolute_url(self):
        return reverse('home:csc_center', kwargs={"slug": self.slug})
    
    @property
    def get_services(self):
        if self.services:
            service_list = []
            for service in self.services.all():
                service_list.append(service.name)
            return service_list
        return None
    
    @property
    def get_products(self):
        if self.products:
            product_list = []
            for product in self.products.all():
                product_list.append(product.name)
            return product_list
        return None

    @property
    def get_keywords(self):
        if self.keywords:
            keyword_list = []
            for keyword in self.keywords.all():
                keyword_list.append(keyword.keyword)

            return keyword_list
        return None
    
    @property
    def get_keywords_as_string(self):
        if self.keywords and self.get_keywords is not None:            
            return ", ".join(self.get_keywords)
        return None

    @property
    def qr_code(self):            
        url = self.get_absolute_url
        protocol = settings.SITE_PROTOCOL  # e.g., 'http' or 'https'
        domain = settings.SITE_DOMAIN     # e.g., 'example.com'
        full_url = f"{protocol}://{domain}{url}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return qr_code_base64
    
    @property
    def live_days(self):
        if not self.is_active:
            today = timezone.now().date()
            if self.inactive_date:
                inactive_date = self.inactive_date
                return (today - inactive_date).days
        return None
    
    def generate_qr_code_image(self):
        url = self.get_absolute_url  
        protocol = settings.SITE_PROTOCOL 
        domain = settings.SITE_DOMAIN    
        full_url = f"{protocol}://{domain}{url}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10, 
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_code_{self.pk}.png'
        self.qr_code_image.save(filename, ContentFile(buffer.read()), save=False)

    @property
    def owner_locations(self):
        owned_csc_centers = CscCenter.objects.filter(email = self.email)
        location_list = [f"{center.block.block}, {center.district.district}, {center.state.state}"  for center in owned_csc_centers]
        return location_list
    
    @property
    def get_contact_number(self):
        if self.contact_number:
            if not self.contact_number.startswith("+91"):
                return f"+91{self.contact_number}"
            return self.contact_number
        return None
    
    @property
    def get_mobile_number(self):
        if self.mobile_number:
            if not self.mobile_number.startswith("+91"):
                return f"+91{self.mobile_number}"
            return self.mobile_number
        return None
    
    @property
    def get_whatsapp_number(self):
        if self.whatsapp_number:
            if self.whatsapp_number.startswith("+91"):
                return self.whatsapp_number.replace("+91", "91")
            elif not self.whatsapp_number.startswith("91"):
                return f"91{self.whatsapp_number}"
            return self.whatsapp_number
        return None

    class Meta:
        db_table = 'csc_center'
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class Image(models.Model):
    name = models.CharField(max_length=150, default="No Image")
    image = models.ImageField(upload_to="rough/", blank=True, null=True)
    banner = models.ImageField(upload_to="rough_banner/", blank=True, null=True)