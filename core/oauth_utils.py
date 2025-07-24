import json
import requests
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import serializers


class GoogleOAuth:
    """Google OAuth utility class"""
    
    @staticmethod
    def verify_google_token(token):
        """
        Verify Google ID token and return user data
        """
        try:
            # Specify the CLIENT_ID of the app that accesses the backend
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
            )

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            if idinfo.get('aud') != getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None):
                raise ValueError('Invalid audience.')

            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer.')

            return {
                'google_id': idinfo.get('sub'),
                'email': idinfo.get('email'),
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'name': idinfo.get('name', ''),
                'profile_image': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
        except ValueError as e:
            raise serializers.ValidationError(f'Invalid Google token: {str(e)}')
        except Exception as e:
            raise serializers.ValidationError(f'Failed to verify Google token: {str(e)}')


class FacebookOAuth:
    """Facebook OAuth utility class"""
    
    @staticmethod
    def verify_facebook_token(access_token):
        """
        Verify Facebook access token and return user data
        """
        try:
            # Verify the token with Facebook
            app_id = getattr(settings, 'FACEBOOK_APP_ID', '')
            app_secret = getattr(settings, 'FACEBOOK_APP_SECRET', '')
            
            # Debug token to verify it's valid
            debug_url = f'https://graph.facebook.com/debug_token'
            debug_params = {
                'input_token': access_token,
                'access_token': f'{app_id}|{app_secret}'
            }
            
            debug_response = requests.get(debug_url, params=debug_params)
            debug_data = debug_response.json()
            
            if 'error' in debug_data or not debug_data.get('data', {}).get('is_valid'):
                raise ValueError('Invalid Facebook token')
            
            # Get user data
            user_url = 'https://graph.facebook.com/me'
            user_params = {
                'access_token': access_token,
                'fields': 'id,email,first_name,last_name,name,picture.type(large)'
            }
            
            user_response = requests.get(user_url, params=user_params)
            user_data = user_response.json()
            
            if 'error' in user_data:
                raise ValueError(f'Facebook API error: {user_data["error"]["message"]}')
            
            return {
                'facebook_id': user_data.get('id'),
                'email': user_data.get('email'),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'name': user_data.get('name', ''),
                'profile_image': user_data.get('picture', {}).get('data', {}).get('url', ''),
            }
            
        except requests.RequestException as e:
            raise serializers.ValidationError(f'Failed to connect to Facebook: {str(e)}')
        except ValueError as e:
            raise serializers.ValidationError(f'Invalid Facebook token: {str(e)}')
        except Exception as e:
            raise serializers.ValidationError(f'Failed to verify Facebook token: {str(e)}')


class SocialAuthUtils:
    """Utility functions for social authentication"""
    
    @staticmethod
    def generate_unique_username(base_name, email):
        """Generate a unique username from name and email"""
        from .models import User
        
        # Clean the base name
        base_username = base_name.lower().replace(' ', '_')
        if not base_username:
            base_username = email.split('@')[0].lower()
        
        # Ensure username is unique
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        return username
    
    @staticmethod
    def get_or_create_user_from_social_data(user_data, provider):
        """
        Get or create user from social authentication data
        """
        from .models import User
        
        email = user_data.get('email')
        provider_id = user_data.get(f'{provider}_id')
        
        if not email or not provider_id:
            raise serializers.ValidationError(f'Email and {provider} ID are required')
        
        # Check if user exists with this provider ID
        user = None
        if provider == 'google':
            user = User.objects.filter(google_id=provider_id).first()
        elif provider == 'facebook':
            user = User.objects.filter(facebook_id=provider_id).first()
        
        if user:
            return user, False  # User exists, not created
        
        # Check if user exists with this email
        user = User.objects.filter(email=email).first()
        if user:
            # Update existing user with social provider info
            if provider == 'google':
                user.google_id = provider_id
            elif provider == 'facebook':
                user.facebook_id = provider_id
            
            user.provider = provider
            user.provider_id = provider_id
            user.is_verified = True  # Social accounts are considered verified
            user.save()
            return user, False
        
        # Create new user
        username = SocialAuthUtils.generate_unique_username(
            user_data.get('name', ''), 
            email
        )
        
        user_fields = {
            'username': username,
            'email': email,
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'is_verified': True,
            'is_approved': True,
            'provider': provider,
            'provider_id': provider_id,
        }
        
        if provider == 'google':
            user_fields['google_id'] = provider_id
        elif provider == 'facebook':
            user_fields['facebook_id'] = provider_id
        
        user = User.objects.create_user(**user_fields)
        
        # Download and save profile image if available
        profile_image_url = user_data.get('profile_image')
        if profile_image_url:
            try:
                SocialAuthUtils.save_profile_image_from_url(user, profile_image_url)
            except:
                pass  # If profile image saving fails, it's not critical
        
        return user, True  # User created
    
    @staticmethod
    def save_profile_image_from_url(user, image_url):
        """Save profile image from URL"""
        import tempfile
        from django.core.files import File
        from django.core.files.temp import NamedTemporaryFile
        import requests
        
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                
                # Save to user profile
                filename = f"profile_{user.id}.jpg"
                user.profile_image.save(filename, File(img_temp), save=True)
        except Exception:
            pass  # Silently fail if image can't be saved
