from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'guides', views.GuideViewSet, basename='guide')
# router.register(r'agencies', views.AgencyViewSet, basename='agency')
# router.register(r'destinations', views.DestinationViewSet, basename='destination')
# router.register(r'bookings', views.BookingViewSet, basename='booking')
# router.register(r'payments', views.PaymentViewSet, basename='payment')
# router.register(r'ratings', views.RatingViewSet, basename='rating')
# router.register(r'chatrooms', views.ChatRoomViewSet, basename='chatroom')
# router.register(r'messages', views.MessageViewSet, basename='message')
# router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # ViewSet routes (this will create the endpoints you're using)
    path('', include(router.urls)),
    
    # JWT token endpoints (if you want to use them separately)
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
]