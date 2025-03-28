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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from api.views import (CustomAuthToken, 
                       register_nasabah, 
                       get_profile,
                       nasabah_poin, 
                       penukaran_poin, 
                       admin_list_nasabah, 
                       admin_list_penukaran, 
                       admin_nasabah_detail, 
                       admin_penukaran_detail
                       )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', CustomAuthToken.as_view(), name='api-login'),
    path('api/create/', register_nasabah, name='api-register'),
    path('api/profile/', get_profile, name='api-profile'),

    # Nasabah Endpoints
    path('api/nasabah/poin/', nasabah_poin, name='nasabah-poin'),
    path('api/nasabah/penukaran/', penukaran_poin, name='penukaran-poin'),
    
    # Admin Endpoints
    path('api/admin/penukaran/', admin_list_penukaran, name='admin-list-penukaran'),
    path('api/admin/penukaran/<int:pk>/', admin_penukaran_detail, name='admin-penukaran-detail'),
    path('api/admin/nasabah/', admin_list_nasabah, name='admin-list-nasabah'),
    path('api/admin/nasabah/<int:pk>/', admin_nasabah_detail, name='admin-nasabah-detail'),
]