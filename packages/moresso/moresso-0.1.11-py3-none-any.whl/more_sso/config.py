import json
import os
import boto3

class ConfigMissingError(Exception):
    """Raised when required SSO config is missing."""
    pass

REQUIRED_SSO_KEYS = ["public_key_uri","region"]

def get_secret(secret,region):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',region_name=region )
    get_secret_value_response = client.get_secret_value( SecretId=secret )
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret  

_config = None

def _validate_config(config: dict):
    missing = [key.upper() for key in REQUIRED_SSO_KEYS if not config.get(key)]
    if missing:
        raise ConfigMissingError(f"Missing SSO config: {', '.join(missing)} \n please set them in environment or pass them as parameters to init_sso_config( ) ")

def init_sso_config(public_key_uri=None,region=None):
    """
    Initialize config from parameters or environment variables.
    Supports any keys. Required keys are checked dynamically.
    """
    global _config
    _config = {
        "public_key_uri": public_key_uri,
        "region":region
    }
    _validate_config(_config)

def get_sso_config():
    global _config
    if _config is not None:
        return _config

    # Lazy load from env if not already initialized
    config = {
        key: os.getenv(f"{key.upper()}", "")
        for key in REQUIRED_SSO_KEYS
    }
    _validate_config(config)
    return config
