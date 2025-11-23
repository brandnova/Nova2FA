"""
Root conftest.py to configure Django for pytest.
"""
import os
import sys
import django
from django.conf import settings

# Add example_project to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'example_project'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')

# Setup Django
django.setup()
