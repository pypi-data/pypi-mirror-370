from uncountable.core.client import Client
from uncountable.core.types import AuthDetailsApiKey

client = Client(
    base_url="https://app.uncountable.com",
    auth_details=AuthDetailsApiKey(api_id="x", api_secret_key="x"),
)
