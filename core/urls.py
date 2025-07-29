from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

router = DefaultRouter()
# Authentication and Profile Management
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'profile', views.ProfileViewSet, basename='profile')

# Public Browse Views (for tourists)
router.register(r'guides', views.GuideViewSet, basename='guide')
router.register(r'agencies', views.AgencyViewSet, basename='agency')
router.register(r'packages', views.PackageViewSet, basename='package')
router.register(r'homepage', views.HomepageViewSet, basename='homepage')

# Tourist-specific Views
router.register(r'tourist/bookings', views.TouristBookingViewSet, basename='tourist-booking')
router.register(r'tourist/ratings', views.TouristRatingViewSet, basename='tourist-rating')

# Agency Management Views
router.register(r'agency/manage', views.AgencyManagementViewSet, basename='agency-manage')

# Admin Views
router.register(r'admin', views.AdminViewSet, basename='admin')

urlpatterns = [
    # ViewSet routes (this will create the endpoints you're using)
    path('', include(router.urls)),
    
    # JWT token endpoints (if you want to use them separately)
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
]