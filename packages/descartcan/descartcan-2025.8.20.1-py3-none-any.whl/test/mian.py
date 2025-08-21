# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/22 12:14
# Author     ：Maxwell
# Description：
"""
import uvicorn

from descartcan.service.app import application


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application, host="127.0.0.1", port=8001)
