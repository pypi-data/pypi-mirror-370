# sso-auth

This package provides:

- RS256 JWT validation using a public key from a URL
- In-memory caching
- Header-based decorator (`@auth_required`)
- AWS Lambda and FastAPI-ready
- Configurable via environment or programmatic init

## Usage

```python
from sso_auth import auth_required,root_auth_required,init_sso_config
from sso_auth.exceptions import JWTValidationError
from sso_auth.validators import validate_token

init_sso_config(
    sso_public_key_url=SSO_PUBLIC_KEY_URL,
    sso_issuer=SSO_ISSUER
)
or 
: export then env with SSO_PUBLIC_KEY_URL and SSO_ISSUER

#the decoded payload will be injected into  event['headers']['user']
@auth_required
def my_func(header, *args,**kwargs):
# header 
    user = header.get("user", {})
    ...


or 
try:
    user = validate_token(token)
except JWTValidationError as e:
    ...
```

the authorization can also be implemented at root level of lambda as given below
the decoded payload will be injected into  event['requestContext']['user']
```python

@root_auth_required
def lambda_handler(event, context):
    """inject_jwt_user with inject the decoded payload into user  of requestContext 
    if authentication fails then  inject_jwt_user returns with statusCode 401 """
    user = event['requestContext']['user']
```
# Where to get it

The source code is currently hosted on GitHub at: [here](https://github.com/more-retail/moresso)