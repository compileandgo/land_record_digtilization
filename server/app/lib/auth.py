import json
import os
from pathlib import Path
from google.oauth2 import service_account

def get_credentials():
    creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")
    
    if not creds_env:
        # Fallback to local credentials.json file
        for candidate in ["credentials.json", "server/credentials.json", "../credentials.json"]:
            path = Path(candidate)
            if path.exists():
                return service_account.Credentials.from_service_account_file(str(path))
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set and credentials.json file not found.")

    # If creds_env is a file path that exists directly
    if os.path.exists(creds_env):
        return service_account.Credentials.from_service_account_file(creds_env)

    # Otherwise parse JSON string
    try:
        data = json.loads(creds_env)
    except Exception as e:
        raise ValueError(f"Failed to parse GOOGLE_CREDENTIALS_JSON: {e}")

    # Un-nest double-encoded JSON string if string was enclosed in extra quotes
    while isinstance(data, str):
        if os.path.exists(data):
            return service_account.Credentials.from_service_account_file(data)
        try:
            data = json.loads(data)
        except Exception:
            break

    if isinstance(data, dict):
        return service_account.Credentials.from_service_account_info(data)

    raise ValueError(f"Invalid credentials format: expected JSON dictionary, got {type(data).__name__}")
