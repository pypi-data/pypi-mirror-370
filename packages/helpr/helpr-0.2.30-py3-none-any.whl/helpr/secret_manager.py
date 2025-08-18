"""
AWS Secret Manager integration for JWT key management.
"""
from typing import Dict, Any, Optional
import json
import boto3
from botocore.exceptions import ClientError
from authlib.jose import JsonWebKey

class SecretManagerError(Exception):
    """Base exception for Secret Manager error"""
    pass

class SecretNotFoundError(SecretManagerError):
    """Raised when secret is not found in AWS Secret Manager"""
    pass

class SecretInvalidError(SecretManagerError):
    """Raised when secret data is invalid"""
    pass

class JWTSigningKeyProvider:
    """Abstract base class for JWT key providers"""
    
    def private_key(self) -> JsonWebKey:
        """Get the private key for signing"""
        raise NotImplementedError
        
    def public_key(self) -> JsonWebKey:
        """Get the public key for verification"""
        raise NotImplementedError
        
    def public_key_kid(self) -> str:
        """Get the key ID of the public key"""
        raise NotImplementedError

class AWSSecretManagerKeyProvider(JWTSigningKeyProvider):
    """AWS Secret Manager implementation of JWT key provider"""

    def __init__(
        self,
        secret_name: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str
    ) -> None:
        """
        Initialize the AWS Secret Manager key provider.
        
        Args:
            secret_name: Name of the secret in AWS Secret Manager
            region_name: AWS region name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretInvalidError: If secret data is invalid
        """
        self._secret_manager = SecretManager(
            secret_name=secret_name,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self._load_keys()
        
    def _load_keys(self) -> None:
        """Load and validate JWT keys from secret manager"""
        try:
            secrets = self._secret_manager.load_secrets()
            private_key_str = secrets.get('private_key')
            public_key_str = secrets.get('public_key')
            
            if not private_key_str or not public_key_str:
                raise SecretInvalidError("Missing required JWT keys in secret")
                
            self._private_key = JsonWebKey.import_key(private_key_str)
            self._public_key = JsonWebKey.import_key(public_key_str)
            
        except ClientError as e:
            raise SecretNotFoundError(f"Failed to fetch secret: {str(e)}")
        except Exception as e:
            raise SecretInvalidError(f"Failed to import JWT keys: {str(e)}")
        
    def private_key(self) -> JsonWebKey:
        """Get the private key for signing"""
        return self._private_key

    def public_key(self) -> JsonWebKey:
        """Get the public key for verification"""
        return self._public_key

    def public_key_kid(self) -> str:
        """Get the key ID of the public key"""
        return self._public_key.as_dict()['kid']

class SecretManager:
    """AWS Secret Manager client wrapper"""

    def __init__(
        self,
        secret_name: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str
    ) -> None:
        """
        Initialize the Secret Manager client.
        
        Args:
            secret_name: Name of the secret to fetch
            region_name: AWS region name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
        """
        self.secret_name = secret_name
        self._cached_secrets: Optional[Dict[str, Any]] = None
        self._region_name = region_name
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    def fetch_secrets(self) -> Dict[str, Any]:
        """
        Fetch secrets from AWS Secret Manager.
        
        Returns:
            dict: Decoded secret data
            
        Raises:
            SecretNotFoundError: If secret is not found
            SecretInvalidError: If secret data is invalid
        """
        session = boto3.session.Session(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._region_name
        )
        client = session.client(service_name='secretsmanager')

        try:
            response = client.get_secret_value(SecretId=self.secret_name)
            return json.loads(response['SecretString'])
        except ClientError as e:
            raise SecretNotFoundError(f"Failed to fetch secret: {str(e)}")
        except json.JSONDecodeError as e:
            raise SecretInvalidError(f"Invalid secret data format: {str(e)}")

    def load_secrets(self) -> Dict[str, Any]:
        """
        Load secrets from cache or fetch from AWS.
        
        Returns:
            dict: Decoded secret data
        """
        if self._cached_secrets is None:
            self._cached_secrets = self.fetch_secrets()
        return self._cached_secrets