# OJT Tracker System

A comprehensive Django-based web application for managing On-the-Job Training (OJT) programs, student placements, and tracking progress.

## Project Structure

```
minimo.itelec3.finalproject/
├── auth_project/              # Main Django project configuration
│   ├── settings.py           # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── authentication/           # Authentication app
│   ├── models.py            # User profile models
│   ├── views.py             # Authentication views
│   ├── forms.py             # Authentication forms
│   ├── serializers.py       # API serializers
│   ├── urls.py              # Authentication URLs
│   └── templates/           # Authentication templates
├── ojt_tracker/             # Main OJT tracking app
│   ├── models.py            # Core business models
│   ├── views.py             # Web and API views
│   ├── forms.py             # Django forms
│   ├── serializers.py       # DRF serializers
│   ├── admin.py             # Django admin configuration
│   ├── urls.py              # App URLs
│   └── templates/           # App templates
├── media/                   # User uploaded files
├── staticfiles/             # Collected static files
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── db.sqlite3              # SQLite database
```

## Features

### User Management
- **Multi-role Authentication**: Students, Faculty, and Administrators
- **Profile Management**: Comprehensive user profiles with role-specific information
- **Secure Authentication**: JWT-based API authentication and session-based web authentication

### Student Features
- **Profile Management**: Personal information, academic details, and profile pictures
- **OJT Requests**: Submit and track OJT placement requests
- **Placement Tracking**: View assigned company and supervisor details
- **Activity Logging**: Daily activity and learning outcome tracking
- **Attendance Management**: Check-in/check-out with break time tracking
- **Dashboard**: Personalized dashboard with key metrics and quick actions

### Faculty Features
- **Student Supervision**: Monitor assigned students' progress
- **Evaluation System**: Create and manage student evaluations
- **Report Generation**: Generate various reports (weekly, monthly, evaluation summaries)
- **Student Communication**: Messaging system for student interaction
- **Dashboard**: Faculty-specific dashboard with supervision overview

### Administrator Features
- **Company Management**: Add and manage partner companies
- **Program Management**: Create and manage OJT programs
- **Placement Management**: Assign students to companies and supervisors
- **Request Management**: Review and approve/reject OJT requests
- **System Overview**: Comprehensive dashboard with system-wide statistics

### API Features
- **RESTful API**: Complete REST API for all major functionalities
- **JWT Authentication**: Secure API access with token-based authentication
- **Filtering and Search**: Advanced filtering and search capabilities
- **Pagination**: Efficient data pagination for large datasets

## Technology Stack

- **Backend**: Django 5.0.2, Django REST Framework 3.14.0
- **Database**: SQLite (development), easily configurable for PostgreSQL/MySQL
- **Authentication**: Django's built-in auth + JWT for API
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **File Handling**: Pillow for image processing
- **API Documentation**: Django REST Framework browsable API

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd minimo.itelec3.finalproject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Web Interface
- Access the application at `http://localhost:8000`
- Login page: `http://localhost:8000/auth/login/`
- Admin interface: `http://localhost:8000/admin/`

### API Endpoints
- API root: `http://localhost:8000/app/api/`
- Authentication: `http://localhost:8000/auth/api/`
- API documentation available through Django REST Framework browsable API

### User Roles
1. **Students**: Can manage profiles, submit OJT requests, log activities, and track attendance
2. **Faculty**: Can supervise students, create evaluations, and generate reports
3. **Administrators**: Can manage the entire system, companies, programs, and placements

## Configuration

### Environment Variables
Create a `.env` file for production settings:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
```

### Media Files
- User uploads are stored in the `media/` directory
- Configure `MEDIA_ROOT` and `MEDIA_URL` in settings for production

### Static Files
- Static files are collected in `staticfiles/` directory
- Run `python manage.py collectstatic` before deployment

## Security Features

- CSRF protection enabled
- Secure password validation
- Role-based access control
- JWT token authentication for API
- File upload restrictions
- XSS protection headers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for educational purposes as part of the ITELEC3 final project.

## Support

For support or questions, please contact the development team or create an issue in the repository. 