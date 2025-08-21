import os
from setuptools import setup, find_packages

# Read the long description from README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='certbot-dns-micetro',
    version='1.0.0',
    packages=find_packages(),
    description="Certbot plugin for Micetro DNS authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nat Biggs",
    author_email='nbiggs112@cedarville.edu',
    url="https://github.com/cedarville-university/certbot-dns-micetro",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="certbot micetro dns ssl certificate letsencrypt",
    license="Apache License 2.0",
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        'certbot>=1.1.0',
        'zope.interface',
        'requests>=2.20.0',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-micetro = certbot_dns_micetro.dns_micetro:Authenticator'
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/cedarville-university/certbot-dns-micetro/issues",
        "Source": "https://github.com/cedarville-university/certbot-dns-micetro",
    },
)