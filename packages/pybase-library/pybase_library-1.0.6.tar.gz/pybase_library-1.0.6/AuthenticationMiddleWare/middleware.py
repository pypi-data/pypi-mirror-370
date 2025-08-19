from fastapi import FastAPI, Request, Response, HTTPException
from fastapi import security
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import requests
import jwt
from datetime import datetime, timedelta
from .access_control import AccessController
import logging
import traceback
import base64
import json
import time
import datetime
import requests
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# public config
logger = logging.getLogger(__name__)
from pydantic_settings import BaseSettings
from typing import List, Optional, Callable

class Settings(BaseSettings):
    public_key_url: str = "https://staging-iam.gt.vng.vn"
    algorithm: str = "RS256"
    token_header: str = "authorization"
    token_prefix: str = "Bearer "
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    excluded_paths: List[str] = ["/", "/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico", "/mock-token"]
    unauthorized_message: str = "Token không hợp lệ"
    auth_prefixes: List[str] = ["/api", "/admin"]
    
    # Optional override for full certs URL
    certs_url_override: Optional[str] = None
    
    class Config:
        env_prefix = "AUTH_"
        env_file = ".env"
        case_sensitive = False
default_setting = Settings()

# change openapi to HTTPBearer
# create wrapper for authentication and authorization
security = HTTPBearer()
def IAMAuthentication(credential: HTTPAuthorizationCredentials = Depends(security)):
    # authenticate
    try:
        auth_config = AuthConfig()
        validator = ValidateToken(auth_config)
        claims = validator.get_claims_from_token(credential.credentials)
        return claims
    except Exception as e:
        logger.exception("Authentication failed")
        raise HTTPException(status_code=401, detail="Authentication failed")
def IAMRoleBasedSecurity(allowed_roles: List[str] = [], custom_position_of_roles: Callable[[dict], list] = None):
    def role_checker(claims: dict = Depends(IAMAuthentication)):
        if not allowed_roles:
            return claims
        if custom_position_of_roles:
            user_roles = custom_position_of_roles(claims)
        else:
            user_roles = claims.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return claims
    return role_checker

@app.get("/test")
def test(user_claims: dict = Depends(IAMRoleBasedSecurity(allowed_roles=["READ", "WRITE"]))):
    return {"message": "Hello World", "user_claims": user_claims}

class AuthConfig:
    """Auth config"""
    def __init__(self, setting: Settings=default_setting):
        self.excluded_paths = setting.excluded_paths
        self.unauthorized_message = setting.unauthorized_message
        self.cache_enabled = setting.cache_enabled
        self.cache_ttl_seconds = setting.cache_ttl_seconds
        self.token_header = setting.token_header
        self.token_prefix = setting.token_prefix
        self.algorithm = setting.algorithm
        self.auth_prefixes = setting.auth_prefixes
        if setting.certs_url_override:
            self.public_key_url = setting.certs_url_override
        else:
            self.public_key_url = f"{setting.public_key_url}/auth/realms/GameTechnical/protocol/openid-connect/certs"


