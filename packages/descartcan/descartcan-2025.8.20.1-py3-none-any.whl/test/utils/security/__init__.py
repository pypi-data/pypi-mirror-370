# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 19:33
# Author     ：Maxwell
# Description：
"""
from descartcan.utils.security.ecc import ECCCipher


if __name__ == '__main__':
    alice_cipher = ECCCipher()
    bob_cipher = ECCCipher()

    plaintext = b"Hello, ECC encryption asdfasdfasdfasdfasdfaasdfsadfasdfasdfasdfasdf!"
    ciphertext = alice_cipher.encrypt(plaintext, bob_cipher.public_key)
    print("Ciphertext:", ciphertext.hex())

    decrypted_text = bob_cipher.decrypt(ciphertext, alice_cipher.public_key)
    print("Decrypted text:", decrypted_text.decode('utf-8'))


# if __name__ == '__main__':
#
#     times = 100000
#     s = time.time_ns()
#     for i in range(0, times):
#         aes_cipher = AESCipher()
#         plaintext = "Hello, AES encryption!"
#         ciphertext = aes_cipher.encrypt(plaintext)
#         # print("Ciphertext:", ciphertext)
#         decrypted_text = aes_cipher.decrypt(ciphertext)
#         # print("Decrypted text:", decrypted_text)
#         # print("AES Key:", aes_cipher.get_key())
#     e = time.time_ns()
#     print(f"use time: {(e-s)/1000_000}")
