import os
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file into environment variables

# Azure Configuration
AZURE_CONFIG = {
    "CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
    "TENANT_ID": os.getenv("AZURE_TENANT_ID"),
    "CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
    "AUTHORITY": f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}",
    "REDIRECT_URI": "http://localhost:8000/accounts/login/callback/",
}

# AWS Configuration
AWS_CONFIG = {
    "ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "REGION": os.getenv("AWS_REGION", "us-east-1"),
}

class CloudAPI:
    def __init__(self, provider):
        self.provider = provider.lower()

    def list_resources(self):
        if self.provider == "aws":
            if not AWS_CONFIG["ACCESS_KEY_ID"] or not AWS_CONFIG["SECRET_ACCESS_KEY"]:
                return "AWS API keys missing or incomplete."
            return f"AWS API setup complete for region {AWS_CONFIG['REGION']}"

        elif self.provider == "azure":
            missing_fields = [key for key, value in AZURE_CONFIG.items() if not value]
            if missing_fields:
                return f"Azure configuration incomplete. Missing: {', '.join(missing_fields)}"
            return "Azure API setup required"

        elif self.provider == "gcp":
            return "GCP API setup required"

        else:
            return "Invalid provider"

def test_cloud_api():
    aws_api = CloudAPI("aws")
    azure_api = CloudAPI("azure")
    gcp_api = CloudAPI("gcp")
    invalid_api = CloudAPI("digitalocean")

    aws_result = aws_api.list_resources()
    assert ("AWS API setup complete" in aws_result) or ("AWS API keys missing" in aws_result), "AWS check failed!"

    if all(AZURE_CONFIG.values()):
        assert azure_api.list_resources() == "Azure API setup required", "Azure check (complete) failed!"
    else:
        assert "Azure configuration incomplete" in azure_api.list_resources(), "Azure check (incomplete) failed!"

    assert gcp_api.list_resources() == "GCP API setup required", "GCP check failed!"
    assert invalid_api.list_resources() == "Invalid provider", "Invalid provider check failed!"

    print("✅ All tests passed!")

if __name__ == "__main__":
    test_cloud_api()
