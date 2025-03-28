"""
URL configuration for setorjoapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# urls.py
from django.urls import path, include
from django.contrib import admin
from api.views import (
    CustomAuthToken,
    register_nasabah,
    get_profile,
    create_penukaran,
    admin_list_penukaran,
    update_penukaran_status,
    admin_list_nasabah,
    admin_nasabah_detail
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/login/', CustomAuthToken.as_view(), name='api-login'),
    path('api/register/', register_nasabah, name='api-register'),
    
    # Profile
    path('api/profile/', get_profile, name='api-profile'),
    
    # Nasabah Endpoints
    path('api/nasabah/penukaran/', create_penukaran, name='create-penukaran'),
    
    # Admin Endpoints
    path('api/admin/penukaran/', admin_list_penukaran, name='admin-list-penukaran'),
    path('api/admin/penukaran/<int:pk>/', update_penukaran_status, name='update-penukaran'),
    path('api/admin/nasabah/', admin_list_nasabah, name='admin-list-nasabah'),
    path('api/admin/nasabah/<int:pk>/', admin_nasabah_detail, name='admin-nasabah-detail'),
]