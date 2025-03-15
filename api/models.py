from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class NasabahManager(BaseUserManager):
    def create_user(self, nama, no_rekening, jenis_kelamin, alamat, no_hp, password=None):
        if not no_rekening:
            raise ValueError('Nasabah must have a no_rekening')
        user = self.model(
            nama=nama,
            no_rekening=no_rekening,
            jenis_kelamin=jenis_kelamin,
            alamat=alamat,
            no_hp=no_hp,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class Nasabah(AbstractBaseUser):
    nama = models.CharField(max_length=255)
    poin = models.IntegerField(default=0)
    no_rekening = models.CharField(max_length=20, unique=True)
    jenis_kelamin = models.CharField(max_length=10)
    alamat = models.TextField()
    no_hp = models.CharField(max_length=15)
    password = models.CharField(max_length=128)

    objects = NasabahManager()

    USERNAME_FIELD = 'no_rekening'
    REQUIRED_FIELDS = ['nama', 'jenis_kelamin', 'alamat', 'no_hp']

    def __str__(self):
        return self.nama

class Admin(AbstractBaseUser):
    nama = models.CharField(max_length=255)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'nama'

    def __str__(self):
        return self.nama

class Setoran(models.Model):
    nasabah = models.ForeignKey(Nasabah, on_delete=models.CASCADE)
    tanggal = models.DateTimeField(auto_now_add=True)
    berat = models.FloatField()
    poin = models.IntegerField()

class PenukaranPoin(models.Model):
    nasabah = models.ForeignKey(Nasabah, on_delete=models.CASCADE)
    tanggal = models.DateTimeField(auto_now_add=True)
    poin = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
