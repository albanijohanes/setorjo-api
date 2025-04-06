from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile, PenukaranPoin
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import (
  CustomAuthTokenSerializer, 
  PenukaranPoinSerializer, 
  ProfileSerializer, 
  PointAdditionSerializer, 
  PenukaranStatusSerializer
  )

class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'nama': user.profile.nama,
            'role': user.profile.role
        })

@api_view(['POST'])
def register_nasabah(request):
    data = request.data
    required_fields = ['nama', 'email', 'password', 'no_hp', 'alamat']
    
    for field in required_fields:
        if field not in data:
            return Response({'error': f'{field} diperlukan'}, status=400)
    
    if User.objects.filter(username=data['email']).exists():
        return Response({'error': 'Email sudah terdaftar'}, status=400)
    
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password']
            )
            
            Profile.objects.create(
                user=user,
                nama=data['nama'],
                no_hp=data['no_hp'],
                alamat=data['alamat'],
                role='nasabah'
            )
            
            return Response({'message': 'Registrasi berhasil'}, status=201)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    profile = user.profile
    return Response({
        'nama': profile.nama,
        'email': user.email,
        'no_hp': profile.no_hp,
        'alamat': profile.alamat,
        'poin': profile.poin,
        'role': profile.role
    })

class is_nasabah(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'nasabah'

class is_admin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'admin'

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    profile = user.profile
    return Response({
        'nama': profile.nama,
        'email': user.email,
        'no_hp': profile.no_hp,
        'alamat': profile.alamat,
        'total_poin': profile.poin,
        'available_poin': profile.available_poin,
        'reserved_poin': profile.reserved_poin,
        'role': profile.role
    })
# Nasabah Endpoints
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_nasabah])
def create_penukaran(request):
    serializer = PenukaranPoinSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        with transaction.atomic():
            penukaran = serializer.save(nasabah=request.user)
            # Reserve poin
            request.user.profile.reserved_poin += penukaran.jumlah_poin
            request.user.profile.save()
            return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_nasabah])
def history_penukaran(request):
    penukaran = PenukaranPoin.objects.filter(nasabah=request.user)
    serializer = PenukaranPoinSerializer(penukaran, many=True)
    return Response(serializer.data)

# Admin Endpoints
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def add_points(request):
    serializer = PointAdditionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                nasabah = serializer.validated_data['nasabah']
                
                # Validasi role nasabah
                if nasabah.profile.role != 'nasabah':
                    return Response(
                        {'error': 'Hanya bisa menambahkan poin untuk nasabah'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Simpan transaksi
                instance = serializer.save(admin=request.user)
                
                # Update poin nasabah SEKALI SAJA
                nasabah.profile.poin += instance.points
                nasabah.profile.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def list_nasabah(request):
    nasabah = Profile.objects.filter(role='nasabah')
    serializer = ProfileSerializer(nasabah, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def update_penukaran_status(request, pk):
    try:
        penukaran = PenukaranPoin.objects.get(pk=pk)
    except PenukaranPoin.DoesNotExist:
        return Response(status=404)
    
    serializer = PenukaranStatusSerializer(penukaran, data=request.data, partial=True)
    if serializer.is_valid():
        with transaction.atomic():
            profile = penukaran.nasabah.profile
            
            if serializer.validated_data['status'] == 'approved':
                profile.poin -= penukaran.jumlah_poin
            
            if penukaran.status == 'pending':
                profile.reserved_poin -= penukaran.jumlah_poin
            
            profile.save()
            serializer.save()
            return Response(serializer.data)
    return Response(serializer.errors, status=400)