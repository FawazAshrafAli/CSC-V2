from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from math import ceil, floor
from django.http import Http404, JsonResponse
from django.db.models import Q, F
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify
import logging
import uuid
import time
import sys

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

            if CscCenter.objects.filter(email = email).exists():
                messages.error(request, "CSC center with the same email already exists. Please try again with another email.")
                return redirect(self.redirect_url)

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
                street = street.strip() if street else None, logo = logo, description = description.strip() if description else None, contact_number = contact_number.strip() if contact_number else None,
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
            self.object.next_payment_date = self.object.created.date()
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

            messages.success(request, "Added CSC center. Once the csc center is approved we will notify you via email.")

            if not User.objects.filter(email = email).exists():
                logout(request)                
                return redirect(self.redirect_url)
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
        

class RemoveCscCenterBannerView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get_object(self):
        try:
            return get_object_or_404(CscCenter, slug = self.kwargs.get('slug'))
        except Http404:
            logger.error("CSC center not found when removing csc center banner. status = 404")
        except Exception as e:
            logger.exception(f"Error in fetching the object in remove csc center banner view: {e}")
        
        return None

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get("x-requested-with") != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            self.object = self.get_object()
            if not self.object:            
                return JsonResponse({"status": "failed", "error": "CSC not found"}, status=404)

            self.object.banners.clear()

            return JsonResponse({"status": "success"}, status=200)
            
        except Exception as e:
            logger.exception(f"Error in removing csc center banner: {e}")
            return JsonResponse({"status": "failed", "error": "An unexpected error occured."}, status=500)

                    


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


def success(msg):
    GREEN = "\033[92m"
    RESET = "\033[0m"

    sys.stdout.write(f"{GREEN}\n{msg}\n{RESET}")

def error(msg):
    RED = "\033[91m"
    RESET = "\033[0m"

    sys.stdout.write(f"{RED}\n{msg}\n{RESET}")



def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        # if index >= 4999:
        yield index, row

def import_excel_data():
    csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')
    length = len(csv_data)  

    success("Importing data . . .")
    
    for index, row in row_generator(csv_data):
        
        time.sleep(0.001)

        current_state = str(row['cs_state']) if row['cs_state'] else None
        state, created =  State.objects.get_or_create(state = current_state.strip())

        current_district = str(row['cs_district']) if row['cs_district'] else None
        district, created =  District.objects.get_or_create(district = current_district.strip(), state = state)

        current_block = str(row['cs_block']) if row['cs_block'] else None
        block, created =  Block.objects.get_or_create(block = current_block.strip(), state = state, district = district)
 
        if not CscCenter.objects.filter(id = f"CSC{row['ID']}").exists():
            contact_number = str(row["csc_phone"]).split(',') if row["csc_phone"] and pd.notna(row["csc_phone"]) else None
            if contact_number is not None:
                contact_number = contact_number[0]
                contact_number = int(float(contact_number))

            mobile_number = str(row["csc_phonetwo"]).split(',') if row["csc_phonetwo"] and pd.notna(row["csc_phonetwo"]) else None
            if mobile_number is not None:
                mobile_number = mobile_number[0]
                mobile_number = mobile_number.replace("+91", "").replace("'", "")                
                try:
                    mobile_number = int(float(mobile_number))
                except ValueError:
                    mobile_number = None

            if not contact_number and mobile_number:
                contact_number = mobile_number

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
                email = str(row.get("csc_email") if pd.notna(row.get("csc_email")) else row.get("CSC Email") if pd.notna(row.get("CSC Email")) else None),
                contact_number = contact_number,
                mobile_number = mobile_number,
                show_opening_hours = False, 
                show_social_media_links = False,
                latitude = row["csc_latitude"] if row["csc_latitude"] and len(str(row["csc_latitude"])) < 100 and row["csc_latitude"] != "nan" and row["csc_latitude"] != '' else None,
                longitude = row["csc_longitude"] if row["csc_longitude"] and len(str(row["csc_longitude"])) < 100 and row["csc_longitude"] != "nan" and row["csc_longitude"] != '' else None,            
                is_active = True,
                status = "Approved",
                approved_date = timezone.now()
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
                    naive_datetime = datetime.strptime(row["Date"], "%d/%m/%Y %H:%M")
                    aware_datetime = timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())
                    csc_center.created = aware_datetime
                    csc_center.save()
                except ValueError:
                    pass

                try:
                    naive_datetime = datetime.strptime(row["Date"], "%d-%m-%Y %H:%M")
                    aware_datetime = timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())
                    csc_center.created = aware_datetime
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
    
    success("Importing Completed!")

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


