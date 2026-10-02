from cryptography.fernet import Fernet
from src.config import settings


cipher = Fernet(settings.fernet_key.encode() if isinstance(settings.fernet_key, str) else settings.fernet_key)


def encrypt_string(plaintext: str) -> str:
    """Encrypt a string."""
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_string(ciphertext: str) -> str:
    """Decrypt a string."""
    return cipher.decrypt(ciphertext.encode()).decode()
