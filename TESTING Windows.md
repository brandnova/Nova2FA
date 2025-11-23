# Running Tests for Nova2FA v1.1.0 (Windows)

## Quick Test Commands

Because of the Django project layout, here are the recommended ways to run tests on Windows.

### Option 1: Run Tests Without Django (Encryption Only)

```powershell
cd C:\Users\Nova\Desktop\Projects\Nova2FA-main
.\.venv\Scripts\activate
python -m pytest tests\test_encryption.py -v -p no:django
```

### Option 2: Run Tests with Django (Recommended)

```powershell
cd C:\Users\Nova\Desktop\Projects\Nova2FA-main
.\.venv\Scripts\activate

# Set environment variables
$env:DJANGO_SETTINGS_MODULE = "example_project.settings"
$env:PYTHONPATH = "C:\Users\Ijeoma Jahsway\Desktop\Projects\Nova2FA\example_project;$env:PYTHONPATH"

# Run tests
python -m pytest tests\ -v
```

### Option 3: Run Tests from Example Project Directory

```powershell
cd C:\Users\Nova\Desktop\Projects\Nova2FA-main\example_project
..\ .venv\Scripts\activate

python -m pytest ..\tests\ -v --ds=example_project.settings
```

### Option 4: Install Package and Test

```powershell
cd C:\Users\Nova\Desktop\Projects\Nova2FA-main
.\.venv\Scripts\activate

pip install -e .

cd example_project
python manage.py test nova2fa
```

## Current Test Status

* ✅ **test_encryption.py** (8 tests) — Does not require Django
* ⚠️ **test_models.py** (13 tests) — Requires Django
* ⚠️ **test_methods.py** (10 tests) — Requires Django

## Troubleshooting

**If you see:** `ModuleNotFoundError: No module named 'example_project'`

Check the following:

1. Confirm you're in the correct directory
2. Ensure `PYTHONPATH` is set correctly (see Option 2)
3. Or run from the `example_project` directory (Option 3)

## Manual Testing with the Example Project

```powershell
cd C:\Users\Nova\Desktop\Projects\Nova2FA-main\example_project
..\ .venv\Scripts\activate

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/2fa/settings/` after logging in.
