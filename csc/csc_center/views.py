from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from datetime import datetime
from math import ceil, floor
from django.http import Http404
from django.db.models import Q
from django.contrib.auth import logout
import logging
import uuid
import time

from .models import CscCenter, CscKeyword, CscNameType, State, District, Block, SocialMediaLink, Banner
from services.models import Service
from products.models import Product
from authentication.models import User
from payment.models import Payment

from base.views import BaseView

logger = logging.getLogger(__name__)

class AddCscCenterView(BaseView, CreateView):
    model = CscCenter
    template_name = 'csc_center/add.html'
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy("csc_center:add_csc")
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['name_types'] = CscNameType.objects.all().order_by('type')
            context['keywords'] = CscKeyword.objects.all().order_by('keyword')
            context['products'] = Product.objects.all()
            context['services'] = Service.objects.all()
            context['states'] = State.objects.all()
            context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]

            time_data = []
            for i in range(1, 25):
                if i < 13:
                    str_time = f"{i} AM"
                else:
                    str_time = f"{i-12} PM"            
                time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
                time_data.append({"str_time": str_time, "time": time})
                context['time_data'] = time_data
        except Exception as e:
            logger.exception("Error in fetching add csc center context data: %s", e)

        return context

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            type = request.POST.get('type')
            csc_reg_no = request.POST.get('csc_reg_no')
            keywords = request.POST.getlist('keywords')

            state = request.POST.get('state')
            district = request.POST.get('district')
            block = request.POST.get('block')
            location = request.POST.get('location')
            zipcode = request.POST.get('zipcode')
            landmark_or_building_name = request.POST.get('landmark_or_building_name')
            street = request.POST.get('address')
            logo = request.FILES.get('logo')
            banners = request.FILES.getlist('banner')
            description = request.POST.get('description')
            owner = request.POST.get('owner')
            email = request.POST.get('email')
            website = request.POST.get('website')
            contact_number = request.POST.get('contact_number')
            mobile_number = request.POST.get('mobile_number')
            whatsapp_number = request.POST.get('whatsapp_number')
            services = request.POST.getlist('services')
            products = request.POST.getlist('products')

            show_opening_hours = request.POST.get('show_opening_hours')
            if show_opening_hours: 
                show_opening_hours = show_opening_hours.strip()

            mon_opening_time = request.POST.get('mon_opening_time')
            tue_opening_time = request.POST.get('tue_opening_time')
            wed_opening_time = request.POST.get('wed_opening_time')
            thu_opening_time = request.POST.get('thu_opening_time')
            fri_opening_time = request.POST.get('fri_opening_time')
            sat_opening_time = request.POST.get('sat_opening_time')
            sun_opening_time = request.POST.get('sun_opening_time')

            mon_closing_time = request.POST.get('mon_closing_time')
            tue_closing_time = request.POST.get('tue_closing_time')
            wed_closing_time = request.POST.get('wed_closing_time')
            thu_closing_time = request.POST.get('thu_closing_time')
            fri_closing_time = request.POST.get('fri_closing_time')
            sat_closing_time = request.POST.get('sat_closing_time')
            sun_closing_time = request.POST.get('sun_closing_time')

            mon_opening_time = mon_opening_time.strip() if mon_opening_time else None
            tue_opening_time = tue_opening_time.strip() if tue_opening_time else None
            wed_opening_time = wed_opening_time.strip() if wed_opening_time else None
            thu_opening_time = thu_opening_time.strip() if thu_opening_time else None
            fri_opening_time = fri_opening_time.strip() if fri_opening_time else None
            sat_opening_time = sat_opening_time.strip() if sat_opening_time else None
            sun_opening_time = sun_opening_time.strip() if sun_opening_time else None
    
            mon_closing_time =         mon_closing_time.strip() if mon_closing_time else None
            tue_closing_time = tue_closing_time.strip() if tue_closing_time else None
            wed_closing_time = wed_closing_time.strip() if wed_closing_time else None
            thu_closing_time = thu_closing_time.strip() if thu_closing_time else None
            fri_closing_time = fri_closing_time.strip() if fri_closing_time else None
            sat_closing_time = sat_closing_time.strip() if sat_closing_time else None
            sun_closing_time = sun_closing_time.strip() if sun_closing_time else None

            show_social_media_links = request.POST.get('show_social_media_links')
            if show_social_media_links:
                show_social_media_links = show_social_media_links.strip()

            social_medias = request.POST.getlist('social_medias')
            social_links = request.POST.getlist('social_links')

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                type = get_object_or_404(CscNameType, slug = type.strip())
            except Http404:
                messages.error(request, 'Invalid CSC Name Type')
                return redirect(self.redirect_url)

            try:
                state = get_object_or_404(State, state = state.strip())
            except Http404:
                messages.error(request, 'Invalid State')
                return redirect(self.redirect_url)

            try:
                district = get_object_or_404(District, district = district.strip())
            except Http404:
                messages.error(request, 'Invalid District')
                return redirect(self.redirect_url)
            
            try:
                block = get_object_or_404(Block, block = block.strip())
            except Http404:
                messages.error(request, 'Invalid Block')
                return redirect(self.redirect_url)
            
            self.object = CscCenter.objects.create(
                name = name.strip() if name else None, type = type, csc_reg_no = csc_reg_no.strip() if csc_reg_no else None, 
                state = state, district = district, block = block, location = location.strip() if location else None,
                zipcode = zipcode.strip() if zipcode else None, landmark_or_building_name = landmark_or_building_name.strip() if landmark_or_building_name else None,
                street = street.strip() if street else None, logo = logo if logo else "/static/w3/images/csc_default.jpeg", description = description.strip() if description else None, contact_number = contact_number.strip() if contact_number else None,
                owner = owner.strip() if owner else None, email = email.strip() if email else None, website = website.strip() if website else None, 
                mobile_number = mobile_number.strip() if mobile_number else None, whatsapp_number = whatsapp_number.strip() if whatsapp_number else None,
                mon_opening_time = mon_opening_time, tue_opening_time = tue_opening_time, 
                wed_opening_time = wed_opening_time, thu_opening_time = thu_opening_time, 
                fri_opening_time = fri_opening_time, sat_opening_time = sat_opening_time, 
                sun_opening_time = sun_opening_time, mon_closing_time = mon_closing_time, 
                tue_closing_time = tue_closing_time, wed_closing_time = wed_closing_time, 
                thu_closing_time = thu_closing_time, fri_closing_time = fri_closing_time, 
                sat_closing_time = sat_closing_time, sun_closing_time = sun_closing_time, 
                latitude = latitude.strip() if latitude else None, longitude = longitude.strip() if longitude else None
            )
            
            # after creation of object
            self.object.keywords.set(keywords)
            self.object.services.set(services)
            self.object.products.set(products)
            self.object.save()

            current_keywords = self.object.keywords.all()
            keyword_count = current_keywords.count()
            keywords_needed = 4 - keyword_count

            if keywords_needed > 0:
                additional_keywords = CscKeyword.objects.exclude(id__in=current_keywords.values_list('id', flat=True))
                keywords_to_add = additional_keywords[:keywords_needed]
                self.object.keywords.add(*keywords_to_add)
                self.object.save()

            current_services = self.object.services.all()
            service_count = current_services.count()
            services_needed = 20 - service_count

            if services_needed > 0:
                additional_services = Service.objects.exclude(id__in=current_services.values_list('id', flat=True))

                services_to_add = additional_services[:services_needed]
                
                self.object.services.add(*services_to_add)

                self.object.save()

            if banners:
                for banner in banners:
                    banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                    self.object.banners.add(banner_obj)
                self.object.save()

            if social_medias and social_links:
                social_media_length = len(social_medias)
                if social_media_length > 0:
                    social_media_list = []
                    for i in range(social_media_length):
                        if social_medias[i] and social_links[i]:
                            social_media_link, created = SocialMediaLink.objects.get_or_create(
                                csc_center_id = self.object,
                                social_media_name = social_medias[i].strip(),
                                social_media_link = social_links[i].strip()
                            )
                            social_media_list.append(social_media_link)
                    
                        self.object.social_media_links.set(social_media_list)
                        self.object.save()

            messages.success(request, "Added CSC center")

            if not User.objects.filter(email = email).exists():
                logout(request)        
                return redirect(reverse('authentication:user_registration', kwargs={'email': self.object.email}))
            elif request.user.is_authenticated and request.user.email == email:
                return redirect(reverse_lazy("users:home"))
            else:
                logout(request)
            
            return redirect(self.success_url)
        except Exception as e:
            msg = "Failed to add csc center"
            logger.exception(f"{msg}: {e}")
            messages.error(request, msg)
            return redirect(self.redirect_url)


