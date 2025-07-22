from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.db.models import Q, Avg
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import datetime, date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .models import (
    User, Tourist, Guide, Agency
)

from .serializers import (
     CustomTokenObtainPairSerializer, UserRegistrationSerializer,UserLoginSerializer, UserSerializer,
    TouristSerializer, GuideSerializer, GuideListSerializer, AgencySerializer,
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        # Get user from refresh token
        refresh_token = request.data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
            
            response_data = serializer.validated_data
            response_data['user'] = UserSerializer(user).data
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


# Authentication Views
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Add custom claims
            access['user_type'] = user.user_type
            access['username'] = user.username
            access['email'] = user.email
            
            return Response({
                'user': UserSerializer(user).data,
                'access': str(access),
                'refresh': str(refresh),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Add custom claims
            access['user_type'] = user.user_type
            access['username'] = user.username
            access['email'] = user.email
            
            return Response({
                'user': UserSerializer(user).data,
                'access': str(access),
                'refresh': str(refresh),
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_data = UserSerializer(request.user).data
        
        # Add profile-specific data based on user type
        if request.user.user_type == 'tourist':
            try:
                profile = TouristSerializer(request.user.tourist_profile).data
                user_data['profile'] = profile
            except:
                pass
        elif request.user.user_type == 'guide':
            try:
                profile = GuideSerializer(request.user.guide_profile).data
                user_data['profile'] = profile
            except:
                pass
        elif request.user.user_type == 'agency':
            try:
                profile = AgencySerializer(request.user.agency_profile).data
                user_data['profile'] = profile
            except:
                pass
        
        return Response(user_data, status=status.HTTP_200_OK)


# User Profile Views

# Destination Views