class AuthMiddleware(BaseHTTPMiddleware):
    """Auth middleware"""
    def __init__(self, app, access_controller: AccessController = None, auth_config: AuthConfig=None, path_prefixes: List[str] = None):
        super().__init__(app)
        self.config = AuthConfig() if auth_config is None else auth_config
        self.validator = ValidateToken(self.config)
        self.access_controller = access_controller
        self.path_prefixes = path_prefixes or []  # Danh sách prefix cần auth

    async def dispatch(self, request: Request, call_next: Callable):
        """Dispatch request"""
        logger.info(f"Request path: {request.url.path}")
        
        # Check if path matches any prefix
        if self.path_prefixes:
            path_matches = any(request.url.path.startswith(prefix) for prefix in self.path_prefixes)
            if not path_matches:
                logger.info(f"Path {request.url.path} not in auth prefixes, skipping auth")
                return await call_next(request)
        
        logger.info(f"All headers: {dict(request.headers)}")
        logger.info(f"Looking for header: {self.config.token_header}")
        
        # Check if route is public using access controller
        if self.access_controller.check_access(request.url.path):
            logger.info("Public route, skipping auth")
            return await call_next(request)
        
        # Extract bearer token from header
        token = request.headers.get(self.config.token_header)
        logger.info(f"Token from header '{self.config.token_header}': {token}")
        
        # Try alternative header names
        auth_header = request.headers.get("authorization")
        logger.info(f"Token from 'authorization' (lowercase): {auth_header}")
        if not token and not auth_header:
            logger.error("No token found in header")
            return JSONResponse(
                status_code=401,
                content={"detail": self.config.unauthorized_message}
            )
        
        # Use whichever token is available
        final_token = token or auth_header
        logger.info(f"Using token: {final_token}")
        
        if not final_token:
            logger.error("No token found in any header format")
            return JSONResponse(
                status_code=401,
                content={"detail": self.config.unauthorized_message}
            )
        
        try:
            # Validate token
            logger.info("Validating token")
            claims = self.validator.get_claims_from_token(final_token)
            logger.info("Token validated successfully, continue to check access")
            
            # Check access with claims using access controller
            if not self.access_controller.check_access(request.url.path, claims):
                logger.error("Access denied")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied"}
                )
            
            logger.info(f"Access granted, continue to next middleware, claims: {claims}")
            # Add claims to request state, FORMAT: JSON #TODO
            request.state.user_claims = claims
            return await call_next(request)
        except jwt.ExpiredSignatureError:
            logger.error("JWT token expired")
            return JSONResponse(
                status_code=401,
                content={"detail": "JWT token expired"}
            )
        except jwt.InvalidTokenError:
            logger.error("Invalid JWT token")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid JWT token"}
            )
        except HTTPException as e:
            logger.error("Invalid token")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Invalid token: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Invalid token"}
            )


