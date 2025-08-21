# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/21 19:36
# Author     ：Maxwell
# Description：
"""
import os
import hashlib
import uuid
import time
import random


class HashManager(object):

    @classmethod
    def md5(cls, content: str) -> str:
        if not content:
            content = ""
        md5_hash = hashlib.md5()
        md5_hash.update(content.encode("utf-8"))
        return md5_hash.hexdigest()

    @classmethod
    def sha256(cls, content: str) -> str:
        if not content:
            content = ""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content.encode("utf-8"))
        return sha256_hash.hexdigest().upper()

    @classmethod
    def is_sha256(cls, string):
        if len(string) != 64:
            return False
        try:
            hashlib.sha256(string.encode()).hexdigest()
            return True
        except ValueError:
            return False

    @classmethod
    def uuid(cls) -> str:
        random_part = random.getrandbits(128)
        unique_str = f"{uuid.uuid1().hex}_{int(time.time())}_{random_part}"
        return hashlib.sha256(unique_str.encode()).hexdigest().upper()

    @classmethod
    def time_hash(cls) -> str:
        pid = os.getpid()
        time_ns = time.time_ns()
        random_id = random.randint(0, 100_0000_0000)
        return f"{pid}-{time_ns}-{random_id}"

    @classmethod
    def time_and_random(cls) -> int:
        time_ns = time.time_ns()
        random_id = str(random.randint(0, 99999999)).zfill(8)
        return int(f"{random_id}{time_ns}")
