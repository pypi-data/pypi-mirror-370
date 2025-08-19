# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="bpcode",
    version="0.4.3",
    author="zhuoyue",
    author_email="2814401134@qq.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=3.0",
        "django-cors-headers",
        "python-dotenv",
        "whitenoise"
    ],
    entry_points={
        'console_scripts': [
            'bpserver = bpcode.cli:main',
            'bpdown = bpcode.bpdown:main',
            'bpnas = bpcode.startnas:main',
        ],
    },
    description="auto backup your code",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/avegetableman/bpcode",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
