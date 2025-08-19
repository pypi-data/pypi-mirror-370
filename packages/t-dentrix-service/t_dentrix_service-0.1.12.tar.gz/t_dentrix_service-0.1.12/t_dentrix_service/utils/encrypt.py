"""This module contains the encryption methods for the Dentrix API."""
import binascii

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def encrypt_with_rsa(message: str, public_key: dict) -> str:
    """Method to RSA encrypt at string."""
    modulus = int(public_key["rsaPublicKey"], 16)
    exponent = int(public_key["rsaExponent"], 16)

    key_components = (modulus, exponent)
    rsa_key = RSA.construct(key_components)

    message_bytes = message.encode("utf-8")

    # Encrypt the message
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted_message = cipher.encrypt(message_bytes)
    # Return Hexadecimal encoded result (typical for RSA encrypted data)
    return binascii.hexlify(encrypted_message).decode("ascii")
