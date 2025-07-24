from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid

# User Models
class User(AbstractUser):
    USER_TYPES = (
        ('tourist', 'Tourist'),
        ('guide', 'Freelance Guide'),
        ('agency', 'Agency'),
        ('admin', 'Admin'),
    )
    
    PROVIDER_CHOICES = (
        ('email', 'Email'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='tourist')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Social Authentication fields
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='email')
    provider_id = models.CharField(max_length=255, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username']

class Tourist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tourist_profile')
    travel_interests = models.JSONField(default=list, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Tourist: {self.user.username}"

class Guide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile', null = True)
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    license_document = models.FileField(upload_to='licenses/', null=True, blank=True)
    languages = models.JSONField(default=list, blank=True)
    specializations = models.JSONField(default=list, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    experience_years = models.IntegerField(default=0)
    portfolio_images = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_trips = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Guide: {self.user.username}"

class Agency(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile')
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_license = models.FileField(upload_to='company_licenses/', null=True, blank=True)
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    managed_guides = models.ManyToManyField(Guide, blank=True)
    
    def __str__(self):
        return f"Agency: {self.company_name or self.user.username}"

