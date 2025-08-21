import time

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidKey, UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend


class RSACipher:
    HASH_ALGORITHM = hashes.SHA512()
    HASH_LENGTH = 64
    PADDING_OVERHEAD = 2 * HASH_LENGTH + 2
    KEY_SIZE = 4096
    MAX_ENCRYPT_LENGTH = (KEY_SIZE // 8) - PADDING_OVERHEAD

    def __init__(self, private_key=None, public_key=None):
        if private_key:
            self.private_key = private_key
        if public_key:
            self.public_key = public_key
        if not private_key and not public_key:
            self.private_key, self.public_key = self.generate_key_pair()

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.KEY_SIZE,
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def encrypt(self, plaintext: bytes) -> bytes:
        try:
            if len(plaintext) > self.MAX_ENCRYPT_LENGTH:
                raise ValueError(
                    f"Plaintext too long. Max length is {self.MAX_ENCRYPT_LENGTH} bytes."
                )

            return self.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=self.HASH_ALGORITHM),
                    algorithm=self.HASH_ALGORITHM,
                    label=None,
                ),
            )
        except ValueError as e:
            raise ValueError(f"Encryption failed: {str(e)}")
        except InvalidKey:
            raise ValueError("Encryption failed: Invalid public key.")
        except UnsupportedAlgorithm:
            raise ValueError("Encryption failed: Unsupported algorithm.")
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt(self, ciphertext: bytes) -> bytes:
        try:
            return self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=self.HASH_ALGORITHM),
                    algorithm=self.HASH_ALGORITHM,
                    label=None,
                ),
            )
        except ValueError as e:
            raise ValueError(f"Decryption failed: {str(e)}")
        except InvalidKey:
            raise ValueError("Decryption failed: Invalid private key.")
        except UnsupportedAlgorithm:
            raise ValueError("Decryption failed: Unsupported algorithm.")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def serialize_private_key(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def serialize_public_key(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @staticmethod
    def deserialize_private_key(private_key_pem: bytes):
        try:
            return serialization.load_pem_private_key(
                private_key_pem, password=None, backend=default_backend()
            )
        except ValueError as e:
            print(f"Error deserializing private key: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error deserializing private key: {e}")
            raise

    @staticmethod
    def deserialize_public_key(public_key_pem: bytes):
        try:
            return serialization.load_pem_public_key(
                public_key_pem, backend=default_backend()
            )
        except ValueError as e:
            print(f"Error deserializing public key: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error deserializing public key: {e}")
            raise