# populate csc center data using excel spread sheet
import pandas as pd

def convert_to_int_if_scientific_notation(value):
    """Convert value to int if it's in scientific notation."""
    if "E+" in str(value):
        return int(float(value))
    return value

def convert_to_int():
    csc_centers = CscCenter.objects.filter(Q(name__icontains = "E+") | Q(mobile_number__icontains = "E+") | Q(contact_number__icontains = "E+") | Q(whatsapp_number__icontains = "E+") | Q(latitude__icontains = "E+") | Q(longitude__icontains = "E+"))
    to_update = []

    for csc_center in csc_centers:
        csc_center.mobile_number = convert_to_int_if_scientific_notation(csc_center.mobile_number)
        csc_center.contact_number = convert_to_int_if_scientific_notation(csc_center.contact_number)
        csc_center.whatsapp_number = convert_to_int_if_scientific_notation(csc_center.whatsapp_number)
        csc_center.latitude = convert_to_int_if_scientific_notation(csc_center.latitude)
        csc_center.longitude = convert_to_int_if_scientific_notation(csc_center.longitude)

        to_update.append(csc_center)
    
    CscCenter.objects.bulk_update(to_update, ['mobile_number', 'contact_number', 'whatsapp_number', 'latitude', 'longitude'])

    return "Convertion to int completed"

