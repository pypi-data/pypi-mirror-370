import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

base_requirements = [
    'loguru==0.6.0',
    'pyyaml~=6.0.2',
    'aiohttp>=3.11.10',
    'aiofiles~=24.1.0',
]

extras_require = {
    'service': [
        'uvloop~=0.21.0',
        'pytz==2025.2',
        'psutil==7.0.0',
        'aiohttp>=3.12.13',
        'httpx==0.25.2',
        'aiofiles~=24.1.0',
        'python-dotenv==0.21.1',
        'pydantic==2.11.7',
        'PyJWT==2.10.1',
        'redis==6.2.0',
        'tortoise-orm==0.19.0',
        'aiomysql==0.2.0',
        'fastapi==0.115.13',
        'uvicorn[standard]==0.29.0',
        'gunicorn==23.0.0',
        'cryptography==45.0.4',
        'pymilvus==2.4.2',
        'marshmallow==3.13.0',
        'qdrant-client==1.14.3',
        'grpcio==1.60.0',
        'grpcio-tools==1.60.0',
        'protobuf==4.21.6',
        'aiokafka==0.12.0',
        'nats-py==2.10.0'
    ],
    'llm': [
        'boto3~=1.34.79',
        'openai~=1.90.0',
        'anthropic~=0.42.0',
        'tiktoken==0.8.0',
        'litellm==1.75.0'
    ]
}

extras_require['all'] = [
    dep for deps in extras_require.values() for dep in deps
]

setuptools.setup(
    name='descartcan',
    version='2025.8.20.2',
    description='A Python toolkit for advanced data processing and API interactions',
    author='DescartCan',
    author_email='louishwh@gmail.com',
    url='',
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    install_requires=base_requirements,
    extras_require=extras_require,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/DescartCan/python_kit/issues",
        "Documentation": "https://doc.descart.com/",
        "Source Code": "https://github.com/DescartCan/python_kit",
    },
    keywords='api, toolkit'
)