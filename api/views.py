from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile
from .serializers import CustomAuthTokenSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Cek role nasabah
        if not hasattr(user, 'profile') or user.profile.role != 'nasabah':
            return Response({'error': 'Akses untuk nasabah saja'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
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
            role='nasabah'
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