def remove_nan():
    csc_centers = CscCenter.objects.filter(Q(latitude = "nan") | Q(longitude = "nan"))

    for csc_center in csc_centers:
        if csc_center.latitude == "nan":
            csc_center.latitude = ''

        if csc_center.longitude == "nan":
            csc_center.longitude = ''
            
        csc_center.save()

    return "Removing nan completed"

def create_dummy_payments():
    project_updation_date = datetime.strptime("10-10-2024", "%d-%m-%Y").date()
    old_csc_centers = CscCenter.objects.filter(created__lt = project_updation_date)

    payment_list = []
    
    for csc_center in old_csc_centers:
        years_before_updation = (project_updation_date - csc_center.created.date()).days / 365
        number_of_old_payments = ceil(years_before_updation) if csc_center.is_active else floor(years_before_updation)
        leftover_payment = number_of_old_payments - Payment.objects.filter(csc_center = csc_center, status = "Completed").count()

        if leftover_payment > 0:
            for _ in range(leftover_payment):
                payment_list.append(
                    Payment(csc_center = csc_center, order_id = "Not Available", payment_id = uuid.uuid4(), amount = "0.00", status = "Completed")
                )
    
    Payment.objects.bulk_create(payment_list)

    return "Dummy payments created"

def remove_trailing_decimals():
    csc_centers = CscCenter.objects.filter(Q (contact_number__icontains = ".0") | Q(mobile_number__icontains = ".0") | Q(whatsapp_number__icontains = ".0"))
    to_update = []
    print()
    print("Removing trailing decimals. . .")
    for csc_center in csc_centers:
        if csc_center.contact_number:
            csc_center.contact_number = csc_center.contact_number.replace(".0", "")
        if csc_center.mobile_number:
            csc_center.mobile_number = csc_center.mobile_number.replace(".0", "")
        if csc_center.whatsapp_number:
            csc_center.whatsapp_number = csc_center.whatsapp_number.replace(".0", "")
        to_update.append(csc_center)

    CscCenter.objects.bulk_update(to_update, ["contact_number", "mobile_number", "whatsapp_number"])

    print()
    return "\nRemoved Trailing Decimals!"


