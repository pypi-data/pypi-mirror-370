# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/7/2 23:22
# Author     ：Maxwell
# Description：
"""
# !/usr/bin/env python
# -*-coding:utf-8 -*-

import os
import uvicorn
import argparse
from descartcan.config.config import APP_HOST, APP_PORT


# =====================================================
# Gunicorn 配置
# =====================================================

def get_gunicorn_config():
    """返回Gunicorn配置字典"""
    log_dir = "./logs/gunicorn"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
        # 基本配置
        "daemon": True,
        "bind": f"{APP_HOST}:{APP_PORT}",
        "chdir": "./",
        "pidfile": "./gunicorn.pid",
        "worker_class": "uvicorn.workers.UvicornWorker",

        # 进程和连接
        "threads": 2,
        "timeout": 30,
        "keepalive": 5,
        "max_requests": 4000,
        "graceful_timeout": 30,
        "worker_connections": 1000,
        "max_requests_jitter": 1000,
        "workers": 1,

        # 日志配置
        "loglevel": "info",
        "capture_output": True,
        "enable_stdio_inheritance": False,
        "errorlog": os.path.join(log_dir, "error.log"),
        "accesslog": os.path.join(log_dir, "access.log"),
        "access_log_format": '%(t)s [%(p)s] %(h)s "%(r)s" %(s)s %(L)s %(b)s "%(f)s" "%(a)s"',

        # 安全和性能设置
        "preload_app": True,
        "proc_name": "gunicorn-app",
        "limit_request_line": 4096,
        "limit_request_fields": 100,
        "limit_request_field_size": 8190,
    }


def generate_gunicorn_config_file(filename="gunicorn_config.py"):
    """生成Gunicorn配置文件"""
    config = get_gunicorn_config()

    with open(filename, "w") as f:
        f.write("# !/usr/bin/env python\n")
        f.write("# -*-coding:utf-8 -*-\n\n")
        f.write('"""Gunicorn配置文件，自动生成"""\n\n')

        for key, value in config.items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f'{key} = {value}\n')

    return filename


# =====================================================
# 启动函数
# =====================================================

def run_with_uvicorn():
    """使用Uvicorn直接运行应用"""
    app = init_application()
    print(f"应用将在 {APP_HOST}:{APP_PORT} 启动...")
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)


def run_with_gunicorn(config_file=None, ):
    """使用Gunicorn运行应用"""
    if not config_file:
        config_file = generate_gunicorn_config_file()

    app_module = "main:application"  # 假设此文件名为main.py
    cmd = f"gunicorn {app_module} -c {config_file}"

    print(f"启动Gunicorn: {cmd}")
    os.system(cmd)


# =====================================================
# 主函数
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="应用启动器")
    parser.add_argument("--mode", choices=["uvicorn", "gunicorn"], default="uvicorn",
                        help="启动模式: uvicorn (直接运行) 或 gunicorn (生产环境)")
    parser.add_argument("--config", help="Gunicorn配置文件路径 (仅在gunicorn模式下使用)")

    args = parser.parse_args()

    if args.mode == "uvicorn":
        run_with_uvicorn()
    else:
        run_with_gunicorn(args.config)


if __name__ == "__main__":
    main()