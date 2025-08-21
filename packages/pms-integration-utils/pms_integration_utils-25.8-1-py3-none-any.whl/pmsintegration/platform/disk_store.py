import os
import time
import hashlib
import functools
import shelve
from cryptography.fernet import Fernet

CACHE_DIR = os.path.expanduser("~/.pms_cache_secrets")
KEY_FILE = os.path.join(CACHE_DIR, "encryption_key.key")
SHELVE_FILE = os.path.join(CACHE_DIR, "secrets_cache")
TTL_SECONDS = 7200  # 2 hours

os.makedirs(CACHE_DIR, exist_ok=True)


def get_or_create_key():
    """Retrieve or generate encryption key."""
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, "rb").read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def encrypt_decrypt(data, encrypt=True):
    """Encrypt or decrypt data securely."""
    fernet = Fernet(get_or_create_key())
    return fernet.encrypt(data.encode()) if encrypt else fernet.decrypt(data).decode()


def get_secret_key(secret_name):
    """Generate a unique key for each secret in the shelve database."""
    return hashlib.sha256(secret_name.encode()).hexdigest()


def disk_memoize(func):
    """Decorator to cache secrets securely using shelve with TTL."""

    @functools.wraps(func)
    def wrapper(secret_name):
        try:
            with shelve.open(SHELVE_FILE) as db:
                secret_key = get_secret_key(secret_name)
                if secret_key in db:
                    timestamp, encrypted_secret = db[secret_key]
                    if time.time() - timestamp < TTL_SECONDS:
                        print(f"Reading from cache: {secret_name}")
                        return encrypt_decrypt(encrypted_secret, encrypt=False)

                # Fetch from Azure if expired/missing
                secret_value = func(secret_name)
                db[secret_key] = (time.time(), encrypt_decrypt(secret_value))
                print("Writing to cache")
                return secret_value
        except Exception as e:
            print(e)
            return func(secret_name)

    return wrapper
