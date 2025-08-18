"""
JWT Token Helper module for generating and verifying tokens.
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from authlib.jose import JsonWebToken, JsonWebKey
from authlib.jose.errors import ExpiredTokenError, DecodeError, InvalidTokenError
from .exceptions import AppException
from .secret_manager import JWTSigningKeyProvider

class TokenError(AppException):
    """Base exception for token-related errorss"""
    def __init__(self, message: str, error_code: int = 1000, http_code: int = 400):
        super().__init__(message=message, error_code=error_code, http_code=http_code)

class TokenMissingError(TokenError):
    """Raised when a token is missings"""
    def __init__(self, message: str = "Token is missing"):
        super().__init__(message=message, error_code=1004, http_code=401)

class TokenExpiredError(TokenError):
    """Raised when a token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message, error_code=1005, http_code=401)

class TokenInvalidError(TokenError):
    """Raised when a token is invalid"""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message, error_code=1006, http_code=401)

class JWTHelper:
    """Helper class for JWT token operations"""
    
    SUPPORTED_ALGORITHMS = ['RS256', 'RS384', 'RS512']
    
    def __init__(self, key_provider: JWTSigningKeyProvider, algorithm: str = 'RS256') -> None:
        """
        Initialize the JWT Helper.
        
        Args:
            key_provider: Provider object that supplies private and public keys
            algorithm (str): Algorithm to use for token signing

        Raises:
            ValueError: If algorithm is not supported
        """
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Supported algorithms: {', '.join(self.SUPPORTED_ALGORITHMS)}")
            
        self.key_provider = key_provider
        self._algo = algorithm
        
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token (str): Token to verify

        Returns:
            dict: Decoded token payload

        Raises:
            TokenMissingError: If token is empty
            TokenExpiredError: If token has expired
            TokenInvalidError: If token is invalid
        """
        if not token:
            raise TokenMissingError()
            
        try:
            jwt_instance = JsonWebToken(algorithms=[self._algo])
            decoded_token = jwt_instance.decode(token, self.key_provider.public_key())
            decoded_token.validate()
            return decoded_token
        except ExpiredTokenError:
            raise TokenExpiredError()
        except (DecodeError, InvalidTokenError):
            raise TokenInvalidError()
        except Exception as e:
            raise TokenInvalidError(f"Token verification failed: {str(e)}")
        