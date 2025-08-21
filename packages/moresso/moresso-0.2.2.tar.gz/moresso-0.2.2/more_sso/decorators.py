# decorators.py

from functools import wraps
from more_sso.validator import validate_jwt
from more_sso.exceptions import JWTValidationError
from typing import TypeVar
import json

RESPONSE_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":"*.more.in",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    }

def json_response(status_code: int, detail: str="success", data: dict = {}):
    return {
        "statusCode": status_code,
        "headers":RESPONSE_HEADERS,
        "body": json.dumps({
            "detail": detail,
            "data": data or {}
        })
    }


def auth_required(func):
    @wraps(func)
    def wrapper(headers: dict , *args, **kwargs):
        token = headers.get("Authorization", "") or headers.get("authorization", "")
        if not token:
            return json_response( 401, detail= "Unauthorized: Missing or invalid Authorization header")
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
        token = event.get("headers", {}).get("Authorization", "") or  event.get("headers", {}).get("authorization", "")
        if token :
            return json_response( 401, detail="invalid Authorization header header should begin with Bearer ..." )
        try:
            user = validate_jwt(token)
            event['requestContext']['user'] = user
            return func(event, context)
        except JWTValidationError as e:
            return json_response( 401, detail=str(e))
    return wrapper