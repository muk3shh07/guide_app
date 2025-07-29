#!/usr/bin/env python3
"""
Create sample data for the Guide App
Run this script to populate the database with test data
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.append('/home/mukesh/Documents/guide_app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import User, Tourist, Guide, Agency, Package, Booking, Rating

def create_sample_users():
    """Create sample users for testing"""
    print("Creating sample users...")
    
    # Create admin user
    try:
        admin_user, created = User.objects.get_or_create(
            email='admin@guideapp.com',
            defaults={
                'username': 'admin_sample',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'is_approved': True,
                'phone_number': '+1234567890'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("✅ Admin user created")
        else:
            print("ℹ️ Admin user already exists")
    except Exception as e:
        print(f"ℹ️ Admin user creation skipped: {e}")
    
    # Create sample tourists
    tourists_data = [
        {
            'email': 'john.doe@email.com',
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567891'
        },
        {
            'email': 'jane.smith@email.com',
            'username': 'jane_smith',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone_number': '+1234567892'
        }
    ]
    
    for tourist_data in tourists_data:
        user, created = User.objects.get_or_create(
            email=tourist_data['email'],
            defaults={
                **tourist_data,
                'user_type': 'tourist',
                'is_verified': True,
                'is_approved': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create tourist profile
            Tourist.objects.get_or_create(
                user=user,
                defaults={
                    'travel_interests': ['adventure', 'cultural', 'wildlife'],
                    'nationality': 'USA',
                    'emergency_contact': '+1234567890'
                }
            )
            print(f"✅ Tourist {user.username} created")

def create_sample_guides():
    """Create sample guides"""
    print("Creating sample guides...")
    
    guides_data = [
        {
            'email': 'guide1@email.com',
            'username': 'mountain_guide',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'phone_number': '+1234567893',
            'specializations': ['mountain', 'adventure', 'trekking'],
            'languages': ['English', 'Spanish'],
            'hourly_rate': 50.00,
            'daily_rate': 300.00,
            'experience_years': 8,
            'bio': 'Experienced mountain guide with 8 years of expertise in high-altitude trekking.'
        },
        {
            'email': 'guide2@email.com',
            'username': 'cultural_guide',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'phone_number': '+1234567894',
            'specializations': ['cultural', 'heritage', 'history'],
            'languages': ['English', 'French', 'Italian'],
            'hourly_rate': 40.00,
            'daily_rate': 250.00,
            'experience_years': 6,
            'bio': 'Cultural heritage specialist with deep knowledge of local history and traditions.'
        }
    ]
    
    for guide_data in guides_data:
        guide_profile_data = {
            'specializations': guide_data.pop('specializations'),
            'languages': guide_data.pop('languages'),
            'hourly_rate': guide_data.pop('hourly_rate'),
            'daily_rate': guide_data.pop('daily_rate'),
            'experience_years': guide_data.pop('experience_years'),
            'bio': guide_data.pop('bio'),
            'average_rating': Decimal('4.5'),
            'total_trips': 50
        }
        
        user, created = User.objects.get_or_create(
            email=guide_data['email'],
            defaults={
                **guide_data,
                'user_type': 'guide',
                'is_verified': True,
                'is_approved': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create guide profile
            Guide.objects.get_or_create(
                user=user,
                defaults=guide_profile_data
            )
            print(f"✅ Guide {user.username} created")

def create_sample_agencies():
    """Create sample agencies"""
    print("Creating sample agencies...")
    
    agencies_data = [
        {
            'email': 'agency1@email.com',
            'username': 'adventure_tours',
            'first_name': 'Adventure',
            'last_name': 'Tours',
            'phone_number': '+1234567895',
            'company_name': 'Adventure Tours Inc.',
            'address': '123 Adventure St, Mountain View, CA',
            'website': 'https://adventuretours.com',
            'description': 'Premier adventure tourism company specializing in mountain and outdoor activities.'
        },
        {
            'email': 'agency2@email.com',
            'username': 'cultural_journeys',
            'first_name': 'Cultural',
            'last_name': 'Journeys',
            'phone_number': '+1234567896',
            'company_name': 'Cultural Journeys Ltd.',
            'address': '456 Heritage Ave, Historic City, NY',
            'website': 'https://culturaljourneys.com',
            'description': 'Specialized in cultural and heritage tours with expert local guides.'
        }
    ]
    
    for agency_data in agencies_data:
        agency_profile_data = {
            'company_name': agency_data.pop('company_name'),
            'address': agency_data.pop('address'),
            'website': agency_data.pop('website'),
            'description': agency_data.pop('description'),
            'average_rating': Decimal('4.3'),
            'total_bookings': 120
        }
        
        user, created = User.objects.get_or_create(
            email=agency_data['email'],
            defaults={
                **agency_data,
                'user_type': 'agency',
                'is_verified': True,
                'is_approved': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create agency profile
            Agency.objects.get_or_create(
                user=user,
                defaults=agency_profile_data
            )
            print(f"✅ Agency {agency_profile_data['company_name']} created")

def create_sample_packages():
    """Create sample packages"""
    print("Creating sample packages...")
    
    try:
        agency1 = Agency.objects.get(company_name='Adventure Tours Inc.')
        agency2 = Agency.objects.get(company_name='Cultural Journeys Ltd.')
        
        packages_data = [
            {
                'name': 'Mountain Adventure Trek',
                'description': 'A thrilling 5-day mountain trekking experience with stunning views and challenging trails.',
                'package_type': 'adventure',
                'agency': agency1,
                'duration_days': 5,
                'price': Decimal('899.00'),
                'max_people': 8,
                'included_services': ['Guide', 'Meals', 'Accommodation', 'Equipment'],
                'excluded_services': ['Flight', 'Insurance', 'Personal expenses'],
                'destinations': ['Mount Peak', 'Alpine Valley', 'Crystal Lake'],
                'itinerary': [
                    {'day': 1, 'activity': 'Arrival and base camp setup'},
                    {'day': 2, 'activity': 'Trek to first checkpoint'},
                    {'day': 3, 'activity': 'Summit attempt'},
                    {'day': 4, 'activity': 'Descent and exploration'},
                    {'day': 5, 'activity': 'Return journey'}
                ],
                'average_rating': Decimal('4.6'),
                'total_bookings': 25
            },
            {
                'name': 'Heritage City Tour',
                'description': 'Explore the rich cultural heritage and historical landmarks of the ancient city.',
                'package_type': 'cultural',
                'agency': agency2,
                'duration_days': 3,
                'price': Decimal('449.00'),
                'max_people': 15,
                'included_services': ['Professional Guide', 'Transportation', 'Entry Fees', 'Lunch'],
                'excluded_services': ['Hotel', 'Dinner', 'Shopping'],
                'destinations': ['Old Town', 'Heritage Museum', 'Ancient Temple', 'Royal Palace'],
                'itinerary': [
                    {'day': 1, 'activity': 'Historical city center tour'},
                    {'day': 2, 'activity': 'Museums and cultural sites'},
                    {'day': 3, 'activity': 'Traditional crafts and markets'}
                ],
                'average_rating': Decimal('4.4'),
                'total_bookings': 40
            }
        ]
        
        for package_data in packages_data:
            package, created = Package.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            if created:
                print(f"✅ Package '{package.name}' created")
    
    except Agency.DoesNotExist:
        print("❌ Agencies not found. Create agencies first.")

def main():
    """Create all sample data"""
    print("🚀 Creating sample data for Guide App...")
    print("=" * 50)
    
    create_sample_users()
    create_sample_guides()
    create_sample_agencies()
    create_sample_packages()
    
    print("\n" + "=" * 50)
    print("🏁 Sample data creation completed!")
    print("\nYou can now:")
    print("- Login as admin with: admin@guideapp.com / admin123")
    print("- Login as tourist with: john.doe@email.com / password123")
    print("- Login as agency with: agency1@email.com / password123")
    print("- Test the API endpoints with the sample data")

if __name__ == "__main__":
    main()
