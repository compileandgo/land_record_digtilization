import json
import os
from pathlib import Path
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_credentials():
    creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")
    creds = None
    
    if not creds_env:
        # Fallback to local credentials.json file
        for candidate in ["credentials.json", "server/credentials.json", "../credentials.json"]:
            path = Path(candidate)
            if path.exists():
                creds = service_account.Credentials.from_service_account_file(str(path))
                break
        if not creds:
            raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set and credentials.json file not found.")

    elif os.path.exists(creds_env):
        creds = service_account.Credentials.from_service_account_file(creds_env)

    else:
        # Otherwise parse JSON string
        try:
            data = json.loads(creds_env)
        except Exception as e:
            raise ValueError(f"Failed to parse GOOGLE_CREDENTIALS_JSON: {e}")

        # Un-nest double-encoded JSON string if string was enclosed in extra quotes
        while isinstance(data, str):
            if os.path.exists(data):
                creds = service_account.Credentials.from_service_account_file(data)
                break
            try:
                data = json.loads(data)
            except Exception:
                break

        if creds is None and isinstance(data, dict):
            creds = service_account.Credentials.from_service_account_info(data)

    if creds is None:
        raise ValueError("Invalid credentials format or location.")

    if creds.requires_scopes:
        creds = creds.with_scopes(SCOPES)
        
    return creds
