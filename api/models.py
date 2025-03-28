from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('nasabah', 'Nasabah'),
        ('admin', 'Admin')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    no_hp = models.CharField(max_length=15)
    alamat = models.TextField()
    poin = models.IntegerField(default=0)
    reserved_poin = models.IntegerField(default=0)  # Poin yang sedang dalam proses penukaran
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='nasabah')

    @property
    def available_poin(self):
        return self.poin - self.reserved_poin

    def __str__(self):
        return self.nama

class PenukaranPoin(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak')
    ]
    
    nasabah = models.ForeignKey(User, on_delete=models.CASCADE, related_name='penukaran_poin')
    jumlah_poin = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nasabah.profile.nama} - {self.jumlah_poin} poin"