class ValidateToken:
    """Validate token"""
    def __init__(self, config: AuthConfig):
        self.config = config
        self._cached_public_key = None
        self._cache_timestamp = None

    def get_claims_from_token(self, token: str):
        """Get claims from token"""
        try:
            # Remove Bearer prefix if present
            if token.startswith(self.config.token_prefix):
                token = token[len(self.config.token_prefix):]
            
            public_key = self.get_public_key()
            logger.info(f"Public key retrieved: {public_key[:100]}..." if public_key else "No public key")
            if not public_key:
                raise HTTPException(status_code=401, detail="Invalid public key")
            
            # Debug token format
            token_parts = token.split('.')
            logger.info(f"Token parts count: {len(token_parts)}")
            logger.info(f"Token header: {token_parts[0] if len(token_parts) > 0 else 'Missing'}")
            logger.info(f"Algorithm configured: {self.config.algorithm}")
            
            # Try to decode header to see algorithm
            try:
                import base64
                import json
                header_data = base64.urlsafe_b64decode(token_parts[0] + "==").decode()
                header = json.loads(header_data)
                logger.info(f"Token algorithm: {header.get('alg', 'Unknown')}")
                logger.info(f"Token key ID: {header.get('kid', 'No kid')}")
            except Exception as e:
                logger.warning(f"Could not decode token header: {str(e)}")
            # TODO: config options
            decode_token = jwt.decode(token, public_key, algorithms=[self.config.algorithm], options={"verify_signature": True, "verify_aud": False})
            logger.info("Successfully decoded JWT token")
            return decode_token
        except jwt.ExpiredSignatureError:
            logger.error("JWT token has expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.exception("Invalid JWT token")
            raise HTTPException(status_code=401, detail=f"Invalid JWT token: {str(e)}")
        except jwt.InvalidKeyError:
            logger.exception("Invalid public key")
            raise HTTPException(status_code=401, detail="Invalid public key")
        except HTTPException as e:
            raise HTTPException(e.status_code, e.detail)
        except Exception as e:
            logger.exception("Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_public_key(self):     
        """Get public key from cache or from public key url"""   
        logger.info("Getting public key")
        # Check cache first
        if self.config.cache_enabled:
            logger.debug("Check cache first", self._cached_public_key, self._cache_timestamp)
            if (self._cached_public_key and self._cache_timestamp and 
                time.time() - self._cache_timestamp < self.config.cache_ttl_seconds):
                logger.info("Successfully get public key from cache")
                return self._cached_public_key
        
        try:
            logger.info("Getting public key from url")
            response = requests.get(self.config.public_key_url)
            response.raise_for_status()
            
            public_key = None
            # Try to parse as JSON first
            try:
                public_key_data = response.json()
                # TODO: handle more complex?
                # Handle JWKS format
                if "keys" in public_key_data:
                    # Get first key from JWKS
                    key = public_key_data["keys"][0]
                    logger.debug("Successfully get public key from url", key)
                    if "x5c" in key:
                        logger.debug("x5c", key["x5c"])
                        # X.509 certificate chain
                        from cryptography import x509
                        from cryptography.hazmat.primitives import serialization
                        import base64
                        cert_data = base64.b64decode(key["x5c"][0])
                        cert = x509.load_der_x509_certificate(cert_data)
                        public_key = cert.public_key().public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                        ).decode()
                    elif "n" in key and "e" in key:
                        logger.debug("n", key["n"])
                        logger.debug("e", key["e"])
                        # RSA components - would need more complex handling
                        from cryptography.hazmat.primitives.asymmetric import rsa
                        from cryptography.hazmat.primitives import serialization
                        import base64
                        n = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "=="), 'big')
                        e = int.from_bytes(base64.urlsafe_b64decode(key["e"] + "=="), 'big')
                        rsa_key = rsa.RSAPublicNumbers(e, n).public_key()
                        public_key = rsa_key.public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                        ).decode()
                else:
                    return None
            except ValueError:
                # Not JSON, treat as raw key
                public_key = response.text
            
            # Cache the result
            if self.config.cache_enabled:
                logger.info("saved cache public key")
                self._cached_public_key = public_key
                self._cache_timestamp = time.time()
            return public_key
                
        except Exception as e:
            logger.error(f"Failed to get public key: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to get public key: {str(e)}")

def get_current_user(request: Request):
    """Get current user from request state"""
    try:
        return getattr(request.state, "user_claims", None)
    except Exception as e:
        logger.error(f"Failed to get current user: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get current user: {str(e)}")


# third party app
app = FastAPI()

# Then add auth middleware
auth_config = AuthConfig()
# Create global access controller instance
access_controller = AccessController()
    
app.add_middleware(AuthMiddleware, 
    access_controller=access_controller, 
    auth_config=auth_config, 
    path_prefixes=["/api", "/admin"])


@app.get("/")
def root():
    return {"message": "JWT Authentication API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/mock-token")
def generate_mock_token():
    """Generate a mock JWT token for testing authentication"""
    import base64
    import json
    
    # Create mock payload
    payload = {
        "sub": "test-user-123",
        "name": "Test User",
        "email": "test@example.com",
        "roles": ["user", "admin"],
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iss": "mock-issuer",
        "aud": "mock-audience"
    }
    
    # Encode payload to base64
    payload_json = json.dumps(payload)
    encoded_payload = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    
    # Create mock token
    mock_token = f"MOCK_{encoded_payload}"
    
    return {
        "access_token": mock_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "payload": payload,
        "usage": "Copy the access_token and use it in Swagger Authorization"
    }

@app.get("/test-headers")
def test_headers(request: Request):
    """Debug endpoint to see all headers"""
    return {"headers": dict(request.headers)}

@app.get("/protected")
def protected(request: Request):
    logger.info("Protected endpoint accessed")
    user_claims = get_current_user(request)
    return {"message": "This is a protected endpoint", "user_claims": user_claims}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)