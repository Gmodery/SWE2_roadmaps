import os
import django
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadmap_app.settings')
django.setup()

raw_password = 'adminpassword123'
hashed_password = make_password(raw_password)
print(f"Hashed password: {hashed_password}")
