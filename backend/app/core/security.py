"""API key hashing (SHA-256) & security utilities"""

import hashlib
import secrets

def generate_api_keys(prefix: str = "sk_live_") -> tuple[str, str, str]:
    """
    Generates a raw key, its SHA-256 hash for storage, and a short prefix,
    Returns: ( raw_key, key_hash, key_prefix )
    """

    raw_secret = secrets.token_hex(24)
    raw_key = f"{prefix}{raw_secret}"
    key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    key_prefix = raw_key[:10]
    return raw_key, key_hash, key_prefix


def hash_api_key(raw_key: str) -> str:
    """Hashes an incoming API key string for database matching."""
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
