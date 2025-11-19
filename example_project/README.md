# Nova2FA Example Project

This is a complete example Django project demonstrating Nova2FA integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

##### Install nova2fa in development mode from parent directory
```bash
cd ../ # To base DIR
pip install -e . # This installs the nova2fa folder as a package into the virtual env which then redirects to the base DIR as the sourse
cd example_project
```

3. Run migrations:
```bash
python manage.py makemigrations # Important, to apply nova2fa settings to migrations.
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit http://127.0.0.1:8000/ and login

## Testing 2FA

1. After logging in, navigate to "Security Settings"
2. Click "Enable Two-Factor Authentication"
3. Choose your preferred method (Email or Authenticator App)
4. Complete the setup process
5. Logout and login again to test 2FA verification

## Features Demonstrated

- User registration and login
- 2FA setup with both TOTP and Email methods
- Backup code generation and usage
- Method switching
- 2FA disabling
- Custom styled templates (basic Bootstrap styling)