def success(msg):
    GREEN = "\033[92m"
    RESET = "\033[0m"

    sys.stdout.write(f"{GREEN}\n{msg}\n{RESET}")

def error(msg):
    RED = "\033[91m"
    RESET = "\033[0m"

    sys.stdout.write(f"{RED}\n{msg}\n{RESET}")

def activate_and_delete_dummy_payments():
    try:
        csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')        

        sys.stdout.write(f"\nActivating and deleting dummy payments . . .\n")    

        csv_center_ids = [f"CSC{row['ID']}" for _, row in csv_data.iterrows()]

        last_paid_date = timezone.datetime(2023, 12, 31, tzinfo=timezone.get_current_timezone()).date()
        
        activated_count = CscCenter.objects.filter(pk__in=csv_center_ids).update(is_active=True, status="Approved", approved_date = F('created'), last_paid_date = last_paid_date)

        success(f"Activated {activated_count} CSC inactive centers")

        payments = Payment.objects.filter(csc_center__pk__in = csv_center_ids)
        payment_count = payments.count()
        payments.delete()
        
        success(f"Deleted {payment_count} dummy payments")

        success(f"All Done!")
    except Exception as e:
        error(f"Error in activating csc centers and destroying dummy payments: \n{e}")

def create_users():
    try:
        csv_data = pd.read_csv(r'/home/shidevr1/cscindia/static/w3/admin_csc_center/documents/csc-centers.csv')                                

        to_create = []

        for index, row in row_generator(csv_data):
            email = row.get("csc_email") if pd.notna(row.get("csc_email")) else row.get("CSC Email") if pd.notna(row.get("CSC Email")) else None

            if email:
                username = str(row["Username"])

                if User.objects.filter(username = username).exists() or username.isdecimal():
                    username = email                

                contact_number = str(row["csc_phone"]).split(',') if row["csc_phone"] and pd.notna(row["csc_phone"]) else None
                if contact_number is not None:
                    contact_number = contact_number[0]
                    contact_number = int(float(contact_number))

                password = str(contact_number) if contact_number else "12345678"

                if not User.objects.filter(Q(email = email) | Q(username = email) | Q(username = username)).exists():
                    to_create.append({
                        "username": username,
                        "email": email,
                        "password": password
                        })
            
        sys.stdout.write(f"\nQued the creating user details")
                
        for _ in to_create:
            username = _["username"]
            email = _["email"]
            password = _["password"]

            if not User.objects.filter(Q(email = email) | Q(username = email) | Q(username = username)).exists():

                User.objects.create_user(username = username, email = email, password = password)
                sys.stdout.write(f"\nCreated user account for {email}.")  

        print("\nUser creation process completed successfully.")

    except Exception as e:
        logger.exception(f"Error in creating user: {e}")

            
def verify_emails():
    try:
        csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')        

        sys.stdout.write(f"\nVerify emails . . .\n")    

        csv_center_emails = [str(row['csc_email']) for _, row in csv_data.iterrows()]

        User.objects.filter(email__in=csv_center_emails).update(email_verified = True)

        success(f"Verified emails of csv file.")

        success(f"All Done!")
    except Exception as e:
        error(f"Error in verifying: \n{e}")


