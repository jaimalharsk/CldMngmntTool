import os
from dotenv import load_dotenv

# Load your .env file
dotenv_path = ".env"
load_dotenv(dotenv_path)

# List of expected environment variable names
expected_keys = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "AZURE_TENANT_ID",
    "GCP_PROJECT_ID",
    "GCP_CLIENT_EMAIL",
    "GCP_PRIVATE_KEY",
    "SOME_SERVICE_API_KEY",
    "ANOTHER_API_KEY",
]

# Diagnostic: Check which ones are missing
print("🔍 Checking environment variables from:", dotenv_path)
missing = []
for key in expected_keys:
    value = os.getenv(key)
    if not value:
        missing.append(key)
        print(f"❌ Missing: {key}")
    else:
        print(f"✅ Loaded: {key} -> {value[:4]}...")

if not missing:
    print("\n🎉 All required environment variables are loaded!")
else:
    print(f"\n⚠️ Total missing: {len(missing)}. Fix your {dotenv_path} file or check the load path.")
