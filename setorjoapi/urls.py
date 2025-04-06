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
    update_penukaran_status,
    history_penukaran,
    add_points,
    list_nasabah
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
    path('api/nasabah/history/', history_penukaran, name='history-penukaran'),
    
    # Admin Endpoints
    path('api/admin/points/', add_points, name='add-points'),
    path('api/admin/nasabah/', list_nasabah, name='list-nasabah'),
    path('api/admin/penukaran/<int:pk>/', update_penukaran_status, name='update-penukaran'),
    path('api/admin/register-nasabah/', register_nasabah, name='register-nasabah'),

]