def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        # if index >= 4999:
        yield index, row

def import_excel_data():
    # csv_data = pd.read_csv(r'D:\Projects\CSC\csc\csc_center\csc-centers.csv')
    csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')
    length = len(csv_data)  

    print("\nImporting data . . .\n")
    
    for index, row in row_generator(csv_data):
        
        time.sleep(0.001)

        current_state = str(row['cs_state']) if row['cs_state'] else None
        state, created =  State.objects.get_or_create(state = current_state.strip())

        current_district = str(row['cs_district']) if row['cs_district'] else None
        district, created =  District.objects.get_or_create(district = current_district.strip(), state = state)

        current_block = str(row['cs_block']) if row['cs_block'] else None
        block, created =  Block.objects.get_or_create(block = current_block.strip(), state = state, district = district)
 
        if not CscCenter.objects.filter(id = f"CSC{row['ID']}").exists():
            csc_center, created = CscCenter.objects.get_or_create(
                id = f"CSC{row['ID']}",
                name = row["csc_name"] if row["csc_name"] and row["csc_name"] != "nan" and row["csc_name"] != '' else None,
                slug = row["Slug"] if row["Slug"] and row["Slug"] != "nan" and row["Slug"] != '' else None,
                type = None,
                state = state,
                district = district,
                block = block,
                location = row["cs_address"] if row["cs_address"] and row["cs_address"] != "nan" and row["cs_address"] != '' else None,
                zipcode = row["csc_pincode"] if row["csc_pincode"] and row["csc_pincode"] != "nan" and row["csc_pincode"] != '' else None,
                street = row["csc_place"] if row["csc_place"] and row["csc_place"] != "nan" and row["csc_place"] != '' else None,
                owner = row["CSC Owner Name"] if row["CSC Owner Name"] and row["CSC Owner Name"] != "nan" and row["CSC Owner Name"] != '' else None,
                email = str(row["csc_email"].lower() if row["csc_email"] and type(row["csc_email"]) == str and row["csc_email"] != "nan" and row["csc_email"] != '' else None),
                contact_number = row["csc_phone"] if row["csc_phone"] and row["csc_phone"] != "nan" and row["csc_phone"] != '' else None,
                mobile_number = row["csc_phonetwo"] if row["csc_phonetwo"] and row["csc_phonetwo"] != "nan" and row["csc_phonetwo"] != '' else None,
                show_opening_hours = False, 
                show_social_media_links = False,
                latitude = row["csc_latitude"] if row["csc_latitude"] and len(str(row["csc_latitude"])) < 100 and row["csc_latitude"] != "nan" and row["csc_latitude"] != '' else None,
                longitude = row["csc_longitude"] if row["csc_longitude"] and len(str(row["csc_longitude"])) < 100 and row["csc_longitude"] != "nan" and row["csc_longitude"] != '' else None,            
                is_active = True if row["Status"] == "publish" else False
            )

            whatsapp = str(row["csc_whatsapp"])

            if whatsapp:
                if len(whatsapp) > 15:
                    whatsapp_list = whatsapp.split(',')
                    csc_center.whatsapp_number = whatsapp_list[0].strip()
                    if len(whatsapp_list) > 1 and not csc_center.mobile_number:
                        csc_center.mobile_number = whatsapp_list[1].strip()
                else:
                    csc_center.whatsapp_number = whatsapp.strip()
                csc_center.save()

            if row["Date"]:            
                try:
                    csc_center.created = datetime.strptime(row["Date"], "%d/%m/%Y %H:%M")
                    csc_center.save()
                except ValueError:
                    pass

                try:
                    csc_center.created = datetime.strptime(row["Date"], "%d-%m-%Y %H:%M")
                    csc_center.save()
                except ValueError:
                    pass

            current_services = row["Services"]
            if current_services and type(current_services) == str:
                services = current_services.split(',')
                for service in services:
                    service_name = service.strip()
                    service_obj, created = Service.objects.get_or_create(name = service_name)
                    csc_center.services.add(service_obj)
                    csc_center.save()
            
            current_username = row["Username"]
            if current_username and csc_center.email:
                user_obj = User.objects.filter(Q (username = current_username) | Q (email = csc_center.email)).exists()
                if not user_obj:
                    password = str(csc_center.contact_number) if csc_center.contact_number else "123456789"
                    user = User.objects.create_user(username = current_username, email = csc_center.email, phone = csc_center.contact_number, password = password)
                    user.email_verified = True
                    user.save()
        
        print(f"\rExecuted {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%", end="")

    print()
    return "Importing Completed!"

