from uncountable.core.client import Client
from uncountable.core.types import AuthDetailsOAuth

client = Client(
    base_url="https://app.uncountable.com",
    auth_details=AuthDetailsOAuth(refresh_token="x"),
)
