from setuptools import setup, find_packages

setup(
    name="mero",
    version="1.0.0",
    description="Professional-grade Python encryption library with custom bytecode implementation",
    long_description="Ultra-secure encryption library with custom bytecode generation and cross-platform support",
    author="Mero Security",
    author_email="security@mero.dev",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="encryption cryptography security bytecode obfuscation",
    project_urls={
        "Documentation": "https://mero-crypto.readthedocs.io/",
        "Source": "https://github.com/mero-security/mero",
        "Tracker": "https://github.com/mero-security/mero/issues",
    },
)
