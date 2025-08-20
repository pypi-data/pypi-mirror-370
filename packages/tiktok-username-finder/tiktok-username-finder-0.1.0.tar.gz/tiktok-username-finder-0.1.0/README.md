# TikTok Username Finder

A Python library to find TikTok usernames by email.

## Installation

```bash
pip install tiktok-username-finder
```

## Usage

```python
from tiktok_username_finder import find_tiktok_username

email = "test@example.com"
result = find_tiktok_username(email)

if result["status"] == "success":
    print(f"Username: {result["username"]}")
else:
    print(f"Error: {result["message"]}")
```
```


