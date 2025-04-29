import os
import importlib
from dotenv import load_dotenv

print("🔍 Validating environment setup...\n")

# 1. Load .env
if load_dotenv(dotenv_path="keys.env"):
    print("✅ keys.env loaded successfully.\n")
else:
    print("❌ keys.env not found or not loaded.\n")

# 2. Check required environment variables
REQUIRED_VARS = [
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION",
    "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"
]

print("🔐 Environment Variables:")
for var in REQUIRED_VARS:
    val = os.getenv(var)
    if val:
        print(f"✅ {var} loaded.")
    else:
        print(f"❌ {var} is missing!")

# 3. Check required Python packages
print("\n📦 Checking installed packages:")
required_packages = ["django_extensions", "dotenv"]
for pkg in required_packages:
    try:
        importlib.import_module(pkg)
        print(f"✅ Package '{pkg}' is installed.")
    except ImportError:
        print(f"❌ Package '{pkg}' is NOT installed!")

# 4. Check if django_extensions is in settings
try:
    from django.conf import settings
    if not settings.configured:
        from django.core.wsgi import get_wsgi_application
        get_wsgi_application()

    if 'django_extensions' in settings.INSTALLED_APPS:
        print("\n⚙️  'django_extensions' is in INSTALLED_APPS ✅")
    else:
        print("\n⚠️  'django_extensions' is MISSING in INSTALLED_APPS ❌")

except Exception as e:
    print(f"\n⚠️  Unable to check settings.py: {e}")
