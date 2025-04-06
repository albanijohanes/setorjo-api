from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Profile, PenukaranPoin, PointAddition

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
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate_jumlah_poin(self, value):
        if value <= 0:
            raise serializers.ValidationError("Jumlah poin harus lebih dari 0")
        if value > self.context['request'].user.profile.available_poin:
            raise serializers.ValidationError("Poin tersedia tidak mencukupi")
        return value

class PointAdditionSerializer(serializers.ModelSerializer):
    nasabah = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__role='nasabah'),
        error_messages={'does_not_exist': 'User bukan nasabah atau tidak ditemukan'}
    )
    
    class Meta:
        model = PointAddition
        fields = ['id', 'nasabah', 'weight_grams', 'points', 'created_at']
        read_only_fields = ['points', 'admin', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'nama', 'no_hp', 'alamat', 'poin', 'role']
        read_only_fields = ['poin', 'role']

class PenukaranStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenukaranPoin
        fields = ['status']