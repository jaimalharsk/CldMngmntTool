import os

AZURE_CONFIG = {
    "CLIENT_ID": os.getenv("79efe962-b1ad-4d66-aea7-8db30d68f0e"),
    "TENANT_ID": os.getenv("59525466-51eb-4e32-a991-8a80fa2821b4"),
    "CLIENT_SECRET": os.getenv("-Qt8Q~Pdb00azJKHXziwvfWHnoiKE15uzQWtOcrH"),
    "AUTHORITY": f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}",
    "REDIRECT_URI": "http://localhost:8000/accounts/login/callback/",
}

class CloudAPI:
    def __init__(self, provider):
        self.provider = provider.lower()

    def list_resources(self):
        if self.provider == "aws":
            return "AWS API setup required"

        elif self.provider == "azure":
            missing_fields = [key for key, value in AZURE_CONFIG.items() if not value]
            if missing_fields:
                missing_str = ", ".join(missing_fields)
                return f"Azure configuration incomplete. Missing: {missing_str}"
            return "Azure API setup required"

        elif self.provider == "gcp":
            return "GCP API setup required"

        else:
            return "Invalid provider"


# Example usage
aws_api = CloudAPI("AWS")
print(aws_api.list_resources())  # AWS API setup required

azure_api = CloudAPI("azure")
print(azure_api.list_resources())  # Azure API setup required or config error

gcp_api = CloudAPI("gcp")
print(gcp_api.list_resources())  # GCP API setup required


def test_cloud_api():
    aws_api = CloudAPI("aws")
    azure_api = CloudAPI("azure")
    gcp_api = CloudAPI("gcp")
    invalid_api = CloudAPI("digitalocean")

    assert aws_api.list_resources() == "AWS API setup required", "AWS check failed!"

    # For Azure, depends if your AZURE_CONFIG values are set or not
    if all(AZURE_CONFIG.values()):
        assert azure_api.list_resources() == "Azure API setup required", "Azure check (complete) failed!"
    else:
        assert "Azure configuration incomplete" in azure_api.list_resources(), "Azure check (incomplete) failed!"

    assert gcp_api.list_resources() == "GCP API setup required", "GCP check failed!"
    assert invalid_api.list_resources() == "Invalid provider", "Invalid provider check failed!"

    print("✅ All tests passed!")


if __name__ == "__main__":
    test_cloud_api()

