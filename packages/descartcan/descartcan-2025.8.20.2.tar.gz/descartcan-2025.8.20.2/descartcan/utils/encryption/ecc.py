import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidKey, UnsupportedAlgorithm


class ECCCipher:
    CURVE = ec.SECP521R1()
    HASH_ALGORITHM = hashes.SHA512()
    HASH_LENGTH = 64
    DERIVED_KEY_LENGTH = 64
    AES_KEY_LENGTH = 32
    IV_LENGTH = 16
    INFO = b"ecc-encryption"

    def __init__(self, private_key=None, public_key=None):
        if private_key and public_key:
            self.private_key = private_key
            self.public_key = public_key
        else:
            self.private_key, self.public_key = self.generate_key_pair()

    def generate_key_pair(self):
        private_key = ec.generate_private_key(self.CURVE)
        public_key = private_key.public_key()
        return private_key, public_key

    def encrypt(self, plaintext: bytes, peer_public_key) -> bytes:
        try:
            shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)
            derived_key = HKDF(
                algorithm=self.HASH_ALGORITHM,
                length=self.DERIVED_KEY_LENGTH,
                salt=None,
                info=self.INFO,
            ).derive(shared_key)
            iv = os.urandom(self.IV_LENGTH)
            cipher = Cipher(
                algorithms.AES(derived_key[: self.AES_KEY_LENGTH]), modes.CBC(iv)
            )
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return iv + ciphertext
        except ValueError as e:
            raise ValueError(f"Encryption failed: {str(e)}")
        except InvalidKey:
            raise ValueError("Encryption failed: Invalid public key.")
        except UnsupportedAlgorithm:
            raise ValueError("Encryption failed: Unsupported algorithm.")
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    def decrypt(self, ciphertext: bytes, peer_public_key) -> bytes:
        try:
            iv = ciphertext[: self.IV_LENGTH]
            ciphertext = ciphertext[self.IV_LENGTH :]
            shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)
            derived_key = HKDF(
                algorithm=self.HASH_ALGORITHM,
                length=self.DERIVED_KEY_LENGTH,
                salt=None,
                info=self.INFO,
            ).derive(shared_key)
            cipher = Cipher(
                algorithms.AES(derived_key[: self.AES_KEY_LENGTH]), modes.CBC(iv)
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            return plaintext
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
        return serialization.load_pem_private_key(
            private_key_pem,
            password=None,
        )

    @staticmethod
    def deserialize_public_key(public_key_pem: bytes):
        return serialization.load_pem_public_key(public_key_pem)
