import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Crypto:
    IV_LENGTH = 12
    TAG_LENGTH = 16

    def __init__(self, key_string: str):
        if len(key_string) != 32:
            raise ValueError('Key must be 32 characters')
        self.key = key_string.encode('utf-8')
        self.aesgcm = AESGCM(self.key)

    def to_url_safe(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

    def from_url_safe(self, data: str) -> bytes:
        padding = '=' * ((4 - len(data) % 4) % 4)
        return base64.urlsafe_b64decode(data + padding)

    def encrypt(self, plain_text: str) -> str:
        iv = os.urandom(self.IV_LENGTH)
        ct_with_tag = self.aesgcm.encrypt(iv, plain_text.encode('utf-8'), None)
        payload = iv + ct_with_tag
        return self.to_url_safe(payload)

    def decrypt(self, enc_data: str) -> str:
        raw = self.from_url_safe(enc_data)
        iv = raw[: self.IV_LENGTH]
        ct_with_tag = raw[self.IV_LENGTH :]
        plain = self.aesgcm.decrypt(iv, ct_with_tag, None)
        return plain.decode('utf-8')
