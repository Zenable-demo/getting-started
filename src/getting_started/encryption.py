"""
Per-customer encryption for data at rest.

Uses HKDF to derive unique Fernet keys per customer from a master key,
ensuring each customer's data is encrypted with their own key.
"""

import base64
import logging
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

LOG = logging.getLogger(__name__)


def get_master_key() -> bytes:
    """Get the master encryption key from the environment.

    The master key is used as input to HKDF to derive per-customer keys.
    It must be set via the ENCRYPTION_MASTER_KEY environment variable.

    Returns:
        The master key as bytes.

    Raises:
        ValueError: If ENCRYPTION_MASTER_KEY is not set.
    """
    key = os.environ.get("ENCRYPTION_MASTER_KEY")
    if not key:
        raise ValueError(
            "ENCRYPTION_MASTER_KEY environment variable must be set. "
            "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )
    return key.encode("utf-8")


def derive_customer_key(customer_id: str) -> bytes:
    """Derive a per-customer Fernet key from the master key using HKDF.

    Each customer gets a unique encryption key derived from the master key
    and their customer ID, ensuring cryptographic isolation between customers.

    Args:
        customer_id: Unique identifier for the customer.

    Returns:
        A Fernet-compatible key (base64url-encoded 32 bytes).

    Raises:
        ValueError: If customer_id is empty or master key is not set.
    """
    if not customer_id:
        raise ValueError("customer_id must not be empty")

    master_key = get_master_key()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=f"customer-key-{customer_id}".encode("utf-8"),
    )
    derived_key = hkdf.derive(master_key)
    return base64.urlsafe_b64encode(derived_key)


def encrypt(plaintext: Optional[str], customer_id: str) -> Optional[str]:
    """Encrypt a string using the customer's derived key.

    Args:
        plaintext: The string to encrypt, or None.
        customer_id: Customer whose key to use for encryption.

    Returns:
        Base64-encoded ciphertext string, or None if plaintext is None.
    """
    if plaintext is None:
        return None

    key = derive_customer_key(customer_id)
    f = Fernet(key)
    return f.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(ciphertext: Optional[str], customer_id: str) -> Optional[str]:
    """Decrypt a string using the customer's derived key.

    Args:
        ciphertext: Base64-encoded ciphertext to decrypt, or None.
        customer_id: Customer whose key to use for decryption.

    Returns:
        Decrypted plaintext string, or None if ciphertext is None.
    """
    if ciphertext is None:
        return None

    key = derive_customer_key(customer_id)
    f = Fernet(key)
    return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
