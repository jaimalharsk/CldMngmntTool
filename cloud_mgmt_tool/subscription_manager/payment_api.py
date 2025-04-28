import os

class PaymentAPI:
    def __init__(self, provider):
        self.provider = provider

    def create_subscription(self, user_email):
        if self.provider == "Stripe":
            return f"Subscription created for {user_email} via Stripe (API key needed)"
        elif self.provider == "PayPal":
            return f"Subscription created for {user_email} via PayPal (API key needed)"
        else:
            return "Invalid payment provider"

# Example usage
stripe_api = PaymentAPI("Stripe")
print(stripe_api.create_subscription("test@example.com"))
# Output: Subscription created for test@example.com via Stripe (API key needed)
