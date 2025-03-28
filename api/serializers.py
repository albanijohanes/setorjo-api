from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Profile, PenukaranPoin

class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nama', 'no_hp', 'alamat', 'poin', 'reserved_poin', 'role']

class PenukaranPoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['id', 'jumlah_poin', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate_jumlah_poin(self, value):
        if value <= 0:
            raise serializers.ValidationError("Jumlah poin harus lebih dari 0")
            
        profile = self.context['request'].user.profile
        if value > profile.available_poin:
            raise serializers.ValidationError("Poin tersedia tidak mencukupi")
        return value

class AdminPenukaranPoinSerializer(serializers.ModelSerializer):
    nasabah = serializers.SerializerMethodField()
    
    class Meta:
        model = PenukaranPoin
        fields = '__all__'
    
    def get_nasabah(self, obj):
        return {
            'id': obj.nasabah.id,
            'nama': obj.nasabah.profile.nama,
            'email': obj.nasabah.email
        }