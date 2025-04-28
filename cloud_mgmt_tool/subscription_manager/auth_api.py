class AuthAPI:
    def __init__(self, provider):
        self.provider = provider

    def login_url(self):
        if self.provider == "Google":
            return "Redirect to Google OAuth (API key needed)"
        elif self.provider == "GitHub":
            return "Redirect to GitHub OAuth (API key needed)"
        else:
            return "Invalid auth provider"

# Example usage
google_auth = AuthAPI("Google")
print(google_auth.login_url())  # Output: Redirect to Google OAuth (API key needed)