def activate_csc_centers():
    try:
        csv_data = pd.read_csv(r'/home/shidevr1/cscindia/static/w3/admin_csc_center/documents/csc-centers.csv')

        sys.stdout.write(f"\nActivating . . .\n")    

        csv_center_ids = [f"CSC{row['ID']}" for _, row in csv_data.iterrows()]

        CscCenter.objects.filter(pk__in = csv_center_ids).update(is_active = True)

        success(f"CSC center activation: Complete!")

        success(f"All Done!")
    except Exception as e:
        error(f"Error in activating csc centers: \n{e}")

def update_csc_centers():
    centers = CscCenter.objects.filter(email = "None")

    csv_data = pd.read_csv(r'/home/shidevr1/cscindia/static/w3/admin_csc_center/documents/csc-centers.csv')

    for index, row in row_generator(csv_data):
        center = centers.filter(pk = f"CSC{row['ID']}").first()
        email = row.get("csc_email") if pd.notna(row.get("csc_email")) else row.get("CSC Email") if pd.notna(row.get("CSC Email")) else None

        if center and email:
            center.email = email
            center.save()

            sys.stdout.write(f"\nEmail updated for {email}")

    success(f"All Done!")


from django.db import transaction

def convert_to_lowercase_email():
    users = User.objects.filter(email__regex=r'[A-Z]')
    csc_centers = CscCenter.objects.filter(email__regex=r'[A-Z]')
    
    if not users.exists():
        logger.info("No users with uppercase letters in email found.")
    if not csc_centers.exists():
        logger.info("No CSC centers with uppercase letters in email found.")

    if not users.exists() and not csc_centers.exists():
        return

    try:
        with transaction.atomic():
            if users.exists():
                for user in users:
                    user.email = user.email.lower()
                User.objects.bulk_update(users, ["email"])
                logger.info(f"Successfully updated {len(users)} user emails to lowercase.")
            
            if csc_centers.exists():
                for csc_center in csc_centers:
                    csc_center.email = csc_center.email.lower()
                CscCenter.objects.bulk_update(csc_centers, ["email"])
                logger.info(f"Successfully updated {len(csc_centers)} CSC center emails to lowercase.")
    
    except Exception as e:
        logger.error(f"Error occurred while updating emails: {str(e)}")
        raise


def update_center_slug():
    sys.stdout.write("\nUpdating slugs of CSC centers . . .\n")

    csc_centers = CscCenter.objects.filter(name__isnull = False)
    existing_slugs = set(CscCenter.objects.values_list("slug", flat=True))

    new_slugs = []

    updating_centers = []

    for center in csc_centers:
        new_slug_parts = [center.name]

        if center.type:
            new_slug_parts.append(center.type.type)

        if center.block:
            new_slug_parts.append(center.block.block)

        if center.district:
            new_slug_parts.append(center.district.district)

        if center.state:
            new_slug_parts.append(center.state.state)

        new_slug = "-".join(new_slug_parts)

        base_slug = slugify(new_slug)
        slug = base_slug

        count = 1

        while slug in existing_slugs or slug in new_slugs:
            slug = f"{base_slug}-{count}"
            count += 1

        center.slug = slug
        
        new_slugs.append(slug)

        updating_centers.append(center)

    CscCenter.objects.bulk_update(updating_centers, ["slug"])

    success("CSC Center slug updation: Completed!\n")
    

def set_slug():
    # csv_data = pd.read_csv(r'/home/shidevr1/cscindia/static/w3/admin_csc_center/documents/csc-centers.csv')
    csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv') 

    sys.stdout.write("\nFunction Called . . .\n")

    centers_to_update = []
    with transaction.atomic():
        for _, row in csv_data.iterrows():
            id = f"CSC{row['ID']}"    
            slug = row["Slug"] if pd.notna(row["Slug"]) and row["Slug"].strip() != "" else None

            try:
                center = CscCenter.objects.get(id=id)
                if center.slug != slug:
                    center.slug = slug
                    centers_to_update.append(center)

                    sys.stdout.write(f"Center '{center.name}' qued for updation")
            except CscCenter.DoesNotExist:                
                error(f"Center with ID {id} does not exist.")

    if centers_to_update:
        CscCenter.objects.bulk_update(centers_to_update, ["slug"])

    success(f"\nCompleted!\n")