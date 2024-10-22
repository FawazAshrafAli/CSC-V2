from django.urls import path
from .views import AuthenticationView, LogoutView, ForgotPasswordView, ResetPasswordWithOtpView, UserRegistrationView, VerifyEamilAddressView

app_name = "authentication"

urlpatterns = [
    path('', AuthenticationView.as_view(), name = 'login'),
    path('user_registration/<str:email>', UserRegistrationView.as_view(), name = 'user_registration'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('reset_password_with_otp/<str:email>', ResetPasswordWithOtpView.as_view(), name = 'reset_password_with_otp'),
    path('forgot_password/', ForgotPasswordView.as_view(), name = 'forgot_password'),
    path('verify_email/<str:token>/', VerifyEamilAddressView.as_view(), name='verify_email'),
]
