"""
Security utilities for API key management and credential handling
"""

import os
import secrets
import re
from typing import Dict, Any
import logging

# Try to import bcrypt, fall back to hashlib if not available
try:
    import bcrypt

    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    logging.warning("bcrypt not available, using PBKDF2 for password hashing")

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Secure API key management with proper hashing and validation"""

    def __init__(self):
        self.secret_key = os.environ.get("API_KEY_SECRET", secrets.token_urlsafe(32))
        if self.secret_key == secrets.token_urlsafe(32):
            logger.warning("Using generated secret key - set API_KEY_SECRET environment variable")

    def generate_api_key(self) -> str:
        """Generate a new secure API key"""
        return "rk_" + secrets.token_urlsafe(24)  # 24 bytes = 32 base64 chars

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for secure storage"""
        if HAS_BCRYPT:
            # Use bcrypt for API key hashing with salt
            return bcrypt.hashpw(api_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        else:
            # Fallback to PBKDF2 with HMAC-SHA256
            salt = secrets.token_bytes(32)
            import hashlib

            key = hashlib.pbkdf2_hmac("sha256", api_key.encode("utf-8"), salt, 100000)
            # Store salt + hash (base64 encoded)
            import base64

            combined = base64.b64encode(salt + key).decode("utf-8")
            return f"pbkdf2:{combined}"

    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """Verify an API key against its hash"""
        try:
            if HAS_BCRYPT and not hashed_key.startswith("pbkdf2:"):
                return bcrypt.checkpw(api_key.encode("utf-8"), hashed_key.encode("utf-8"))
            else:
                # Handle PBKDF2 format
                if hashed_key.startswith("pbkdf2:"):
                    import base64
                    import hashlib

                    combined = base64.b64decode(hashed_key[7:])
                    salt = combined[:32]
                    stored_key = combined[32:]
                    test_key = hashlib.pbkdf2_hmac("sha256", api_key.encode("utf-8"), salt, 100000)
                    return secrets.compare_digest(stored_key, test_key)
                else:
                    logger.error("Unknown hash format")
                    return False
        except Exception as e:
            logger.error(f"API key verification failed: {e}")
            return False

    def is_valid_format(self, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False

        # Should start with "rk_" and be the correct length
        if not api_key.startswith("rk_"):
            return False

        # Should be 35 characters total (3 prefix + 32 base64)
        if len(api_key) != 35:
            return False

        # Check character set (base64url safe)
        pattern = r"^rk_[A-Za-z0-9_-]{32}$"
        return bool(re.match(pattern, api_key))


class CredentialValidator:
    """Validate and sanitize credentials"""

    @staticmethod
    def validate_environment_variables() -> Dict[str, Any]:
        """Validate required environment variables are set"""
        required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]

        optional_vars = ["DAYTONA_API_KEY", "GOOGLE_AI_API_KEY", "REDIS_PASSWORD", "ANTHROPIC_API_KEY"]

        missing_required = []
        missing_optional = []

        for var in required_vars:
            value = os.environ.get(var)
            if not value or value.strip() in ["", "your_key_here", "placeholder"]:
                missing_required.append(var)

        for var in optional_vars:
            value = os.environ.get(var)
            if not value or value.strip() in ["", "your_key_here", "placeholder"]:
                missing_optional.append(var)

        return {
            "valid": len(missing_required) == 0,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "total_required": len(required_vars),
            "total_optional": len(optional_vars),
        }

    @staticmethod
    def validate_credential_strength(credential: str, min_length: int = 32) -> bool:
        """Validate credential strength"""
        if not credential or len(credential) < min_length:
            return False

        # Check for placeholder values
        placeholders = ["your_key_here", "placeholder", "changeme", "default", "test", "demo", "example", "sample"]

        if credential.lower() in placeholders:
            return False

        return True


class SecureConfigLoader:
    """Secure configuration loader with validation"""

    def __init__(self):
        self.validator = CredentialValidator()
        self.api_key_manager = APIKeyManager()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with security validation"""
        validation = self.validator.validate_environment_variables()

        config = {
            # Azure OpenAI
            "azure_openai_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "azure_openai_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            # Optional services
            "daytona_api_key": os.environ.get("DAYTONA_API_KEY"),
            "google_ai_key": os.environ.get("GOOGLE_AI_API_KEY"),
            "redis_password": os.environ.get("REDIS_PASSWORD"),
            # Validation results
            "validation": validation,
        }

        # Log validation results (without exposing actual keys)
        if validation["valid"]:
            logger.info("✅ All required credentials configured")
        else:
            logger.error(f"❌ Missing required credentials: {validation['missing_required']}")

        if validation["missing_optional"]:
            logger.info(f"ℹ️ Optional credentials not configured: {validation['missing_optional']}")

        return config

    def mask_credential(self, credential: str) -> str:
        """Mask credential for logging (show only first/last chars)"""
        if not credential or len(credential) < 8:
            return "***"

        return credential[:4] + "***" + credential[-4:]


# Global instances
api_key_manager = APIKeyManager()
credential_validator = CredentialValidator()
config_loader = SecureConfigLoader()


def get_secure_config() -> Dict[str, Any]:
    """Get securely loaded configuration"""
    return config_loader.load_config()


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format"""
    return api_key_manager.is_valid_format(api_key)


def hash_api_key_secure(api_key: str) -> str:
    """Hash API key securely for storage"""
    return api_key_manager.hash_api_key(api_key)


def verify_api_key_secure(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash"""
    return api_key_manager.verify_api_key(api_key, hashed_key)
