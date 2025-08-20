import sys
import os
from .core import MeroCore
from .cipher import MeroCipher
from .bytecode import MeroBytecode
from .keymaster import MeroKeymaster
from .platform import MeroPlatform
from .stream import MeroStream
from .hash import MeroHash
from .obfuscator import MeroObfuscator

__version__ = "1.0.0"
__author__ = "Mero Security"
__all__ = [
    "encrypt", "decrypt", "generate_key", "hash_data", 
    "obfuscate_code", "MeroCore", "MeroCipher", "MeroBytecode",
    "MeroKeymaster", "MeroPlatform", "MeroStream", "MeroHash", "MeroObfuscator"
]

_core = MeroCore()
_platform = MeroPlatform()

def encrypt(data, key=None, algorithm="mero_aes"):
    if isinstance(data, str):
        data = data.encode('utf-8')
    if key is None:
        key = MeroKeymaster.generate_secure_key()
    return _core.encrypt(data, key, algorithm)

def decrypt(encrypted_data, key, algorithm="mero_aes"):
    result = _core.decrypt(encrypted_data, key, algorithm)
    if isinstance(result, bytes):
        try:
            decoded = result.decode('utf-8')
            return decoded.rstrip('\x00')
        except UnicodeDecodeError:
            return result
    return result

def generate_key(key_size=256):
    return MeroKeymaster.generate_secure_key(key_size)

def hash_data(data, algorithm="mero_sha"):
    if isinstance(data, str):
        data = data.encode('utf-8')
    hasher = MeroHash()
    return hasher.compute_hash(data, algorithm)

def obfuscate_code(code_string):
    obfuscator = MeroObfuscator()
    return obfuscator.obfuscate_python_code(code_string)

if _platform.is_supported():
    _core.initialize_platform_specific()
