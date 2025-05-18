# User Authentication API

This project implements a secure user authentication system using Django Rest Framework and JWT tokens.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the server:
```bash
python manage.py runserver
```

## API Endpoints

### 1. Register User
- **Method**: POST
- **URL**: `/api/auth/register/`
- **Request Body**:
```json
{
    "username": "example_user",
    "email": "user@example.com",
    "password": "secure_password123"
}
```
- **Response (201 Created)**:
```json
{
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
}
```

### 2. Login
- **Method**: POST
- **URL**: `/api/auth/login/`
- **Request Body**:
```json
{
    "username": "example_user",
    "password": "secure_password123"
}
```
- **Response (200 OK)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### 3. Refresh Token
- **Method**: POST
- **URL**: `/api/auth/token/refresh/`
- **Request Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```
- **Response (200 OK)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### 4. Get User Profile (Protected Route)
- **Method**: GET
- **URL**: `/api/auth/profile/`
- **Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbG...
```
- **Response (200 OK)**:
```json
{
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
}
```

## Error Responses

### Invalid Credentials (401 Unauthorized)
```json
{
    "detail": "No active account found with the given credentials"
}
```

### Token Required (401 Unauthorized)
```json
{
    "detail": "Authentication credentials were not provided"
}
```

### Invalid Token (401 Unauthorized)
```json
{
    "detail": "Token is invalid or expired"
}
``` 