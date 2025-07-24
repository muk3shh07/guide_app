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
import requests


from .models import (
    User, Tourist, Guide, Agency
)

from .serializers import (
     CustomTokenObtainPairSerializer, UserRegistrationSerializer,UserLoginSerializer, UserSerializer,
    TouristSerializer, GuideSerializer, GuideListSerializer, AgencySerializer,
    GoogleOAuthSerializer, FacebookOAuthSerializer,
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
    
    from rest_framework.decorators import action
 
    
    @action(detail=False, methods=['post'])
    def google_login(self, request):
        """Google OAuth Login/Register"""
        access_token = request.data.get("access_token")

        if not access_token:
            return Response({"error": "Access token is required"}, status=400)

        # Validate access token using Google's UserInfo endpoint
        google_user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = requests.get(
            google_user_info_url,
            params={'alt': 'json'},
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=400)

        user_info = response.json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        picture = user_info.get("picture")

        if not email:
            return Response({"error": "Email not found in Google profile"}, status=400)

        # Get or create the user
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0],
            'first_name': name.split()[0] if name else '',
            'last_name': name.split()[-1] if len(name.split()) > 1 else '',
            'is_verified': True,
            'is_approved': True,
        })

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Optional: Add custom claims
        access['user_type'] = user.user_type
        access['username'] = user.username
        access['email'] = user.email

        message = 'Registration successful' if created else 'Login successful'

        return Response({
            'user': UserSerializer(user).data,
            'access': str(access),
            'refresh': str(refresh),
            'message': message,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    
    @action(detail=False, methods=['post'])
    def facebook_login(self, request):
        """Facebook OAuth Login/Register"""
        access_token = request.data.get('access_token')

        if not access_token:
            return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Validate access token and get user info from Facebook
        fb_response = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,name,email',
                'access_token': access_token
            }
        )

        if fb_response.status_code != 200:
            return Response({'error': 'Invalid Facebook token'}, status=status.HTTP_400_BAD_REQUEST)

        fb_data = fb_response.json()
        email = fb_data.get('email')
        name = fb_data.get('name')

        if not email:
            return Response({'error': 'Email permission is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Get or create user
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email.split('@')[0],
            'full_name': name,  # optional: adjust according to your user model
            'is_active': True,
        })

        # Step 3: Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Optional: add custom claims
        access['user_type'] = getattr(user, 'user_type', '')
        access['username'] = user.username
        access['email'] = user.email

        message = 'Registration successful' if created else 'Login successful'

        return Response({
            'user': UserSerializer(user).data,
            'access': str(access),
            'refresh': str(refresh),
            'message': message,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# User Profile Views
class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put'])
    def tourist(self, request):
        """Get or update tourist profile"""
        if request.user.user_type != 'tourist':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        tourist_profile, created = Tourist.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = TouristSerializer(tourist_profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = TouristSerializer(tourist_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put'])
    def guide(self, request):
        """Get or update guide profile"""
        if request.user.user_type != 'guide':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        guide_profile, created = Guide.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = GuideSerializer(guide_profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = GuideSerializer(guide_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put'])
    def agency(self, request):
        """Get or update agency profile"""
        if request.user.user_type != 'agency':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        agency_profile, created = Agency.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = AgencySerializer(agency_profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = AgencySerializer(agency_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Guide Discovery Views
class GuideViewSet(viewsets.ReadOnlyModelViewSet):
    """Public guide listing and search"""
    queryset = Guide.objects.filter(user__is_approved=True, user__is_active=True)
    serializer_class = GuideListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['languages', 'specializations', 'user__is_verified']
    search_fields = ['user__first_name', 'user__last_name', 'specializations', 'bio']
    ordering_fields = ['average_rating', 'hourly_rate', 'daily_rate', 'experience_years']
    ordering = ['-average_rating']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check guide availability"""
        guide = self.get_object()
        # TODO: Implement availability logic with bookings
        return Response({'message': 'Availability checking not implemented yet'})

# Destination Views
