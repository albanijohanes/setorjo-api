# filepath: c:\laragon\www\djangoapi\setorjoapi\api\views.py
from rest_framework import viewsets, permissions
from .models import Nasabah, Admin, Setoran, PenukaranPoin
from .serializers import NasabahSerializer, AdminSerializer, SetoranSerializer, PenukaranPoinSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

class NasabahViewSet(viewsets.ModelViewSet):
    queryset = Nasabah.objects.all()
    serializer_class = NasabahSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Nasabah.objects.all()
        return Nasabah.objects.all()  # Ubah ini untuk sementara waktu untuk memastikan tidak ada filter

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAdminUser]

class SetoranViewSet(viewsets.ModelViewSet):
    queryset = Setoran.objects.all()
    serializer_class = SetoranSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Setoran.objects.all()
        return Setoran.objects.filter(nasabah=self.request.user)

class PenukaranPoinViewSet(viewsets.ModelViewSet):
    queryset = PenukaranPoin.objects.all()
    serializer_class = PenukaranPoinSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PenukaranPoin.objects.all()
        return PenukaranPoin.objects.filter(nasabah=self.request.user)

class LoginView(APIView):
    def post(self, request):
        no_rekening = request.data.get('no_rekening')
        password = request.data.get('password')
        user = authenticate(username=no_rekening, password=password)  # Use no_rekening as username
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=400)