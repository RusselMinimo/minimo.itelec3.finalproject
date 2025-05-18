# E-Commerce API Documentation

This project implements a RESTful API for an e-commerce system with authentication and CRUD operations for Categories, Products, and Orders.

## Project Structure

The project consists of two main interfaces:

1. **Authentication Interface** - The main page at `/` for user registration and login.
2. **CRUD Testing Interface** - A separate interface at `/crud/` for testing CRUD operations.

## Getting Started

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Run the development server:
```
python manage.py runserver
```
5. Navigate to `http://localhost:8000/` in your browser.

### Usage Flow

1. Register a new user account or log in with existing credentials
2. After login, access tokens are stored in localStorage
3. Click "Access CRUD Interface" to navigate to the CRUD testing interface
4. Perform CRUD operations on Categories, Products, and Orders

## Authentication Endpoints

### Register
- **Method**: POST
- **URL**: `/api/auth/register/`
- **Body**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password2": "string"
}
```
- **Response**:
```json
{
    "username": "string",
    "email": "string"
}
```

### Login
- **Method**: POST
- **URL**: `/api/auth/login/`
- **Body**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **Response**:
```json
{
    "access": "string",
    "refresh": "string"
}
```

### Token Refresh
- **Method**: POST
- **URL**: `/api/auth/token/refresh/`
- **Body**:
```json
{
    "refresh": "string"
}
```
- **Response**:
```json
{
    "access": "string"
}
```

## Category Endpoints

All category endpoints require authentication. Include the JWT token in the Authorization header:
`Authorization: Bearer <access_token>`

### List Categories
- **Method**: GET
- **URL**: `/api/categories/`
- **Response**:
```json
[
    {
        "id": 1,
        "name": "string",
        "description": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
]
```

### Create Category
- **Method**: POST
- **URL**: `/api/categories/`
- **Body**:
```json
{
    "name": "string",
    "description": "string"
}
```

### Get Category
- **Method**: GET
- **URL**: `/api/categories/{id}/`

### Update Category
- **Method**: PUT/PATCH
- **URL**: `/api/categories/{id}/`
- **Body**:
```json
{
    "name": "string",
    "description": "string"
}
```

### Delete Category
- **Method**: DELETE
- **URL**: `/api/categories/{id}/`

## Product Endpoints

All product endpoints require authentication.

### List Products
- **Method**: GET
- **URL**: `/api/products/`
- **Response**:
```json
[
    {
        "id": 1,
        "name": "string",
        "description": "string",
        "price": "decimal",
        "category": 1,
        "category_name": "string",
        "stock": "integer",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
]
```

### Create Product
- **Method**: POST
- **URL**: `/api/products/`
- **Body**:
```json
{
    "name": "string",
    "description": "string",
    "price": "decimal",
    "category": "integer",
    "stock": "integer"
}
```

### Get Product
- **Method**: GET
- **URL**: `/api/products/{id}/`

### Update Product
- **Method**: PUT/PATCH
- **URL**: `/api/products/{id}/`
- **Body**: Same as Create Product

### Delete Product
- **Method**: DELETE
- **URL**: `/api/products/{id}/`

### Get Category Products
- **Method**: GET
- **URL**: `/api/products/category_products/{category_id}/`

## Order Endpoints

All order endpoints require authentication. Regular users can only access their own orders.

### List Orders
- **Method**: GET
- **URL**: `/api/orders/`
- **Response**:
```json
[
    {
        "id": 1,
        "user": {
            "id": 1,
            "username": "string",
            "email": "string"
        },
        "product": 1,
        "product_name": "string",
        "product_price": "decimal",
        "quantity": "integer",
        "status": "string",
        "total_price": "decimal",
        "shipping_address": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
]
```

### Create Order
- **Method**: POST
- **URL**: `/api/orders/`
- **Body**:
```json
{
    "product": "integer",
    "quantity": "integer",
    "shipping_address": "string"
}
```

### Get Order
- **Method**: GET
- **URL**: `/api/orders/{id}/`

### Update Order Status
- **Method**: PATCH
- **URL**: `/api/orders/{id}/update_status/`
- **Body**:
```json
{
    "status": "string" // One of: pending, processing, shipped, delivered, cancelled
}
```

### Delete Order
- **Method**: DELETE
- **URL**: `/api/orders/{id}/`

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 400 Bad Request
```json
{
    "field_name": [
        "Error message"
    ]
}
```

## Testing the API

1. Register a new user account
2. Login to get the access token
3. Use the access token in the Authorization header for all subsequent requests
4. Create categories and products
5. Create orders and manage their status

A web interface is provided at the root URL (`/`) for testing the API endpoints. 