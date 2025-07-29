from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

# User Models
class User(AbstractUser):
    USER_TYPES = (
    ('tourist', 'Tourist'),
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
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_tourist(self):
        return self.user_type == 'tourist'

    @property
    def is_agency(self):
        return self.user_type == 'agency'

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    def clean(self):
        if self.user_type == 'admin' and not self.is_staff:
            raise ValidationError('Admin must have is_staff=True.')

    def save(self, *args, **kwargs):
        # Ensure that admin users are marked as staff
        if self.is_admin:
            self.is_staff = True
        
        # Auto-approve tourists and admins, but not agencies
        if self.user_type in ['tourist', 'admin'] and not self.is_approved:
            self.is_approved = True
            self.is_verified = True
        
        super().save(*args, **kwargs)
    
    def get_profile(self):
        """Get the related profile based on user type"""
        if self.is_tourist:
            return getattr(self, 'tourist_profile', None)
        elif self.is_agency:
            return getattr(self, 'agency_profile', None)
        return None

    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username
    
    def get_display_name(self):
        """Get display name based on user type"""
        if self.is_agency and hasattr(self, 'agency_profile'):
            return self.agency_profile.company_name or self.get_full_name()
        return self.get_full_name()
    
    def can_book_services(self):
        """Check if user can book services (only tourists)"""
        return self.is_tourist and self.is_active and self.is_approved
    
    def can_manage_services(self):
        """Check if user can manage services (agencies and admins)"""
        return (self.is_agency or self.is_admin) and self.is_active and self.is_approved
    
    def requires_approval(self):
        """Check if user type requires admin approval"""
        return self.user_type == 'agency'
    
    def __str__(self):
        return f"{self.get_display_name()} ({self.get_user_type_display()})"
    
    class Meta:
        db_table = 'core_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    # Social Authentication fields
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='email')
    provider_id = models.CharField(max_length=255, blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username']

class Tourist(models.Model):
    TRAVEL_INTERESTS_CHOICES = [
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('religious', 'Religious'),
        ('wildlife', 'Wildlife'),
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City Tours'),
        ('heritage', 'Heritage'),
        ('food', 'Food & Cuisine'),
        ('photography', 'Photography'),
        ('relaxation', 'Relaxation'),
        ('family', 'Family Friendly'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tourist_profile')
    travel_interests = models.JSONField(default=list, blank=True, help_text="List of travel interests")
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=50, default='English')
    travel_budget_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., $500-1000")
    total_bookings = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def clean(self):
        if self.user and not self.user.is_tourist:
            raise ValidationError('User must be of type tourist')
    
    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def get_travel_interests_display(self):
        """Get display names for travel interests"""
        interests_dict = dict(self.TRAVEL_INTERESTS_CHOICES)
        return [interests_dict.get(interest, interest) for interest in self.travel_interests]
    
    def has_completed_profile(self):
        """Check if tourist has completed their profile"""
        required_fields = [self.nationality, self.date_of_birth, self.emergency_contact]
        return all(field is not None and field != '' for field in required_fields)
    
    def __str__(self):
        return f"Tourist: {self.user.get_full_name()}"
    
    class Meta:
        db_table = 'core_tourist'
        verbose_name = 'Tourist Profile'
        verbose_name_plural = 'Tourist Profiles'

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
    AGENCY_TYPES = [
        ('tour_operator', 'Tour Operator'),
        ('travel_agency', 'Travel Agency'),
        ('adventure_company', 'Adventure Company'),
        ('cultural_tours', 'Cultural Tours'),
        ('eco_tourism', 'Eco Tourism'),
        ('luxury_travel', 'Luxury Travel'),
        ('budget_travel', 'Budget Travel'),
        ('corporate_travel', 'Corporate Travel'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile')
    company_name = models.CharField(max_length=200, blank=True, null=True)
    agency_type = models.CharField(max_length=50, choices=AGENCY_TYPES, blank=True, null=True)
    company_license = models.FileField(upload_to='company_licenses/', null=True, blank=True)
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    social_media_links = models.JSONField(default=dict, blank=True, help_text="Social media profiles")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    managed_guides = models.ManyToManyField(Guide, blank=True, related_name='agencies')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    employee_count = models.IntegerField(blank=True, null=True)
    certifications = models.JSONField(default=list, blank=True, help_text="List of certifications")
    operating_regions = models.JSONField(default=list, blank=True, help_text="Regions where agency operates")
    
    def clean(self):
        if self.user and not self.user.is_agency:
            raise ValidationError('User must be of type agency')
        
        if self.commission_rate < 0 or self.commission_rate > 50:
            raise ValidationError('Commission rate must be between 0% and 50%')
    
    @property
    def is_approved(self):
        return self.user.is_approved
    
    @property
    def years_in_business(self):
        if self.established_year:
            from datetime import datetime
            return datetime.now().year - self.established_year
        return None
    
    def get_active_packages_count(self):
        return self.packages.filter(is_active=True).count()
    
    def get_completion_percentage(self):
        """Calculate profile completion percentage"""
        required_fields = [
            self.company_name, self.agency_type, self.address, 
            self.city, self.country, self.description
        ]
        completed = sum(1 for field in required_fields if field)
        return int((completed / len(required_fields)) * 100)
    
    def has_valid_license(self):
        """Check if agency has uploaded valid license documents"""
        return bool(self.company_license and self.registration_number)
    
    def __str__(self):
        return f"Agency: {self.company_name or self.user.get_full_name()}"
    
    class Meta:
        db_table = 'core_agency'
        verbose_name = 'Agency Profile'
        verbose_name_plural = 'Agency Profiles'
        ordering = ['-user__created_at']


class Package(models.Model):
    PACKAGE_TYPES = (
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('religious', 'Religious'),
        ('wildlife', 'Wildlife'),
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City Tour'),
        ('heritage', 'Heritage'),
        ('custom', 'Custom'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='packages')
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_people = models.IntegerField(default=10)
    included_services = models.JSONField(default=list, blank=True)
    excluded_services = models.JSONField(default=list, blank=True)
    destinations = models.JSONField(default=list, blank=True)  # List of places
    itinerary = models.JSONField(default=list, blank=True)  # Day-wise itinerary
    images = models.JSONField(default=list, blank=True)  # Package images
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_bookings = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.agency.company_name}"

class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    BOOKING_TYPE = (
        ('package', 'Package'),
        ('guide', 'Guide'),
        ('agency', 'Agency'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tourist = models.ForeignKey(Tourist, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE)
    
    # References to different booking options
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_people = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.tourist.user.username}"

class Rating(models.Model):
    RATING_TYPE = (
        ('package', 'Package'),
        ('guide', 'Guide'),
        ('agency', 'Agency'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tourist = models.ForeignKey(Tourist, on_delete=models.CASCADE, related_name='ratings')
    rating_type = models.CharField(max_length=20, choices=RATING_TYPE)
    
    # References to different rating targets
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tourist', 'package', 'guide', 'agency']  # One rating per tourist per item
    
    def __str__(self):
        return f"Rating {self.rating}/5 by {self.tourist.user.username}"

