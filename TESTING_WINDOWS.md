# Running Tests for Nova2FA v1.1.0 on Windows

## Prerequisites

- **Python 3.11+** installed and added to your `PATH`
- **Git Bash** or **PowerShell** (any terminal that supports Unix‑style commands)
- A virtual environment (recommended) to isolate dependencies
- The same source code checkout as on Linux (the repository is OS‑agnostic)

## 1. Set up the virtual environment

```powershell
# Navigate to the project root
cd C:\path\to\Nova2FA-main

# Create a virtual environment (once)
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1   # PowerShell
# or
.\.venv\Scripts\activate.bat   # Command Prompt
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
# If you use the optional dev requirements for testing
pip install -r requirements-dev.txt
```

## 3. Configure environment variables for Django

```powershell
# Adjust the path to your example project
$env:PYTHONPATH="C:\path\to\Nova2FA-main\example_project;$env:PYTHONPATH"
$env:DJANGO_SETTINGS_MODULE="example_project.settings"
```

## 4. Run the test suite

### Option A – Run all tests (recommended)

```powershell
python -m pytest tests/ -v
```

### Option B – Run a single test file (e.g., encryption only, no Django needed)

```powershell
python -m pytest tests\test_encryption.py -v -p no:django
```

### Option C – Run from the example project directory

```powershell
cd example_project
python -m pytest ..\tests\ -v --ds=example_project.settings
```

### Option D – Install the package in editable mode and use Django’s test runner

```powershell
pip install -e .
cd example_project
python manage.py test nova2fa
```

## 5. Common Windows‑specific issues & fixes

- **Line‑ending differences** – Ensure you commit files with LF (`git config core.autocrlf false`).
- **Path separators** – Use double backslashes (`\\`) or forward slashes (`/`) in commands; Python accepts both.
- **Virtual‑env activation** – The activation script differs (`Activate.ps1` for PowerShell, `activate.bat` for CMD).
- **Permissions** – If you see `PermissionError` when creating temporary files, run the terminal as Administrator or adjust the folder permissions.

## 6. Troubleshooting

- _"ModuleNotFoundError: No module named 'example_project'"_ – Verify `$env:PYTHONPATH` points to the `example_project` folder.
- _"django.core.exceptions.ImproperlyConfigured"_ – Ensure `DJANGO_SETTINGS_MODULE` is set correctly.
- _"Failed to collect test files"_ – Make sure `pytest` is installed (`pip install pytest`).

## 7. Manual testing (optional)

You can also run the development server on Windows to manually verify the UI:

```powershell
python manage.py migrate
python manage.py createsuperuser   # Follow prompts
python manage.py runserver
```

Then open `http://127.0.0.1:8000/2fa/settings/` in a browser.

---

**Happy testing!** If you encounter any OS‑specific quirks, feel free to open an issue on the repository.
