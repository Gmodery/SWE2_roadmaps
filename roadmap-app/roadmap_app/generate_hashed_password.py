import os
import django
from django.contrib.auth.hashers import make_password

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadmap_app.settings')
django.setup()

# Generate hashed password
raw_password = 'adminpassword'
hashed_password = make_password(raw_password)
print(f"Hashed password: {hashed_password}")
