from os import getenv

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from .utils import resolve_related_field

try:
    AES_PASSWORD = getenv("AES_PASSWORD")
    if AES_PASSWORD is None:
        raise ValueError("AES_PASSWORD not found in environment variables.")
    AES_KEY = base64.urlsafe_b64encode(hashlib.sha256(AES_PASSWORD.encode()).digest())
except Exception as e:
    raise RuntimeError(f"Failed to generate AES key: {e}")

def process_obj(
        obj,
        *,
        search: str,
        related_field: str | None,
        fields: tuple[str]
    ) -> int:
    """
    Returns obj.pk if any of the fields contain the term.
    """
    try:
        client_obj = resolve_related_field(obj, related_field)
        
        values = set()
        for field in fields:
            values.add(getattr(client_obj, field, None))
            
        if any(search in str(value).lower() for value in values):
            return obj.pk
    except Exception as e:
        raise RuntimeError(f"Failed to process object: {e}")

def process_values(
        encrypted_values_list: tuple[str, int],
        search: str,
        **_
    ) -> int:
    """
    Return the id of the object referring to the values.
    """
    decrypted_values: list[str, int] = list()

    for encrypted_value in encrypted_values_list:
        try:
            if type(encrypted_value) == bytes:
                decrypted_values.append(Fernet(AES_KEY).decrypt(encrypted_value).decode())
            # Return the value itself if it is already decrypted
            decrypted_values.append(encrypted_value)
        except (InvalidToken, ValueError, TypeError) as e:
            raise Exception(f"Error decrypting data: {e}")

    for value in decrypted_values:
        if search in str(value).lower():
            return decrypted_values[0] # obj.pk
