#!/usr/bin/env python3
"""
Tests for per-customer encryption module.
"""

import os
from unittest.mock import patch

import pytest
from cryptography.fernet import InvalidToken

from getting_started.encryption import (
    decrypt,
    derive_customer_key,
    encrypt,
    get_master_key,
)


FAKE_MASTER_KEY = "test-master-key-for-unit-tests-only"


@pytest.fixture(autouse=True)
def _set_master_key(monkeypatch):
    """Set a test master key for all encryption tests."""
    monkeypatch.setenv("ENCRYPTION_MASTER_KEY", FAKE_MASTER_KEY)


@pytest.mark.unit
class TestGetMasterKey:
    def test_returns_key_from_env(self):
        result = get_master_key()
        assert result == FAKE_MASTER_KEY.encode("utf-8")

    def test_raises_when_not_set(self, monkeypatch):
        monkeypatch.delenv("ENCRYPTION_MASTER_KEY")
        with pytest.raises(ValueError, match="ENCRYPTION_MASTER_KEY"):
            get_master_key()


@pytest.mark.unit
class TestDeriveCustomerKey:
    def test_derives_key(self):
        key = derive_customer_key("customer-1")
        assert isinstance(key, bytes)
        assert len(key) == 44  # base64url-encoded 32 bytes

    def test_different_customers_get_different_keys(self):
        key1 = derive_customer_key("customer-1")
        key2 = derive_customer_key("customer-2")
        assert key1 != key2

    def test_same_customer_gets_same_key(self):
        key1 = derive_customer_key("customer-1")
        key2 = derive_customer_key("customer-1")
        assert key1 == key2

    def test_empty_customer_id_raises(self):
        with pytest.raises(ValueError, match="customer_id must not be empty"):
            derive_customer_key("")


@pytest.mark.unit
class TestEncryptDecrypt:
    def test_roundtrip(self):
        plaintext = "sensitive data for customer"
        ciphertext = encrypt(plaintext, "customer-1")
        assert ciphertext != plaintext
        assert decrypt(ciphertext, "customer-1") == plaintext

    def test_none_passthrough(self):
        assert encrypt(None, "customer-1") is None
        assert decrypt(None, "customer-1") is None

    def test_empty_string(self):
        ciphertext = encrypt("", "customer-1")
        assert ciphertext is not None
        assert decrypt(ciphertext, "customer-1") == ""

    def test_wrong_customer_cannot_decrypt(self):
        ciphertext = encrypt("secret", "customer-1")
        with pytest.raises(InvalidToken):
            decrypt(ciphertext, "customer-2")

    def test_unicode_data(self):
        plaintext = "Unicode test data"
        ciphertext = encrypt(plaintext, "customer-1")
        assert decrypt(ciphertext, "customer-1") == plaintext

    def test_large_data(self):
        plaintext = "x" * 10_000
        ciphertext = encrypt(plaintext, "customer-1")
        assert decrypt(ciphertext, "customer-1") == plaintext
