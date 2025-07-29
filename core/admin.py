from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from .models import User, Guide, Tourist, Agency, Package, Booking, Rating

# Customize admin site headers
admin.site.site_header = "Guide App Administration"
admin.site.site_title = "Guide App Admin"
admin.site.index_title = "Welcome to Guide App Administration Panel"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_approved', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Account Status', {
            'fields': ('user_type', 'is_verified', 'is_approved', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Profile', {
            'fields': ('profile_image',)
        }),
        ('Social Auth', {
            'fields': ('provider', 'google_id', 'facebook_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(Tourist)
class TouristAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'get_user_email', 'nationality', 'get_travel_interests', 'emergency_contact']
    list_filter = ['nationality', 'user__created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Full Name'
    get_user_name.admin_order_field = 'user__first_name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_travel_interests(self, obj):
        return ', '.join(obj.travel_interests) if obj.travel_interests else 'None'
    get_travel_interests.short_description = 'Travel Interests'

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ['get_user_name', 'get_user_email', 'get_specializations', 'experience_years', 'average_rating', 'total_trips', 'hourly_rate', 'daily_rate']
    list_filter = ['experience_years', 'average_rating', 'user__is_verified', 'user__created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'specializations']
    readonly_fields = ['average_rating', 'total_trips']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'license_number', 'license_document', 'bio')
        }),
        ('Professional Details', {
            'fields': ('languages', 'specializations', 'experience_years')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'daily_rate')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_trips'),
            'classes': ('collapse',)
        }),
        ('Portfolio', {
            'fields': ('portfolio_images',),
            'classes': ('collapse',)
        })
    )
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Full Name'
    get_user_name.admin_order_field = 'user__first_name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_specializations(self, obj):
        return ', '.join(obj.specializations) if obj.specializations else 'None'
    get_specializations.short_description = 'Specializations'

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'get_user_email', 'get_user_name', 'average_rating', 'total_bookings', 'get_approval_status']
    list_filter = ['user__is_approved', 'user__is_verified', 'average_rating', 'user__created_at']
    search_fields = ['company_name', 'user__username', 'user__email', 'address']
    readonly_fields = ['average_rating', 'total_bookings']
    filter_horizontal = ['managed_guides']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('user', 'company_name', 'address', 'website', 'description')
        }),
        ('Legal Documents', {
            'fields': ('company_license', 'registration_number')
        }),
        ('Business Settings', {
            'fields': ('commission_rate',)
        }),
        ('Guide Management', {
            'fields': ('managed_guides',)
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_bookings'),
            'classes': ('collapse',)
        })
    )
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_name.short_description = 'Contact Person'
    get_user_name.admin_order_field = 'user__first_name'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_approval_status(self, obj):
        if obj.user.is_approved:
            return format_html('<span style="color: green;">✓ Approved</span>')
        else:
            return format_html('<span style="color: red;">✗ Pending</span>')
    get_approval_status.short_description = 'Status'
    get_approval_status.admin_order_field = 'user__is_approved'

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'package_type', 'duration_days', 'price', 'max_people', 'average_rating', 'total_bookings', 'is_active']
    list_filter = ['package_type', 'is_active', 'duration_days', 'agency', 'created_at']
    search_fields = ['name', 'description', 'agency__company_name']
    readonly_fields = ['id', 'average_rating', 'total_bookings', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'package_type', 'agency')
        }),
        ('Package Details', {
            'fields': ('duration_days', 'price', 'max_people', 'is_active')
        }),
        ('Services', {
            'fields': ('included_services', 'excluded_services')
        }),
        ('Itinerary', {
            'fields': ('destinations', 'itinerary')
        }),
        ('Media', {
            'fields': ('images',)
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_bookings'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_tourist_name', 'booking_type', 'get_service_name', 'status', 'start_date', 'end_date', 'number_of_people', 'total_price']
    list_filter = ['booking_type', 'status', 'start_date', 'created_at']
    search_fields = ['tourist__user__username', 'tourist__user__email', 'package__name', 'guide__user__username', 'agency__company_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('tourist', 'booking_type', 'status')
        }),
        ('Service Details', {
            'fields': ('package', 'guide', 'agency')
        }),
        ('Booking Details', {
            'fields': ('start_date', 'end_date', 'number_of_people', 'total_price')
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_tourist_name(self, obj):
        return f"{obj.tourist.user.first_name} {obj.tourist.user.last_name}"
    get_tourist_name.short_description = 'Tourist'
    get_tourist_name.admin_order_field = 'tourist__user__first_name'
    
    def get_service_name(self, obj):
        if obj.booking_type == 'package' and obj.package:
            return obj.package.name
        elif obj.booking_type == 'guide' and obj.guide:
            return f"{obj.guide.user.first_name} {obj.guide.user.last_name}"
        elif obj.booking_type == 'agency' and obj.agency:
            return obj.agency.company_name
        return 'N/A'
    get_service_name.short_description = 'Service'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['get_tourist_name', 'rating_type', 'get_service_name', 'rating', 'get_rating_stars', 'created_at']
    list_filter = ['rating_type', 'rating', 'created_at']
    search_fields = ['tourist__user__username', 'tourist__user__email', 'review']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('tourist', 'rating_type', 'rating')
        }),
        ('Service Details', {
            'fields': ('package', 'guide', 'agency')
        }),
        ('Review', {
            'fields': ('review',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_tourist_name(self, obj):
        return f"{obj.tourist.user.first_name} {obj.tourist.user.last_name}"
    get_tourist_name.short_description = 'Tourist'
    get_tourist_name.admin_order_field = 'tourist__user__first_name'
    
    def get_service_name(self, obj):
        if obj.rating_type == 'package' and obj.package:
            return obj.package.name
        elif obj.rating_type == 'guide' and obj.guide:
            return f"{obj.guide.user.first_name} {obj.guide.user.last_name}"
        elif obj.rating_type == 'agency' and obj.agency:
            return obj.agency.company_name
        return 'N/A'
    get_service_name.short_description = 'Service'
    
    def get_rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(f'<span style="color: gold; font-size: 16px;">{stars}</span>')
    get_rating_stars.short_description = 'Stars'
    get_rating_stars.admin_order_field = 'rating'
