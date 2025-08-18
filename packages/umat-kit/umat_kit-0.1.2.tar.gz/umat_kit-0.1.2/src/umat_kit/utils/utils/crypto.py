"""
Advanced Cryptography and Security Utilities for UMAT API Testing
Provides encryption, decryption, hashing, and JWT token management
"""

import hashlib
import hmac
import base64
import secrets
import jwt
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import json

class CryptoManager:
    """Advanced cryptography management system"""

    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or self._generate_key()
        self._fernet = Fernet(self.master_key.encode() if isinstance(self.master_key, str) else self.master_key)

    @staticmethod
    def _generate_key() -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()

    def encrypt_data(self, data: Union[str, Dict[str, Any]]) -> str:
        """Encrypt data using Fernet symmetric encryption"""
        if isinstance(data, dict):
            data = json.dumps(data)

        encrypted_data = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict[str, Any]]:
        """Decrypt data using Fernet symmetric encryption"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data).decode()

            # Try to parse as JSON
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """Hash password using PBKDF2 with SHA256"""
        if salt is None:
            salt = secrets.token_bytes(32)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = kdf.derive(password.encode())
        hashed_password = base64.urlsafe_b64encode(key).decode()
        salt_str = base64.urlsafe_b64encode(salt).decode()

        return hashed_password, salt_str

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            salt_bytes = base64.urlsafe_b64decode(salt.encode())
            expected_hash, _ = CryptoManager.hash_password(password, salt_bytes)
            return hmac.compare_digest(expected_hash, hashed_password)
        except Exception:
            return False

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm"""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }

        if algorithm not in algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        hash_obj = algorithms[algorithm]()
        hash_obj.update(data.encode())
        return hash_obj.hexdigest()

    @staticmethod
    def create_hmac(data: str, key: str, algorithm: str = 'sha256') -> str:
        """Create HMAC signature"""
        algorithms = {
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }

        if algorithm not in algorithms:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")

        signature = hmac.new(
            key.encode(),
            data.encode(),
            algorithms[algorithm]
        ).hexdigest()

        return signature

    @staticmethod
    def verify_hmac(data: str, signature: str, key: str, algorithm: str = 'sha256') -> bool:
        """Verify HMAC signature"""
        try:
            expected_signature = CryptoManager.create_hmac(data, key, algorithm)
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

class JWTManager:
    """Advanced JWT token management"""

    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload: Dict[str, Any],
                    expires_in: timedelta = timedelta(hours=24)) -> str:
        """Create a JWT token with expiration"""
        now = datetime.now(timezone.utc)
        payload.update({
            'iat': now,
            'exp': now + expires_in,
            'nbf': now
        })

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str, verify_signature: bool = True) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            if verify_signature:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            else:
                payload = jwt.decode(token, options={"verify_signature": False})

            return payload

        except jwt.exceptions.DecodeError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def refresh_token(self, token: str, new_expires_in: timedelta = timedelta(hours=24)) -> str:
        """Refresh an existing token with new expiration"""
        try:
            # Decode without verifying expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            # Remove old timing claims
            for claim in ['iat', 'exp', 'nbf']:
                payload.pop(claim, None)

            # Create new token
            return self.create_token(payload, new_expires_in)

        except jwt.exceptions.DecodeError as e:
            raise ValueError(f"Cannot refresh invalid token: {str(e)}")

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get detailed information about a token"""
        try:
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})

            info = {
                'header': header,
                'payload': payload,
                'algorithm': header.get('alg'),
                'token_type': header.get('typ'),
                'issued_at': None,
                'expires_at': None,
                'not_before': None,
                'is_expired': False,
                'time_until_expiry': None
            }

            # Process timing claims
            now = datetime.now(timezone.utc)

            if 'iat' in payload:
                info['issued_at'] = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)

            if 'exp' in payload:
                exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
                info['expires_at'] = exp_time
                info['is_expired'] = exp_time < now
                if not info['is_expired']:
                    info['time_until_expiry'] = exp_time - now

            if 'nbf' in payload:
                info['not_before'] = datetime.fromtimestamp(payload['nbf'], tz=timezone.utc)

            return info

        except Exception as e:
            raise ValueError(f"Cannot analyze token: {str(e)}")

    def is_token_valid(self, token: str) -> bool:
        """Check if token is valid without raising exceptions"""
        try:
            self.decode_token(token)
            return True
        except Exception:
            return False

class RSAManager:
    """RSA asymmetric encryption management"""

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_key_pair(self, key_size: int = 2048) -> tuple[bytes, bytes]:
        """Generate RSA key pair"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        self.public_key = self.private_key.public_key()

        # Serialize keys
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    def load_private_key(self, private_key_pem: bytes, password: Optional[bytes] = None):
        """Load private key from PEM format"""
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=password
        )

    def load_public_key(self, public_key_pem: bytes):
        """Load public key from PEM format"""
        self.public_key = serialization.load_pem_public_key(public_key_pem)

    def encrypt_with_public_key(self, data: str) -> str:
        """Encrypt data with public key"""
        if not self.public_key:
            raise ValueError("Public key not loaded")

        encrypted_data = self.public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return base64.b64encode(encrypted_data).decode()

    def decrypt_with_private_key(self, encrypted_data: str) -> str:
        """Decrypt data with private key"""
        if not self.private_key:
            raise ValueError("Private key not loaded")

        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted_data.decode()

    def sign_data(self, data: str) -> str:
        """Sign data with private key"""
        if not self.private_key:
            raise ValueError("Private key not loaded")

        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()

    def verify_signature(self, data: str, signature: str) -> bool:
        """Verify signature with public key"""
        if not self.public_key:
            raise ValueError("Public key not loaded")

        try:
            signature_bytes = base64.b64decode(signature.encode())
            self.public_key.verify(
                signature_bytes,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

# Utility functions for easy access
def create_crypto_manager(key: Optional[str] = None) -> CryptoManager:
    """Create a crypto manager instance"""
    return CryptoManager(key)

def create_jwt_manager(secret_key: str) -> JWTManager:
    """Create a JWT manager instance"""
    return JWTManager(secret_key)

def create_rsa_manager() -> RSAManager:
    """Create an RSA manager instance"""
    return RSAManager()