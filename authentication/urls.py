from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ForgotPasswordView, VerifyOTPView, ResetPasswordView
urlpatterns = [
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name = 'forgot-pass'),
    path('verfiy-otp/', VerifyOTPView.as_view(), name = 'verify-otp'),
    path('reset-pass/', ResetPasswordView.as_view(), name = 'reset-pass'),
]

