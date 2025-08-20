# RoWifi Python Client

`rowifi-python` is a Python client for the [RoWifi API](https://rowifi.xyz/docs/api).  
It allows you to interact with RoWifi services, including managing members, denylists, ranks, and more.

## Features

- Easy access to RoWifi endpoints
- Pydantic models for structured responses
- Supports authentication via API token

## Installation

```bash
pip install rowifi-python
```
## Usage

```python
from rowifi import RoWifiClient

# Initialize client with your API token
client = RoWifiClient(token="your_api_token_here")

# Example: fetch a user by Roblox ID
user_data = client.get_user(user_id=123456)
print(user_data)

# Example: fetch the denylist
denylist = client.get_denylist()
print(denylist)
```
## Notes

All methods are synchronous.

Replace "your_api_token_here" with your actual RoWifi API token.