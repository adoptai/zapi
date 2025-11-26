"""Secure encryption/decryption utilities for LLM API keys."""

import base64
import secrets

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class LLMKeyEncryption:
    """Handles encryption/decryption of LLM API keys using org_id as context."""

    # Constants for encryption
    KEY_LENGTH = 32  # 256 bits for AES-256
    NONCE_LENGTH = 12  # 96 bits for GCM
    SALT_LENGTH = 16  # 128 bits
    TAG_LENGTH = 16  # 128 bits for GCM tag
    ITERATIONS = 100000  # PBKDF2 iterations

    def __init__(self, org_id: str):
        """
        Initialize encryption handler with organization ID.

        Args:
            org_id: Organization ID used as encryption context

        Raises:
            ValueError: If org_id is empty or invalid
        """
        if not org_id or not org_id.strip():
            raise ValueError("org_id cannot be empty")

        self.org_id = org_id.strip()

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from org_id using PBKDF2.

        Args:
            salt: Random salt for key derivation

        Returns:
            Derived encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(self.org_id.encode("utf-8"))

    def encrypt_key(self, api_key: str) -> str:
        """
        Encrypt a single LLM API key using org_id as context.

        Args:
            api_key: API key to encrypt

        Returns:
            Base64-encoded encrypted data with embedded salt and nonce

        Raises:
            ValueError: If encryption fails
        """
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")

        try:
            # Generate random salt and nonce
            salt = secrets.token_bytes(self.SALT_LENGTH)
            nonce = secrets.token_bytes(self.NONCE_LENGTH)

            # Derive encryption key
            key = self._derive_key(salt)

            # Only encrypt the API key itself (no provider needed)
            plaintext = api_key.strip().encode("utf-8")

            # Encrypt using AES-256-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()

            # Package: salt + nonce + ciphertext + tag
            encrypted_data = salt + nonce + ciphertext + encryptor.tag

            # Return base64-encoded result
            return base64.b64encode(encrypted_data).decode("ascii")

        except Exception as e:
            raise ValueError(f"Failed to encrypt LLM key: {e}")
        finally:
            # Clear sensitive data from memory
            if "key" in locals():
                key = b"\x00" * len(key)
            if "plaintext" in locals():
                plaintext = b"\x00" * len(plaintext)

    def decrypt_key(self, encrypted_data: str) -> str:
        """
        Decrypt a single LLM API key from encrypted data.

        Args:
            encrypted_data: Base64-encoded encrypted data

        Returns:
            Decrypted API key string

        Raises:
            ValueError: If decryption fails or data is corrupted
        """
        if not encrypted_data or not encrypted_data.strip():
            raise ValueError("encrypted_data cannot be empty")

        key = None
        plaintext = None

        try:
            # Decode base64 data
            try:
                data = base64.b64decode(encrypted_data.encode("ascii"))
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {e}")

            # Validate minimum length
            min_length = self.SALT_LENGTH + self.NONCE_LENGTH + self.TAG_LENGTH + 1
            if len(data) < min_length:
                raise ValueError("Encrypted data is too short")

            # Extract components
            salt = data[: self.SALT_LENGTH]
            nonce = data[self.SALT_LENGTH : self.SALT_LENGTH + self.NONCE_LENGTH]
            tag_start = len(data) - self.TAG_LENGTH
            ciphertext = data[self.SALT_LENGTH + self.NONCE_LENGTH : tag_start]
            tag = data[tag_start:]

            # Derive decryption key
            key = self._derive_key(salt)

            # Decrypt using AES-256-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Return decrypted API key directly
            return plaintext.decode("utf-8")

        except Exception as e:
            if "Invalid base64" in str(e):
                raise
            raise ValueError(f"Failed to decrypt LLM key: {e}")
        finally:
            # Clear sensitive data from memory
            if key is not None:
                key = b"\x00" * len(key)
            if plaintext is not None:
                plaintext = b"\x00" * len(plaintext)


def encrypt_llm_key(org_id: str, api_key: str) -> str:
    """
    Convenience function to encrypt a single LLM key.

    Args:
        org_id: Organization ID for encryption context
        api_key: API key to encrypt

    Returns:
        Base64-encoded encrypted data
    """
    encryptor = LLMKeyEncryption(org_id)
    return encryptor.encrypt_key(api_key)


def decrypt_llm_key(org_id: str, encrypted_data: str) -> str:
    """
    Convenience function to decrypt a single LLM key.

    Args:
        org_id: Organization ID for decryption context
        encrypted_data: Base64-encoded encrypted data

    Returns:
        Decrypted API key string
    """
    decryptor = LLMKeyEncryption(org_id)
    return decryptor.decrypt_key(encrypted_data)


def secure_compare_key(provider1: str, key1: str, provider2: str, key2: str) -> bool:
    """
    Securely compare two provider-key pairs without timing attacks.

    Args:
        provider1: First provider name
        key1: First API key
        provider2: Second provider name
        key2: Second API key

    Returns:
        True if both provider and key match, False otherwise
    """
    # Use secrets.compare_digest for timing-safe comparison
    provider_match = secrets.compare_digest(provider1, provider2)
    key_match = secrets.compare_digest(key1, key2)

    return provider_match and key_match
