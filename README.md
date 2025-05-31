# On-the-Job Trainee Tracker

A comprehensive Django-based web application designed to help educational institutions efficiently monitor and evaluate their students' internship (OJT) progress.

## Project Overview

This system provides real-time tracking of trainee activities, attendance, and performance with automated report generation and communication features between students and faculty.

## Key Features

- **Secure Authentication**: Role-based access control for students and faculty
- **Dashboard System**: Customized dashboards based on user roles
- **Activity Logging**: Students can log daily activities and learning outcomes
- **Attendance Tracking**: Comprehensive attendance monitoring with verification
- **Performance Evaluation**: Faculty can evaluate students with detailed feedback
- **Automated Reports**: Weekly and monthly report generation
- **Messaging System**: Built-in communication between students and faculty
- **Company Management**: Track OJT companies and placements

## Technical Stack

- **Backend**: Django 5.0.2 (Python)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **API**: Django REST Framework with JWT authentication
- **Frontend**: Django Templates with Bootstrap
- **Authentication**: Django's built-in auth system with custom roles

## Models Structure

The application includes 9 core models with proper relationships:

1. **UserRole** - Manages user role assignments (student/faculty/admin)
2. **Company** - OJT partner companies information
3. **OJTProgram** - Academic programs with OJT requirements
4. **Student** - Student profiles and program enrollment
5. **Faculty** - Faculty profiles and supervision assignments
6. **OJTPlacement** - Student-company placement records
7. **ActivityLog** - Daily activity tracking with approval workflow
8. **Attendance** - Attendance records with verification
9. **Evaluation** - Performance evaluations with detailed scoring
10. **Message** - Internal messaging system
11. **Report** - Automated report generation and distribution

## API Endpoints

Each model provides comprehensive REST API endpoints:

- **GET** `/api/model/` - List all records
- **POST** `/api/model/` - Create new record
- **GET** `/api/model/{id}/` - Retrieve specific record
- **PUT/PATCH** `/api/model/{id}/` - Update record
- **DELETE** `/api/model/{id}/` - Delete record

Plus custom actions for:
- Dashboard data aggregation
- Report generation
- Approval workflows
- Analytics and statistics

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd minimo.itelec3.finalproject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
minimo.itelec3.finalproject/
├── auth_project/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/         # User authentication app
├── ojt_tracker/           # Main OJT tracking app
│   ├── models.py          # Core data models
│   ├── views.py           # API views and template views
│   ├── serializers.py     # REST API serializers
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin interface
│   └── templates/         # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Recent Cleanup & Optimizations

The project has been thoroughly cleaned and optimized:

### ✅ Fixed Issues
- **Added missing dependency**: `django-filter==23.5` for API filtering
- **Fixed import errors**: Added missing `DashboardFacultySerializer`
- **Resolved URL conflicts**: Removed unused app references
- **Added missing settings**: `STATIC_ROOT` for production deployment

### 🗑️ Removed Unused Code
- **Deleted unused apps**: Removed `frontend` and `api` apps containing unrelated e-commerce models
- **Cleaned up imports**: Removed unused imports and dependencies
- **Removed unused files**: Deleted orphaned template files and media files
- **Streamlined settings**: Removed references to unused applications

### 📦 Current Dependencies
```
Django==5.0.2
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
python-dotenv==1.0.1
django-cors-headers==4.3.1
Pillow==10.2.0
django-filter==23.5
```

## Usage

### For Students
1. Login with student credentials
2. View dashboard with OJT progress overview
3. Log daily activities and learning outcomes
4. Check attendance records
5. View evaluations and feedback
6. Communicate with supervisors

### For Faculty
1. Login with faculty credentials
2. Monitor supervised students' progress
3. Approve activity logs
4. Record attendance verification
5. Create performance evaluations
6. Generate progress reports

### For Administrators
1. Manage companies and programs
2. Create OJT placements
3. Oversee system-wide analytics
4. Generate institutional reports

## Security Features

- JWT-based authentication
- Role-based access control
- CSRF protection
- SQL injection protection
- XSS protection
- File upload validation

## Production Deployment

The application is production-ready with:
- Static file configuration
- Security headers
- Database optimization
- Error handling
- Caching configuration

## Support

For technical issues or questions about the OJT Tracker system, please refer to the Django documentation or contact the development team.

---

**Project Status**: ✅ Production Ready
**Last Updated**: January 2025
**Django Version**: 5.0.2 