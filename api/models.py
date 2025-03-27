from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [('nasabah', 'Nasabah')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    no_hp = models.CharField(max_length=15)
    alamat = models.TextField()
    poin = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='nasabah')

    def __str__(self):
        return self.nama