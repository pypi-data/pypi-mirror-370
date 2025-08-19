# decorators.py

from functools import wraps
from more_sso.validator import validate_jwt
from more_sso.exceptions import JWTValidationError
from typing import TypeVar
import json

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":"*.more.in",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }

def json_response(status_code: int, detail: str="success", data: dict = {}):
    return {
        "statusCode": status_code,
        "headers":headers,
        "body": json.dumps({
            "detail": detail,
            "data": data or {}
        })
    }

def auth_required(func):
    @wraps(func)
    def wrapper(headers: dict , *args, **kwargs):
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return json_response( 401, detail= "Unauthorized: Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        try:
            user = validate_jwt(token)
            headers = {"user": user}  # Inject user into headers for further use
            return func(headers, *args, **kwargs)
        except JWTValidationError as e:
            return json_response( 401, detail= str(e) )
    return wrapper

def root_auth_required(func):
    @wraps(func)
    def wrapper(event, context):
        auth_header = event.get("headers", {}).get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return json_response( 401, detail="invalid Authorization header header should begin with Bearer ..." )
        token = auth_header.split(" ")[1]
        try:
            user = validate_jwt(token)
            event['requestContext']['user'] = user
            return func(event, context)
        except JWTValidationError as e:
            return json_response( 401, detail=str(e))
    return wrapper