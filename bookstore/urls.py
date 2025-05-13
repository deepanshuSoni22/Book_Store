"""
URL configuration for bookstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Remove the import for TemplateView as we are using a custom view now
# from django.views.generic import TemplateView

# Import the new home_redirect_view from your books app's views
from books.views import home_redirect_view # Assuming it's in books/views.py


urlpatterns = [
    path('admin/', admin.site.urls),
    # Use the new home_redirect_view for the root path
    path('', home_redirect_view, name='home_page'),
    # Keep the include for books.urls, but it will now handle paths other than the root
    path('books/', include('books.urls')), # Changed to 'books/' to avoid conflict with root
    path('accounts/', include('accounts.urls')), # Add this
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # if you use STATIC_ROOT for dev

