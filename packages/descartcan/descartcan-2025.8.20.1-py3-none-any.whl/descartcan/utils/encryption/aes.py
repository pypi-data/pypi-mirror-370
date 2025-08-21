import os
import base64
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidKey, UnsupportedAlgorithm


class AESCipher:
    BLOCK_SIZE = algorithms.AES.block_size
    KEY_SIZE = 32
    IV_SIZE = int(BLOCK_SIZE / 8)

    def __init__(self, key: bytes = None):
        if key:
            if len(key) != self.KEY_SIZE:
                raise ValueError(f"Key must be {self.KEY_SIZE} bytes long.")
            self.key = key
        else:
            self.key = os.urandom(self.KEY_SIZE)

    def encrypt(self, plaintext: str) -> str:
        try:
            iv = os.urandom(self.IV_SIZE)
            padder = padding.PKCS7(self.BLOCK_SIZE).padder()
            padded_data = padder.update(plaintext.encode("utf-8")) + padder.finalize()
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(iv + ciphertext).decode("utf-8")
        except ValueError as e:
            raise ValueError(f"Encryption failed: {str(e)}")
        except InvalidKey:
            raise ValueError("Encryption failed: Invalid key.")
        except UnsupportedAlgorithm:
            raise ValueError("Encryption failed: Unsupported algorithm.")
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt(self, ciphertext: str) -> str:
        try:
            encrypted_data = base64.b64decode(ciphertext.encode("utf-8"))
            iv = encrypted_data[: self.IV_SIZE]
            ciphertext = encrypted_data[self.IV_SIZE :]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(self.BLOCK_SIZE).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            return plaintext.decode("utf-8")
        except ValueError as e:
            raise ValueError(f"Decryption failed: {str(e)}")
        except InvalidKey:
            raise ValueError("Decryption failed: Invalid key.")
        except UnsupportedAlgorithm:
            raise ValueError("Decryption failed: Unsupported algorithm.")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def get_key(self) -> str:
        return base64.b64encode(self.key).decode("utf-8")

    @classmethod
    def get_key_bytes(cls, base64_bytes: bytes) -> bytes:
        base64_str = base64_bytes.decode("utf-8")
        return base64.b64decode(base64_str)
