# 🔐 Google & Facebook OAuth Integration Guide

This guide explains how to use the newly implemented Google and Facebook OAuth authentication in your Guide App.

## 🆕 What's Been Added

### 1. User Model Updates
- ✅ Added `provider` field (email, google, facebook)
- ✅ Added `provider_id` field for social account IDs
- ✅ Added `google_id` field for Google Account ID
- ✅ Added `facebook_id` field for Facebook Account ID

### 2. New API Endpoints
- ✅ `POST /api/auth/google_login/` - Google OAuth Login/Register
- ✅ `POST /api/auth/facebook_login/` - Facebook OAuth Login/Register

### 3. OAuth Utilities
- ✅ Google token verification
- ✅ Facebook token verification
- ✅ Automatic user creation/linking
- ✅ Profile image download from social providers

## 🚀 Setup Instructions

### Step 1: Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google+ API** and **Google Identity and Access Management (IAM) API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Configure the OAuth consent screen
6. Create OAuth 2.0 client ID:
   - Application type: Web application
   - Authorized JavaScript origins: `http://localhost:3000` (your frontend URL)
   - Authorized redirect URIs: `http://localhost:3000/auth/callback` (if needed)
7. Copy the **Client ID** and **Client Secret**

### Step 2: Facebook App Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **Create App** → **Consumer** → **Next**
3. Enter your app name and contact email
4. Go to **Settings** → **Basic**
5. Copy the **App ID** and **App Secret**
6. Add **Facebook Login** product
7. In **Facebook Login** settings:
   - Valid OAuth Redirect URIs: `http://localhost:3000/auth/callback` (if needed)
   - Web OAuth Settings: Enable

### Step 3: Environment Configuration

Create a `.env` file in your project root:

```bash
# Database Configuration
DB_NAME=guide_db
DB_USER=muke
DB_PASSWORD=muke123
DB_HOST=localhost
DB_PORT=5432

# Google OAuth2 Configuration
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret

# Facebook OAuth Configuration
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

## 📱 Frontend Integration

### Google OAuth Frontend Example

```javascript
// Install: npm install google-auth-library

// Get Google ID token (example using Google Sign-In JavaScript)
function signInWithGoogle() {
    google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed()) {
            console.log('Sign-in dialog not displayed');
        }
    });
}

// Handle Google sign-in response
function handleGoogleSignIn(response) {
    const idToken = response.credential;
    
    // Send to your Django backend
    fetch('/api/auth/google_login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            token: idToken,
            user_type: 'tourist' // or 'guide', 'agency'
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            // Store JWT tokens
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            console.log('Login successful:', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}
```

### Facebook OAuth Frontend Example

```javascript
// Install Facebook SDK for JavaScript

// Initialize Facebook SDK
window.fbAsyncInit = function() {
    FB.init({
        appId: 'your_facebook_app_id',
        cookie: true,
        xfbml: true,
        version: 'v18.0'
    });
};

// Handle Facebook login
function loginWithFacebook() {
    FB.login(function(response) {
        if (response.authResponse) {
            const accessToken = response.authResponse.accessToken;
            
            // Send to your Django backend
            fetch('/api/auth/facebook_login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    access_token: accessToken,
                    user_type: 'guide' // or 'tourist', 'agency'
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.access) {
                    // Store JWT tokens
                    localStorage.setItem('access_token', data.access);
                    localStorage.setItem('refresh_token', data.refresh);
                    console.log('Login successful:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }, {scope: 'email,public_profile'});
}
```

## 📊 API Documentation

### Google OAuth Login/Register
```
POST /api/auth/google_login/
Content-Type: application/json

{
    "token": "google_id_token_from_frontend",
    "user_type": "tourist"  // optional: tourist, guide, agency
}

Response (201 for new user, 200 for existing):
{
    "user": {
        "id": "uuid",
        "username": "john_doe",
        "email": "john@gmail.com",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "tourist",
        "provider": "google",
        "is_verified": true
    },
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "message": "Login successful",
    "created": false
}
```

### Facebook OAuth Login/Register
```
POST /api/auth/facebook_login/
Content-Type: application/json

{
    "access_token": "facebook_access_token_from_frontend",
    "user_type": "guide"  // optional: tourist, guide, agency
}

Response (201 for new user, 200 for existing):
{
    "user": {
        "id": "uuid",
        "username": "jane_smith",
        "email": "jane@facebook.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "user_type": "guide",
        "provider": "facebook",
        "is_verified": true
    },
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "message": "Registration successful",
    "created": true
}
```

## 🔄 User Flow Logic

### New User Registration
1. Frontend gets OAuth token from Google/Facebook
2. Frontend sends token to Django API
3. Django verifies token with OAuth provider
4. Django creates new user account
5. Django returns JWT tokens for authentication

### Existing User Login
1. User exists with same email → Links OAuth account
2. User exists with same OAuth ID → Direct login
3. Django returns JWT tokens for authentication

### Profile Image Handling
- Automatically downloads and saves profile images from OAuth providers
- Images are stored in `media/profiles/` directory
- Gracefully handles image download failures

## 🧪 Testing

Run the test script to verify everything is working:
```bash
poetry run python test_oauth.py
```

Test with real tokens by starting the server:
```bash
poetry run python manage.py runserver
```

## 🔧 Troubleshooting

### Common Issues

1. **"Invalid Google token"**
   - Ensure `GOOGLE_OAUTH2_CLIENT_ID` is set correctly in `.env`
   - Verify the token is a valid Google ID token, not access token

2. **"Invalid Facebook token"**
   - Ensure `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` are set correctly
   - Verify the token is a valid Facebook access token

3. **"Email required"**
   - Make sure your OAuth app requests email scope
   - Check that the social provider returns user email

4. **CORS Issues**
   - Update `CORS_ALLOWED_ORIGINS` in settings.py
   - Add your frontend URL to allowed origins

### Environment Variables Check
```bash
# Check if environment variables are loaded
poetry run python -c "
from decouple import config
print('Google Client ID:', config('GOOGLE_OAUTH2_CLIENT_ID', 'NOT SET'))
print('Facebook App ID:', config('FACEBOOK_APP_ID', 'NOT SET'))
"
```

## 🎯 Next Steps

1. Set up your OAuth applications (Google Cloud Console & Facebook Developers)
2. Configure environment variables
3. Implement frontend OAuth flows
4. Test with real OAuth tokens
5. Deploy with HTTPS for production use

## 📝 Notes

- OAuth accounts are automatically verified (`is_verified=True`)
- Profile images are automatically downloaded and saved
- Users can link multiple OAuth providers to the same account
- JWT tokens work the same way as regular email/password authentication

Need help? Check the test script output or Django server logs for detailed error messages!
