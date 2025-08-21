import json
import os
import boto3
import base64
class ConfigMissingError(Exception):
    """Raised when required SSO config is missing."""
    pass

REQUIRED_SSO_KEYS = ["public_key_uri"]

def get_pem(KeyId) -> str:
    kms = boto3.client("kms",'ap-south-1')
    resp = kms.get_public_key(KeyId=KeyId)
    b:bytes = resp["PublicKey"]
    body = base64.encodebytes(b).decode("ascii").replace("\n", "")
    lines = [body[i:i+64] for i in range(0, len(body), 64)]
    return "-----BEGIN PUBLIC KEY-----\n" + "\n".join(lines) + "\n-----END PUBLIC KEY-----\n"

_config = None

def _validate_config(config: dict):
    missing = [key.upper() for key in REQUIRED_SSO_KEYS if not config.get(key)]
    if missing:
        raise ConfigMissingError(f"Missing SSO config: {', '.join(missing)} \n please set them in environment or pass them as parameters to init_sso_config( ) ")

def init_sso_config(public_key_uri=None):
    """
    Initialize config from parameters or environment variables.
    Supports any keys. Required keys are checked dynamically.
    """
    global _config
    _config = {
        "public_key_uri": public_key_uri
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
