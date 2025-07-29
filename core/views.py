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
    User, Tourist, Guide, Agency, Package, Booking, Rating
)

from .serializers import (
     CustomTokenObtainPairSerializer, UserRegistrationSerializer,UserLoginSerializer, UserSerializer,
    TouristSerializer, GuideSerializer, GuideListSerializer, AgencySerializer, AgencyListSerializer,
    PackageSerializer, PackageListSerializer, BookingSerializer, BookingCreateSerializer,
    RatingSerializer, RatingCreateSerializer, GoogleOAuthSerializer, FacebookOAuthSerializer,
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
    serializer_class = UserSerializer  # fallback for DRF

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'profile':
            return UserSerializer
        return UserSerializer

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

# Agency Views
class AgencyViewSet(viewsets.ReadOnlyModelViewSet):
    """Public agency listing and search"""
    queryset = Agency.objects.filter(user__is_approved=True, user__is_active=True)
    serializer_class = AgencyListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['company_name', 'description', 'address']
    ordering_fields = ['average_rating', 'total_bookings', 'user__created_at']
    ordering = ['-average_rating']
    
    @action(detail=True, methods=['get'])
    def guides(self, request, pk=None):
        """Get guides managed by this agency"""
        agency = self.get_object()
        guides = agency.managed_guides.filter(user__is_approved=True, user__is_active=True)
        serializer = GuideListSerializer(guides, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def packages(self, request, pk=None):
        """Get packages offered by this agency"""
        agency = self.get_object()
        packages = agency.packages.filter(is_active=True)
        serializer = PackageListSerializer(packages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """Get ratings for this agency"""
        agency = self.get_object()
        ratings = agency.ratings.all().order_by('-created_at')
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

# Package Views
class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    """Public package listing and search"""
    queryset = Package.objects.filter(is_active=True, agency__user__is_approved=True)
    serializer_class = PackageListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['package_type', 'duration_days']
    search_fields = ['name', 'description', 'destinations']
    ordering_fields = ['price', 'average_rating', 'total_bookings', 'created_at']
    ordering = ['-average_rating']
    
    @action(detail=True, methods=['get'])
    def agencies(self, request, pk=None):
        """Get agencies offering similar packages"""
        package = self.get_object()
        similar_packages = Package.objects.filter(
            package_type=package.package_type,
            is_active=True,
            agency__user__is_approved=True
        ).exclude(id=package.id)
        
        agencies = Agency.objects.filter(
            packages__in=similar_packages
        ).distinct()
        
        serializer = AgencyListSerializer(agencies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """Get ratings for this package"""
        package = self.get_object()
        ratings = package.ratings.all().order_by('-created_at')
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

# Enhanced Guide Views
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
    def agencies(self, request, pk=None):
        """Get agencies this guide is registered with"""
        guide = self.get_object()
        agencies = Agency.objects.filter(managed_guides=guide, user__is_approved=True)
        serializer = AgencyListSerializer(agencies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """Get ratings for this guide"""
        guide = self.get_object()
        ratings = guide.ratings.all().order_by('-created_at')
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check guide availability"""
        guide = self.get_object()
        # TODO: Implement availability logic with bookings
        return Response({'message': 'Availability checking not implemented yet'})

# Tourist Booking and Rating Views
class TouristBookingViewSet(viewsets.ModelViewSet):
    """Tourist booking management"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'tourist':
            try:
                tourist = self.request.user.tourist_profile
                return tourist.bookings.all().order_by('-created_at')
            except:
                return Booking.objects.none()
        return Booking.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        # Ensure tourist profile exists
        tourist_profile, created = Tourist.objects.get_or_create(user=self.request.user)
        
        # Calculate total price based on booking type
        booking_data = serializer.validated_data
        number_of_people = booking_data.get('number_of_people', 1)
        
        if booking_data.get('package'):
            total_price = booking_data['package'].price * number_of_people
        elif booking_data.get('guide'):
            # Calculate based on guide's daily rate and duration
            start_date = booking_data['start_date']
            end_date = booking_data['end_date']
            duration = (end_date - start_date).days + 1
            total_price = booking_data['guide'].daily_rate * duration * number_of_people
        else:
            # For agency booking, price needs to be calculated based on services
            total_price = 0  # This should be handled differently in real implementation
        
        serializer.save(tourist=tourist_profile, total_price=total_price)

class TouristRatingViewSet(viewsets.ModelViewSet):
    """Tourist rating management"""
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'tourist':
            try:
                tourist = self.request.user.tourist_profile
                return tourist.ratings.all().order_by('-created_at')
            except:
                return Rating.objects.none()
        return Rating.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RatingCreateSerializer
        return RatingSerializer
    
    def perform_create(self, serializer):
        # Ensure tourist profile exists
        tourist_profile, created = Tourist.objects.get_or_create(user=self.request.user)
        serializer.save(tourist=tourist_profile)

# Agency Management Views
class AgencyManagementViewSet(viewsets.GenericViewSet):
    """Agency management for their own content"""
    permission_classes = [IsAuthenticated]
    
    def get_agency_profile(self):
        if self.request.user.user_type != 'agency':
            return None
        try:
            return self.request.user.agency_profile
        except:
            return None
    
    @action(detail=False, methods=['get', 'post'])
    def packages(self, request):
        """Manage agency packages"""
        agency = self.get_agency_profile()
        if not agency:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            packages = agency.packages.all()
            serializer = PackageSerializer(packages, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = PackageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(agency=agency)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post'])
    def guides(self, request):
        """Manage agency guides"""
        agency = self.get_agency_profile()
        if not agency:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            guides = agency.managed_guides.all()
            serializer = GuideSerializer(guides, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            guide_id = request.data.get('guide_id')
            try:
                guide = Guide.objects.get(id=guide_id, user__is_approved=True)
                agency.managed_guides.add(guide)
                return Response({'message': 'Guide added successfully'})
            except Guide.DoesNotExist:
                return Response({'error': 'Guide not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def bookings(self, request):
        """View agency bookings"""
        agency = self.get_agency_profile()
        if not agency:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get all bookings for this agency's packages, guides, or direct agency bookings
        bookings = Booking.objects.filter(
            Q(package__agency=agency) | 
            Q(guide__in=agency.managed_guides.all()) |
            Q(agency=agency)
        ).order_by('-created_at')
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

# Admin Views
class AdminViewSet(viewsets.GenericViewSet):
    """Admin management views"""
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return super().dispatch(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def pending_agencies(self, request):
        """Get agencies pending approval"""
        agencies = Agency.objects.filter(user__is_approved=False)
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def approve_agency(self, request):
        """Approve an agency"""
        agency_id = request.data.get('agency_id')
        try:
            agency = Agency.objects.get(id=agency_id)
            agency.user.is_approved = True
            agency.user.is_verified = True
            agency.user.save()
            return Response({'message': 'Agency approved successfully'})
        except Agency.DoesNotExist:
            return Response({'error': 'Agency not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def reject_agency(self, request):
        """Reject an agency"""
        agency_id = request.data.get('agency_id')
        try:
            agency = Agency.objects.get(id=agency_id)
            agency.user.is_active = False
            agency.user.save()
            return Response({'message': 'Agency rejected'})
        except Agency.DoesNotExist:
            return Response({'error': 'Agency not found'}, status=status.HTTP_404_NOT_FOUND)

# Homepage Views
class HomepageViewSet(viewsets.GenericViewSet):
    """Homepage content for tourists"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def content(self, request):
        """Get homepage content - packages, guides, and agencies"""
        # Featured packages
        featured_packages = Package.objects.filter(
            is_active=True, 
            agency__user__is_approved=True
        ).order_by('-average_rating')[:6]
        
        # Top guides
        top_guides = Guide.objects.filter(
            user__is_approved=True, 
            user__is_active=True
        ).order_by('-average_rating')[:6]
        
        # Top agencies
        top_agencies = Agency.objects.filter(
            user__is_approved=True, 
            user__is_active=True
        ).order_by('-average_rating')[:6]
        
        return Response({
            'packages': PackageListSerializer(featured_packages, many=True).data,
            'guides': GuideListSerializer(top_guides, many=True).data,
            'agencies': AgencyListSerializer(top_agencies, many=True).data,
        })
