from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    User, Tourist, Guide, Agency
)
from .oauth_utils import GoogleOAuth, FacebookOAuth, SocialAuthUtils


# Custom JWT Token Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_type'] = user.user_type
        token['username'] = user.username
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        token['is_approved'] = user.is_approved
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'user_type': self.user.user_type,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_verified': self.user.is_verified,
            'is_approved': self.user.is_approved,
            'phone_number': self.user.phone_number,
        }
        
        return data
    

# User Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        # Automatically assign defaults
        validated_data['user_type'] = 'tourist'  # Default type
        validated_data['is_verified'] = True
        validated_data['is_approved'] = True

        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
            
        else:
            raise serializers.ValidationError('Must include username and password')
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'profile_image', 'is_verified', 
                 'is_approved', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified', 'is_approved')

# Profile Serializers
class TouristSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Tourist
        fields = '__all__'

class GuideSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Guide
        fields = '__all__'
        
class GuideListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Guide
        fields = ('id', 'user', 'languages', 'specializations', 'hourly_rate', 
                 'daily_rate', 'experience_years', 'average_rating', 'total_trips')

class AgencySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    managed_guides = GuideListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Agency
        fields = '__all__'


# Social Authentication Serializers
class GoogleOAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication"""
    token = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPES, 
        default='tourist', 
        required=False
    )
    
    def validate(self, attrs):
        token = attrs.get('token')
        user_type = attrs.get('user_type', 'tourist')
        
        # Verify Google token
        try:
            google_user_data = GoogleOAuth.verify_google_token(token)
        except serializers.ValidationError:
            raise
        
        # Get or create user
        try:
            user, created = SocialAuthUtils.get_or_create_user_from_social_data(
                google_user_data, 'google'
            )
            
            # Set user type if this is a new user
            if created:
                user.user_type = user_type
                user.save()
            
            attrs['user'] = user
            attrs['created'] = created
            attrs['google_user_data'] = google_user_data
            
        except Exception as e:
            raise serializers.ValidationError(f'Failed to authenticate with Google: {str(e)}')
        
        return attrs


class FacebookOAuthSerializer(serializers.Serializer):
    """Serializer for Facebook OAuth authentication"""
    access_token = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPES, 
        default='tourist', 
        required=False
    )
    
    def validate(self, attrs):
        access_token = attrs.get('access_token')
        user_type = attrs.get('user_type', 'tourist')
        
        # Verify Facebook token
        try:
            facebook_user_data = FacebookOAuth.verify_facebook_token(access_token)
        except serializers.ValidationError:
            raise
        
        # Get or create user
        try:
            user, created = SocialAuthUtils.get_or_create_user_from_social_data(
                facebook_user_data, 'facebook'
            )
            
            # Set user type if this is a new user
            if created:
                user.user_type = user_type
                user.save()
            
            attrs['user'] = user
            attrs['created'] = created
            attrs['facebook_user_data'] = facebook_user_data
            
        except Exception as e:
            raise serializers.ValidationError(f'Failed to authenticate with Facebook: {str(e)}')
        
        return attrs

 
