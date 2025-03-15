from rest_framework import serializers
from .models import Nasabah, Admin, Setoran, PenukaranPoin

class NasabahSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nasabah
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'nama']

class SetoranSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setoran
        fields = ['id', 'nasabah', 'tanggal', 'berat', 'poin']

class PenukaranPoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['id', 'nasabah', 'tanggal', 'poin', 'status']
