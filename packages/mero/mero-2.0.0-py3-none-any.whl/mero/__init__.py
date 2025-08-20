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
from .quantum_cipher import QuantumCipher
from .megabytes import get_mega_engine, compile_mega, execute_mega
from .executor import get_executor, execute_file, execute_content

__version__ = "2.0.0"
__author__ = "Mero Security"
__all__ = [
    "encrypt", "decrypt", "generate_key", "hash_data", 
    "obfuscate_code", "protect_file", "create_executable",
    "quantum_encrypt", "quantum_decrypt", "exec_protected",
    "compile_to_mega_bytecode", "execute_mega_bytecode",
    "MeroCore", "MeroCipher", "MeroBytecode",
    "MeroKeymaster", "MeroPlatform", "MeroStream", "MeroHash", "MeroObfuscator",
    "QuantumCipher"
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

def protect_file(source_file, output_file=None, key=None):
    from .protector import MeroProtector
    protector = MeroProtector()
    if output_file is None:
        output_file = os.path.splitext(source_file)[0] + '_protected.py'
    return protector.protect_file(source_file, output_file, key)

def create_executable(source_file, output_name=None):
    from .protector import MeroProtector
    protector = MeroProtector()
    return protector.create_executable(source_file, output_name)

# V2.0 Quantum cipher functions
def quantum_encrypt(data, custom_seed=None):
    """تشفير كمي متقدم - V2.0"""
    cipher = QuantumCipher()
    return cipher.quantum_encrypt(data, custom_seed)

def quantum_decrypt(encrypted_data):
    """فك التشفير الكمي - V2.0"""
    cipher = QuantumCipher()
    return cipher.quantum_decrypt(encrypted_data)

# V2.0 Mega bytecode functions  
def compile_to_mega_bytecode(source_code, complexity=10):
    """تجميع إلى بايتكود ضخم - V2.0"""
    engine = get_mega_engine()
    return engine.compile_to_mega_bytecode(source_code, complexity)

def execute_mega_bytecode(bytecode, globals_dict=None):
    """تنفيذ بايتكود ضخم - V2.0"""
    engine = get_mega_engine()
    return engine.execute_mega_bytecode(bytecode, globals_dict)

# V2.0 Direct execution functions
def exec_protected(file_or_content):
    """تنفيذ مباشر exec() للملفات المحمية - V2.0"""
    executor = get_executor()
    if '\n' in str(file_or_content) or len(str(file_or_content)) > 500:
        # Content detected
        return executor.execute_protected_content(str(file_or_content))
    else:
        # File path detected
        return executor.execute_protected_file(str(file_or_content))

if _platform.is_supported():
    _core.initialize_platform_specific()
