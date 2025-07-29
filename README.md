# Guide App - Tourist & Agency Platform

## Overview

A comprehensive Django REST API platform that connects tourists with travel agencies and guides. The application supports three main user types: **Tourists**, **Agencies**, and **Admins**, each with distinct workflows and capabilities.

## 🏗️ Architecture & User Flow

### App Entry Point
When users open the app, they are presented with a mode selection interface:
- **Tourist Mode**: For travelers looking to book services
- **Agency Mode**: For travel agencies managing their services

### 👤 Tourist Flow

1. **Registration/Login**: Tourists register and login to access the platform
2. **Profile Management**: Create and update personal profiles
3. **Browse Options**: Homepage displays three main categories:
   - **Packages**: Pre-designed tour packages
   - **Guides**: Individual tour guides
   - **Agencies**: Travel agencies
4. **Detailed Views**:
   - **Package Selection**: View agencies offering specific packages with pricing
   - **Guide Selection**: View guide ratings, bio, agencies they're registered with, and places they cover
   - **Agency Selection**: View agency's guides, packages, and ratings
5. **Booking**: Make bookings for packages, guides, or agencies
6. **Rating**: Rate and review services after completion

### 🏢 Agency Flow

1. **Registration/Login**: Agencies register (requires admin approval) and login
2. **Profile Management**: Update company information and details
3. **Service Management**:
   - **Register Guides**: Add guides to their network
   - **Create Packages**: Design and publish tour packages
   - **Manage Content**: Update all agency-related information
4. **Booking Management**: View and manage all bookings
5. **Pending Approval**: New agencies must wait for admin verification

### 👨‍💼 Admin Flow

1. **Agency Verification**: Review and approve/reject agency registrations
2. **Platform Oversight**: Monitor all platform activities

## 🗄️ Database Models

### Core User Models
- **User**: Extended Django user with user types (tourist, guide, agency, admin)
- **Tourist**: Tourist-specific profile information
- **Guide**: Guide profiles with ratings, specializations, and rates
- **Agency**: Agency profiles with company information and managed guides

### Service Models
- **Package**: Tour packages created by agencies
- **Booking**: Booking records for packages/guides/agencies
- **Rating**: Rating and review system for all services

## 🚀 API Endpoints

### Authentication
- `POST /auth/register/` - User registration with user type selection
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `GET /auth/profile/` - Get user profile
- `POST /auth/google_login/` - Google OAuth login
- `POST /auth/facebook_login/` - Facebook OAuth login

### Profile Management
- `GET/PUT /profile/tourist/` - Tourist profile management
- `GET/PUT /profile/guide/` - Guide profile management
- `GET/PUT /profile/agency/` - Agency profile management

### Public Browse (Tourist Access)
- `GET /homepage/content/` - Homepage content (featured packages, guides, agencies)
- `GET /packages/` - List all packages with filtering and search
- `GET /packages/{id}/agencies/` - Get agencies offering similar packages
- `GET /packages/{id}/ratings/` - Get package ratings
- `GET /guides/` - List all guides with filtering and search
- `GET /guides/{id}/agencies/` - Get agencies this guide works with
- `GET /guides/{id}/ratings/` - Get guide ratings
- `GET /agencies/` - List all agencies with filtering and search
- `GET /agencies/{id}/guides/` - Get guides managed by agency
- `GET /agencies/{id}/packages/` - Get packages offered by agency
- `GET /agencies/{id}/ratings/` - Get agency ratings

### Tourist Services
- `GET/POST/PUT/DELETE /tourist/bookings/` - Manage tourist bookings
- `GET/POST/PUT/DELETE /tourist/ratings/` - Manage tourist ratings

### Agency Management
- `GET/POST /agency/manage/packages/` - Manage agency packages
- `GET/POST /agency/manage/guides/` - Manage agency guides
- `GET /agency/manage/bookings/` - View agency bookings

### Admin Functions
- `GET /admin/pending_agencies/` - Get agencies pending approval
- `POST /admin/approve_agency/` - Approve an agency
- `POST /admin/reject_agency/` - Reject an agency

## 🔧 Key Features

### Enhanced User Registration
- User type selection during registration (Tourist/Agency)
- Agencies require admin approval before activation
- Social login support (Google/Facebook)

### Comprehensive Search & Filter
- Package filtering by type, duration, price, ratings
- Guide filtering by specializations, languages, rates
- Agency filtering by location, ratings, services

### Multi-dimensional Booking System
- Book packages directly
- Book individual guides
- Book through agencies
- Automatic price calculation based on booking type

### Rating & Review System
- Rate packages, guides, and agencies separately
- Average rating calculation
- Review comments and feedback

### Agency Management Dashboard
- Manage guide network
- Create and update packages
- Track all bookings
- Profile and company information management

### Admin Panel
- Agency verification workflow
- Platform oversight and management
- User management capabilities

## 🆕 What's New & Changed

### Models Added
1. **Package Model**: Complete tour package management
2. **Booking Model**: Multi-type booking system
3. **Rating Model**: Comprehensive rating system

### Enhanced Models
- **Agency**: Added ratings, booking count, and description fields
- **User**: Enhanced user type system with proper approval workflows

### New API Endpoints
- Complete CRUD operations for all new models
- Advanced filtering and search capabilities
- Relationship-based data retrieval (e.g., guides per agency)

### Authentication Improvements
- User type selection during registration
- Agency approval workflow
- Enhanced profile management

### Business Logic
- Automatic price calculation for bookings
- Rating aggregation system
- Multi-dimensional search and discovery

## 🛠️ Technical Stack

- **Backend**: Django REST Framework
- **Database**: SQLite (default) / PostgreSQL (production)
- **Authentication**: JWT with social login support
- **API Documentation**: DRF built-in browsable API
- **Deployment**: Poetry for dependency management

## 📱 Frontend Integration Points

### Mode Selection Interface
The frontend should implement a landing page where users choose between:
- Tourist Mode (leads to tourist registration/login)
- Agency Mode (leads to agency registration/login)

### Tourist Interface
- Homepage with packages, guides, and agencies
- Detailed view pages for each service type
- Booking interface with date selection and pricing
- Rating interface for completed bookings

### Agency Interface
- Dashboard for managing guides and packages
- Booking management interface
- Profile and company information forms

### Admin Interface
- Agency approval dashboard
- Platform analytics and management

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   poetry install
   ```

2. **Run Migrations**:
   ```bash
   poetry run python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   poetry run python manage.py createsuperuser
   ```

4. **Run Development Server**:
   ```bash
   poetry run python manage.py runserver
   ```

5. **Access API**:
   - API Root: `http://localhost:8000/`
   - Admin Panel: `http://localhost:8000/admin/`

## 📊 Data Flow Examples

### Tourist Booking a Package
1. Tourist browses `/packages/`
2. Selects a package and views details
3. Creates booking via `POST /tourist/bookings/`
4. After completion, rates via `POST /tourist/ratings/`

### Agency Creating a Package
1. Agency registers and gets admin approval
2. Agency logs in and creates package via `POST /agency/manage/packages/`
3. Package appears in public listings
4. Tourists can book the package

### Guide Registration with Agency
1. Guide creates account with guide user type
2. Agency adds guide via `POST /agency/manage/guides/`
3. Guide appears in agency's guide list
4. Tourists can book guide through agency

This platform provides a complete ecosystem for tourism service management with clear separation of concerns and comprehensive functionality for all user types.
