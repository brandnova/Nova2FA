# Running Tests for Nova2FA v1.1.0 (Linux)

## Quick Test Commands

Due to the Django project structure, here are the recommended ways to run tests:

### Option 1: Run Tests Without Django (Encryption Only)

```bash
cd /home/Nova/Desktop/Projects/Nova2FA-main
source .venv/bin/activate
python -m pytest tests/test_encryption.py -v -p no:django
```

### Option 2: Run Tests with Django (Recommended)

```bash
cd /home/Nova/Desktop/Projects/Nova2FA-main
source .venv/bin/activate

# Set PYTHONPATH and DJANGO_SETTINGS_MODULE
export PYTHONPATH=/home/Nova/Desktop/Projects/Nova2FA-main/example_project:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=example_project.settings

# Run tests
python -m pytest tests/ -v
```

### Option 3: Run Tests from Example Project Directory

```bash
cd /home/Nova/Desktop/Projects/Nova2FA-main/example_project
source ../.venv/bin/activate

# Run tests
python -m pytest ../tests/ -v --ds=example_project.settings
```

### Option 4: Install Package and Test

```bash
cd /home/Nova/Desktop/Projects/Nova2FA-main
source .venv/bin/activate

# Install package in development mode
pip install -e .

# Run tests
cd example_project
python manage.py test nova2fa
```

## Current Test Status

- ✅ **test_encryption.py** (8 tests) - No Django required
- ⚠️ **test_models.py** (13 tests) - Requires Django setup
- ⚠️ **test_methods.py** (10 tests) - Requires Django setup

## Troubleshooting

If you get "No module named 'example_project'":

1. Make sure you're in the correct directory
2. Set PYTHONPATH as shown in Option 2
3. Or use Option 3 to run from example_project directory

## Manual Testing with Example Project

For manual testing of the 2FA flows:

```bash
cd /home/Nova/Desktop/Projects/Nova2FA-main/example_project
source ../.venv/bin/activate
python manage.py migrate
python manage.py createsuperuser  # Create a test user
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/2fa/settings/` after logging in.
