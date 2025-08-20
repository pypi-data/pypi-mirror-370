import os
from dotenv import load_dotenv
import ethereal

# Read the environment variables from the .env file
# Ensure you have set the following:
# - BASE_URL: API URL for Ethereal
# - RPC_URL: RPC URL for the blockchain network
# - PRIVATE_KEY: Private key for the account
load_dotenv(override=True)

# Initialize the client
client = ethereal.RESTClient(
    {
        "base_url": os.getenv("BASE_URL") or "https://api.etherealtest.net",
        "chain_config": {
            "private_key": os.getenv("PRIVATE_KEY"),
            "rpc_url": os.getenv("RPC_URL"),
        },
    }
)

print("""
Development environment ready! RESTClient is available for use as 'client'

Try commands like:
- client.list_products()
- client.list_subaccounts()
""")
