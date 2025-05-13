# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication views provided by Django
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), # Redirect to home page after logout

    # Custom views
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    # New URL pattern for the user profile page
    path('profile/', views.user_profile_view, name='user_profile'),
]
