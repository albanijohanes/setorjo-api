from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile, PenukaranPoin
from .serializers import CustomAuthTokenSerializer, PenukaranPoinSerializer, AdminPenukaranPoinSerializer, ProfileSerializer
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission

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
    required_fields = ['nama', 'email', 'password', 'no_hp', 'alamat', 'role']
    
    for field in required_fields:
        if field not in data:
            return Response({'error': f'{field} diperlukan'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    email = data['email']
    if User.objects.filter(username=email).exists():
        return Response({'error': 'Email sudah terdaftar'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=data['password']
        )
        Profile.objects.create(
            user=user,
            nama=data['nama'],
            no_hp=data['no_hp'],
            alamat=data['alamat'],
            poin=0,
            role=data['role']
        )
    except Exception as e:
        return Response({'error': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'message': 'Registrasi berhasil'}, 
                  status=status.HTTP_201_CREATED)

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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_nasabah])
def create_penukaran(request):
    serializer = PenukaranPoinSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            profile = request.user.profile
            jumlah_poin = serializer.validated_data['jumlah_poin']
            
            # Buat penukaran
            penukaran = PenukaranPoin.objects.create(
                nasabah=request.user,
                jumlah_poin=jumlah_poin
            )
            
            # Update reserved poin
            profile.reserved_poin += jumlah_poin
            profile.save()
            
            return Response(
                PenukaranPoinSerializer(penukaran).data,
                status=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def update_penukaran_status(request, pk):
    try:
        penukaran = PenukaranPoin.objects.get(pk=pk)
    except PenukaranPoin.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    
    if new_status not in ['approved', 'rejected']:
        return Response(
            {'error': 'Status tidak valid'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            profile = penukaran.nasabah.profile
            
            if new_status == 'approved':
                # Kurangi poin aktual
                profile.poin -= penukaran.jumlah_poin
            
            # Kurangi reserved poin
            profile.reserved_poin -= penukaran.jumlah_poin
            profile.save()
            
            # Update status penukaran
            penukaran.status = new_status
            penukaran.save()
            
            return Response(AdminPenukaranPoinSerializer(penukaran).data)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def admin_list_penukaran(request):
    penukaran = PenukaranPoin.objects.all()
    serializer = AdminPenukaranPoinSerializer(penukaran, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def admin_nasabah_detail(request, pk):
    try:
        profile = Profile.objects.get(pk=pk, role='nasabah')
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        delta_poin = request.data.get('poin', 0)
        
        try:
            delta_poin = int(delta_poin)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Nilai poin tidak valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile.poin += delta_poin
        profile.save()
        return Response(ProfileSerializer(profile).data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, is_admin])
def admin_list_nasabah(request):
    nasabah = Profile.objects.filter(role='nasabah')
    serializer = ProfileSerializer(nasabah, many=True)
    return Response(serializer.data)