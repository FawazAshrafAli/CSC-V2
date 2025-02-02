from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View, UpdateView, TemplateView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import Http404, JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from random import randint
import logging

from .models import User, UserOtp
from home.views import BaseHomeView
from .models import EmailVerificationOtp
from csc_center.models import CscCenter

from .tasks import send_otp_email, send_verification_otp

logger = logging.getLogger(__name__)
class AuthenticationView(BaseHomeView, TemplateView):
    template_name = 'authentication/login.html'
    admin_success_url = reverse_lazy('csc_admin:home')
    user_success_url = reverse_lazy('users:home')
    redirect_url = reverse_lazy('authentication:login')

    def get_context_date(sekf, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:         
                if request.user.is_superuser:
                    return redirect(self.admin_success_url)
                else:
                    return redirect(self.user_success_url)
            
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Some error occured: {e}")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me')

            if username and password:
                user = authenticate(request, username = username, password = password)
                if user is None:
                    user_list = User.objects.filter(Q(email = username) | Q(phone = username))
                    user_list.exists()
                    user_obj = user_list.first()
                    if user_obj and user_obj.check_password(password):
                        user = user_obj                    
                if user is not None:
                    login(request, user) 
                    if user.is_superuser:
                        if remember_me:
                            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                        else:
                            request.session.set_expiry(0) 

                    if user.is_superuser:                        
                        return redirect(self.admin_success_url)                    
                    else:                        
                        return redirect(reverse_lazy('authentication:login'))
                else:
                    messages.error(request, 'Invalid Credentials.')
                    
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Some error occured: {e}")
            return redirect(self.redirect_url)


class LogoutView(View):
    success_url = reverse_lazy('home:view')
    
    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                logout(request)
                return redirect(self.success_url)
            else:
                return redirect(reverse_lazy('authentication:login'))
        except Exception:
            logger.exception("Some error occured")
            return redirect(self.redirect_url)

class ResetPasswordWithOtpView(BaseHomeView, UpdateView):
    model = User
    fields = ['password']
    template_name = 'authentication/forgot_password.html'
    success_url = reverse_lazy('authentication:login')
    pk_url_kwarg = 'email'
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(self.model, email = self.kwargs.get('email'))
        except Exception:
            logger.exception("Error in fetching user")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['email'] = self.kwargs.get('email')
            return context
        except Exception:
            logger.exception("Error in fetching context data for sending otp")
            return {}
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            try:            
                user_otp = get_object_or_404(UserOtp, user = self.object)
            except Http404:
                messages.error(request, 'No otp has been generated for your account')
                return redirect(self.redirect_url)

            otp = request.POST.get('otp')
            password = request.POST.get('password')
            repeat_password = request.POST.get('repeat_password')

            if user_otp.otp != otp:
                messages.error(request, "Invalid OTP")
                return redirect(self.redirect_url)

            if timezone.now() > user_otp.updated + timedelta(minutes=5):
                messages.error(request, "Expired OTP.")
                return redirect(self.redirect_url)
            
            if password != repeat_password:
                messages.error(request, "Password not matching.")
                return redirect(self.redirect_url)
            
            self.object.set_password(password)
            self.object.save()

            user_otp.delete()
            messages.success(request, "Successfully resetted password")
            return redirect(self.get_success_url())
        except Exception:
            logger.exception("Error in resetting password")
            return redirect(self.redirect_url)


class ForgotPasswordView(View):
    redirect_url = reverse_lazy('authentication:login')
    success_url = reverse_lazy('authentication:reset_password_with_otp')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            email = self.request.POST.get('email')
            context['email'] = email
            return context
        except Exception:
            logger.exception("Error in getting context data")
            return {}
    

    def post(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email')
            user = None

            try:
                user = get_object_or_404(User, email = email)
            except Http404:
                pass

            if not email:
                messages.warning(request, "Please provide your email id.")
                return redirect(self.redirect_url)

            if not User.objects.filter(email = email).exists():
                messages.error(request, "Invalid Email Id")
                return redirect(self.redirect_url)

            otp = get_random_string(length=6, allowed_chars='1234567890')

            UserOtp.objects.update_or_create(user = user, defaults={'otp': otp})

            send_otp_email.delay(email, otp)

            messages.success(request, "OTP has been sent to your email.")
            return redirect(reverse('authentication:reset_password_with_otp', kwargs={'email': email}))

        except Exception:
            logger.exception("Error in forgot password view")
            return redirect(self.redirect_url)


class UserRegistrationView(BaseHomeView, CreateView):
    model = User
    fields = ["username", "email", "password"]
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('users:home')
    redirect_url = reverse_lazy('authentication:login')

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['email'] = self.kwargs.get('email')
            return context
        except Exception:
            logger.exception("Error in getting context data")
            return {}

    def get(self, request, *args, **kwargs):
        try:            
            email = self.kwargs.get('email')
            if not CscCenter.objects.filter(email = email, status = "Approved").exists():
                messages.error(request, "Invalid Link")
                return redirect(self.redirect_url)

            if email and self.model.objects.filter(email = email).exists():
                if request.user.is_authenticated:
                    logout(request)

                user = User.objects.get(email = email)
                login(request, user)

                return redirect(self.success_url)            
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in getting user request in UserRegistrationView: {e}")
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            email = self.kwargs.get('email')
            password = request.POST.get("password")
            repeat_password = request.POST.get("repeat_password")

            if password != repeat_password:
                messages.error(request, "Passwords are not matching.")
                return super().get(request, *args, **kwargs)

            new_user = self.model.objects.create_user(username = email, email=email, password=password)            
            new_user.save()

            if request.user.is_authenticated:
                logout(request)            

            user = authenticate(request, username = new_user.username, password = password)
            login(request, user)                  
            messages.success(request, "Account creation successfull.")       
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in user registration: {e}")
            return redirect(self.redirect_url)
    

def call_email_verification_mail(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)
        
        if "@" not in email or "." not in email:
            return JsonResponse({"error": "Invalid email format"}, status=400)
        
        if CscCenter.objects.filter(email = email.strip()).exists():
            return JsonResponse({"error": "duplicate"})
        
        otp_number = randint(100000, 999999)

        otp_obj, created = EmailVerificationOtp.objects.update_or_create(
            email=email,
            defaults={"otp": otp_number}
        )

        send_verification_otp.delay(otp_obj.otp, email)

        return JsonResponse({"status": "success"}, status=200)
    
    except Exception as e:
        logger.exception(f"Error sending OTP for email verification: {e}")
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
def verify_email_with_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        inputted_otp = request.POST.get("otp")
        email = request.POST.get("email")
        
        if not inputted_otp or not email:
            return JsonResponse({"error": "OTP and email are required"}, status=400)
        
        otp_obj = EmailVerificationOtp.objects.filter(otp=inputted_otp, email=email).first()
        if otp_obj:
            if timezone.now() < otp_obj.updated + timedelta(minutes=5):                
                return JsonResponse({"status": "success"}, status=200)
            else:
                return JsonResponse({"error": "OTP expired"}, status=400)
        else:
            return JsonResponse({"error": "Invalid OTP"}, status=400)
    
    except Exception as e:
        logger.exception(f"Error verifying OTP for email: {e}")
        return JsonResponse({"error": f"An error occurred: {e}"}, status=500)
                

