from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile, PenukaranPoin
from .serializers import CustomAuthTokenSerializer, PenukaranPoinSerializer, AdminPenukaranPoinSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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

def is_nasabah(user):
    return user.profile.role == 'nasabah'

def is_admin(user):
    return user.profile.role == 'admin'

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def nasabah_poin(request):
    """Get poin nasabah"""
    if not is_nasabah(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    profile = request.user.profile
    return Response({'poin': profile.poin})

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def penukaran_poin(request):
    """Create/get penukaran poin (nasabah)"""
    if not is_nasabah(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        penukaran = PenukaranPoin.objects.filter(nasabah=request.user)
        serializer = PenukaranPoinSerializer(penukaran, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Cek poin cukup
        if request.user.profile.poin < request.data.get('jumlah_poin', 0):
            return Response(
                {'error': 'Poin tidak mencukupi'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PenukaranPoinSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(nasabah=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_penukaran_detail(request, pk):
    """Admin: Get/update penukaran poin"""
    if not is_admin(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        penukaran = PenukaranPoin.objects.get(pk=pk)
    except PenukaranPoin.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AdminPenukaranPoinSerializer(penukaran)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        new_status = request.data.get('status')
        old_status = penukaran.status
        
        serializer = AdminPenukaranPoinSerializer(penukaran, data=request.data, partial=True)
        if serializer.is_valid():
            # Jika status berubah ke approved
            if new_status == 'approved' and old_status != 'approved':
                # Kurangi poin nasabah
                nasabah_profile = penukaran.nasabah.profile
                nasabah_profile.poin -= penukaran.jumlah_poin
                nasabah_profile.save()
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_list_penukaran(request):
    """Admin: List semua permintaan penukaran"""
    if not is_admin(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    penukaran = PenukaranPoin.objects.all()
    serializer = AdminPenukaranPoinSerializer(penukaran, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_nasabah_detail(request, pk):
    """Admin: Get/update poin nasabah"""
    if not is_admin(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        profile = Profile.objects.get(pk=pk, role='nasabah')
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PenukaranPoinSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        delta_poin = request.data.get('poin', 0)
        
        try:
            delta_poin = int(delta_poin)
        except ValueError:
            return Response(
                {'error': 'Nilai poin tidak valid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile.poin += delta_poin
        profile.save()
        return Response({'poin': profile.poin})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_list_nasabah(request):
    """Admin: List semua nasabah"""
    if not is_admin(request.user):
        return Response({'error': 'Akses ditolak'}, status=status.HTTP_403_FORBIDDEN)
    
    nasabah = Profile.objects.filter(role='nasabah')
    serializer = PenukaranPoinSerializer(nasabah, many=True)
    return Response(serializer.data)