def restore():
    import_excel_data()
    print("Converting to integers. . .")
    convert_to_int()
    print("Replacing nan. . .")
    remove_nan()
    print("Removing trailing decimals in contact numbers. . .")
    remove_trailing_decimals()
    print("Creating dummy payments. . .")
    create_dummy_payments()

    generate_name_from_slug()

    print()

    return "Restoration Completed! You are all set."

def delete_and_restore():
    print("Deleting Data. . .")
    CscCenter.objects.all().delete()
    Service.objects.all().delete()
    Block.objects.all().delete()
    District.objects.all().delete
    State.objects.all().delete()
    print("Deleted Data!")

    import_excel_data()
    print("Converting to integers. . .")
    convert_to_int()
    print("Replacing nan. . .")
    remove_nan()
    print("Removing trailing decimals in contact numbers. . .")
    remove_trailing_decimals()
    print("Creating dummy payments. . .")
    create_dummy_payments()

    generate_name_from_slug()

    print()

    return "Restoration Completed! You are all set."


def import_mobile_numbers():
    csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')
    length = len(csv_data)  

    print("\nImporting mobile numbers . . .\n")

    for index, row in row_generator(csv_data):
        
        time.sleep(0.001)

        print(f"\rExecuted {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%", end="")

        try:
            csc_center = get_object_or_404(CscCenter, pk = f"CSC{row['ID']}")

            csc_center.mobile_number = row["csc_phonetwo"] if row["csc_phonetwo"] and row["csc_phonetwo"] != "nan" and row["csc_phonetwo"] != '' else csc_center.mobile_number
            csc_center.save()
        except Http404:
            continue
        except Exception as e:
            logger.exception(f"Error in importing mobile numbers from row id: {row['ID']}. Exception: {e}")
            continue

    print()
    return "Mobile Number Importing Completed!"


def set_user_phone():
    try:
        csc_centers = CscCenter.objects.all()
        length = len(csc_centers)
        for index, csc_center in enumerate(csc_centers, start=1):

            print(f"\rSetting phone number. Completed {int((index + 1) / length * 100)}%", end="")

            user_obj = User.objects.filter(email = csc_center.email)
            if user_obj.exists():
                user = user_obj.first()
                user.phone = csc_center.contact_number
                user.save()
        print()
        print("\nCompleted")
    except Exception as e:
        logger.exception(f"Error in setting user phone. Exception: {e}")


def generate_name_from_slug():
    try:
        csc_centers = CscCenter.objects.filter(name = "nan")
        to_update = []

        print()
        print("Genrating name from slug . . .")

        for csc_center in csc_centers:
            if csc_center.slug:
                name = csc_center.slug.replace("-", " ").title()
                csc_center.name = name

                to_update.append(csc_center)

        CscCenter.objects.bulk_update(to_update, ["name"])

        print()
        return "Name generation complete!"

    except Exception as e:
        logger.exception(f"Error in name center using slug. Exception: {e}")