from django.urls import path

from auth_app.api.views import RegistrationView, LoginView, LogoutView, UserProfileView, EmailCheckView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]