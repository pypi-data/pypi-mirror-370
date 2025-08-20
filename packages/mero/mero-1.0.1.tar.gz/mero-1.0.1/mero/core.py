import os
import sys
import time
import struct
from .cipher import MeroCipher
from .bytecode import MeroBytecode
from .keymaster import MeroKeymaster
from .platform import MeroPlatform

class MeroCore:
    def __init__(self):
        self.cipher = MeroCipher()
        self.bytecode = MeroBytecode()
        self.keymaster = MeroKeymaster()
        self.platform = MeroPlatform()
        self.initialized = False
        self._entropy_pool = bytearray(4096)
        self._entropy_index = 0
        self._magic_constants = [
            0x9e3779b9, 0x6a09e667, 0xbb67ae85, 0x3c6ef372,
            0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
            0x5be0cd19, 0xcbbb9d5d, 0x629a292a, 0x9159015a,
            0x152fecd8, 0x67332667, 0x8eb44a87, 0xdb0c2e0d
        ]
        
    def initialize_platform_specific(self):
        if self.initialized:
            return
        
        platform_info = self.platform.get_platform_info()
        self._init_entropy_sources(platform_info)
        self._init_cpu_features(platform_info)
        self.initialized = True
        
    def _init_entropy_sources(self, platform_info):
        entropy_sources = []
        entropy_sources.append(os.urandom(256))
        entropy_sources.append(struct.pack('<Q', int(time.time() * 1000000)))
        entropy_sources.append(str(id(self)).encode())
        
        if platform_info['os'] == 'posix':
            try:
                with open('/dev/urandom', 'rb') as f:
                    entropy_sources.append(f.read(128))
            except:
                pass
                
        combined = b''.join(entropy_sources)
        for i, byte in enumerate(combined):
            self._entropy_pool[i % len(self._entropy_pool)] ^= byte
            
    def _init_cpu_features(self, platform_info):
        self._cpu_rounds = 12 if platform_info['arch'] == 'x86_64' else 8
        self._simd_available = platform_info.get('simd', False)
        
    def _get_entropy_bytes(self, count):
        result = bytearray()
        for _ in range(count):
            self._entropy_index = (self._entropy_index + 1) % len(self._entropy_pool)
            result.append(self._entropy_pool[self._entropy_index])
            self._entropy_pool[self._entropy_index] ^= (int(time.time() * 1000000) & 0xFF)
        return bytes(result)
        
    def encrypt(self, data, key, algorithm="mero_aes"):
        if not self.initialized:
            self.initialize_platform_specific()
            
        nonce = self._get_entropy_bytes(16)
        salt = self._get_entropy_bytes(32)
        
        derived_key = self.keymaster.derive_key(key, salt, algorithm)
        
        if algorithm == "mero_aes":
            encrypted = self.cipher.mero_aes_encrypt(data, derived_key, nonce)
        elif algorithm == "mero_stream":
            encrypted = self.cipher.mero_stream_encrypt(data, derived_key, nonce)
        elif algorithm == "mero_hybrid":
            encrypted = self.cipher.mero_hybrid_encrypt(data, derived_key, nonce)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        header = self._create_header(algorithm, salt, nonce)
        return header + encrypted
        
    def decrypt(self, encrypted_data, key, algorithm="mero_aes"):
        if not self.initialized:
            self.initialize_platform_specific()
            
        header_size = 64
        if len(encrypted_data) < header_size:
            raise ValueError("Invalid encrypted data")
            
        header = encrypted_data[:header_size]
        ciphertext = encrypted_data[header_size:]
        
        algo, salt, nonce = self._parse_header(header)
        if algo != algorithm:
            raise ValueError("Algorithm mismatch")
            
        derived_key = self.keymaster.derive_key(key, salt, algorithm)
        
        if algorithm == "mero_aes":
            return self.cipher.mero_aes_decrypt(ciphertext, derived_key, nonce)
        elif algorithm == "mero_stream":
            return self.cipher.mero_stream_decrypt(ciphertext, derived_key, nonce)
        elif algorithm == "mero_hybrid":
            return self.cipher.mero_hybrid_decrypt(ciphertext, derived_key, nonce)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
    def _create_header(self, algorithm, salt, nonce):
        header = bytearray(64)
        header[0:4] = b'MERO'
        header[4] = 1
        header[5] = len(algorithm)
        algo_bytes = algorithm.encode()
        header[6:6+len(algo_bytes)] = algo_bytes
        header[16:48] = salt
        header[48:64] = nonce
        return bytes(header)
        
    def _parse_header(self, header):
        if header[0:4] != b'MERO':
            raise ValueError("Invalid header")
        version = header[4]
        if version != 1:
            raise ValueError("Unsupported version")
        algo_len = header[5]
        algorithm = header[6:6+algo_len].decode()
        salt = header[16:48]
        nonce = header[48:64]
        return algorithm, salt, nonce
