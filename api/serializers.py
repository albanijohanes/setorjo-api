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

class PenukaranPoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['id', 'jumlah_poin', 'status', 'created_at', 'updated_at']

class AdminPenukaranPoinSerializer(serializers.ModelSerializer):
    nasabah = serializers.StringRelatedField()
    
    class Meta:
        model = PenukaranPoin
        fields = '__all__'

class NasabahPoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['poin']