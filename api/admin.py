from django.contrib import admin
from .models import Nasabah, Admin as AdminModel

admin.site.register(Nasabah)
admin.site.register(AdminModel)