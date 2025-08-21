# Nilva Django Auth

A comprehensive Django authentication package that uses Django REST Framework (DRF) and JWT tokens for secure, flexible authentication in Django applications.

## Features

- **JWT Token Authentication**: Secure authentication using JSON Web Tokens
- **Session Management**: Efficient handling of user sessions
- **Username/Password Authentication**: Secure authentication using username and password
- **Login Endpoint**: Simple API for user login
- **Logout Endpoint**: API for user logout
- **Logout All Devices**: Ability to terminate all active sessions
- **Token Refresh**: Automatic token refresh mechanism
- **Highly Configurable**: Customize the authentication flow to suit your needs
- **DRF Integration**: Seamless integration with Django REST Framework

## Installation

You can install the package using pip:

```bash
pip install nilva-django-auth
```

Or using uv (recommended):

```bash
uv pip install nilva-django-auth
```

## Development Setup

This project uses uv for dependency management. To set up a development environment:

1. Install uv:

```bash
pip install uv
```

2. Clone the repository:

```bash
git clone https://github.com/nilva/nilva-django-auth.git
cd nilva-django-auth
```

3. Install development dependencies:

```bash
uv pip install -e ".[dev]"
# or
uv pip install -r requirements-dev.txt
```

## Running Tests

You can run all tests using the provided bash script:

```bash
./run_tests.sh
```

The script supports several options:

```bash
# Run all tests
./run_tests.sh

# Run tests with coverage report
./run_tests.sh -c

# Run tests in verbose mode
./run_tests.sh -v

# Run a specific test file
./run_tests.sh tests/test_authentication.py

# Run a specific test
./run_tests.sh tests/test_authentication.py::AuthenticationTests::test_login

# Show help
./run_tests.sh -h
```

Alternatively, you can use pytest directly:

To run the tests:

```bash
python -m pytest
```

To run the tests with coverage:

```bash
python -m pytest --cov=nilva_django_auth
```

To run a specific test:

```bash
python -m pytest tests/test_authentication.py::AuthenticationTests::test_login
```

Note: Make sure you have installed the development dependencies first:

```bash
pip install -r requirements-dev.txt
# or
uv pip install -e ".[dev]"
```

## Quick Start

1. Add `nilva_django_auth` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'nilva_django_auth',
    'nilva_django_auth',
    # ...
]
```

2. Apply migrations to create the necessary database tables:

```bash
python manage.py migrate nilva_django_auth
python manage.py migrate nilva_django_auth
```

3. Configure the authentication backend in `settings.py`:

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'nilva_django_auth.simplejwt.authentication.JWTAuthentication',
    ),
}

# Nilva Django Auth settings
NILVA_AUTH = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # 5 minutes (default)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 1 day (default)
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_COOKIE_NAME': 'auth',
    'REFRESH_COOKIE_NAME': 'refresh',
    'USE_COOKIES': False,  # Set to True to use cookies instead of headers
    'SECURE_COOKIES': True,  # Use secure cookies in production
}
```

4. Include the authentication URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('auth/', include('nilva_django_auth.urls')),
    # ...
]
```


## API Endpoints

- **Login**: `POST /auth/login/`
  - Request: `{"username": "user", "password": "pass"}`
  - Response: `{"access": "token", "refresh": "token"}`

- **Refresh Token**: `POST /auth/refresh/`
  - Request: `{"refresh": "token"}`
  - Response: `{"access": "new-token"}`

- **Verify Token**: `POST /auth/verify/`
  - Request: `{"token": "token"}`
  - Response: `{}` (200 OK if token is valid, error otherwise)

- **Logout**: `POST /auth/logout/`
  - Request: `{"refresh": "token"}`
  - Response: `{"success": "Successfully logged out"}`

- **Logout All**: `POST /auth/logout-all/`
  - Request: `{}`
  - Response: `{"success": "Successfully logged out from all devices"}`

- **List Sessions**: `GET /auth/sessions/`
  - Response: `[{"id": 1, "device_info": "Chrome on Windows", "ip_address": "192.168.1.1", "created_at": "2023-01-01T12:00:00Z", "last_activity": "2023-01-01T13:00:00Z", "is_active": true}]`

## Advanced Configuration

The package is highly configurable. Here are some advanced configuration options:

```python
from datetime import timedelta

NILVA_AUTH = {
    # Basic settings
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # 5 minutes (default)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 1 day (default)


    # Token settings
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Cookie settings
    'USE_COOKIES': False,
    'AUTH_COOKIE_NAME': 'auth',
    'REFRESH_COOKIE_NAME': 'refresh',
    'SECURE_COOKIES': True,
    'HTTPONLY_COOKIES': True,
    'SAMESITE_COOKIES': 'Lax',

    # Custom user model
    'USER_MODEL': 'auth.User',

    # Token serializers (SimpleJWT)
    'TOKEN_OBTAIN_SERIALIZER': 'nilva_django_auth.simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'nilva_django_auth.simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'nilva_django_auth.simplejwt.serializers.TokenVerifySerializer',
    'TOKEN_BLACKLIST_SERIALIZER': 'nilva_django_auth.simplejwt.serializers.TokenBlacklistSerializer',
    'TOKEN_BLACKLIST_ALL_SERIALIZER': 'nilva_django_auth.simplejwt.serializers.TokenBlacklistAllSerializer',
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
