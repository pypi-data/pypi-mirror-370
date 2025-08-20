import os
import struct
import hashlib
from .platform import MeroPlatform

class QuantumCipher:
    def __init__(self):
        self.platform = MeroPlatform()
        self._init_quantum_constants()
        
    def _init_quantum_constants(self):
        platform_info = self.platform.get_platform_info()
        system_hash = hash(f"{platform_info['system']}-{platform_info['arch']}")
        
        self.QUANTUM_PRIME_1 = 0x1F2E3D4C5B6A79685947362518F4E3D2
        self.QUANTUM_PRIME_2 = 0x9E8D7C6B5A49382716F5E4D3C2B1A098
        self.QUANTUM_PRIME_3 = 0x8C7B6A5948372615F4E3D2C1B0A09887
        
        self.QUANTUM_MATRIX = [
            [0x6A, 0x4F, 0x92, 0x3E, 0x81, 0xC5, 0x27, 0xB3],
            [0x95, 0x18, 0x7D, 0x42, 0xAE, 0x60, 0xF9, 0x34],
            [0x2B, 0x87, 0x5C, 0xE1, 0x46, 0x93, 0x0F, 0x72],
            [0xD8, 0x53, 0x1A, 0x6E, 0xB4, 0x29, 0x85, 0x47],
            [0x71, 0xCF, 0x38, 0x94, 0x2D, 0x86, 0x5B, 0xE0],
            [0x4A, 0x15, 0x79, 0xBE, 0x63, 0xA8, 0x37, 0xD2],
            [0x91, 0x56, 0x2F, 0x84, 0xC9, 0x1E, 0x73, 0xB7],
            [0x05, 0x4B, 0x97, 0x3C, 0x82, 0x6F, 0xA4, 0x59]
        ]
        
        self.SYSTEM_ENTROPY = abs(system_hash) % 0xFFFFFFFF
        
    def _quantum_hash(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        result = bytearray(32)
        entropy = self.SYSTEM_ENTROPY
        
        for i, byte in enumerate(data):
            pos = i % 32
            entropy = (entropy * self.QUANTUM_PRIME_1 + byte) % 0xFFFFFFFFFFFFFFFF
            matrix_row = (entropy >> 8) % 8
            matrix_col = entropy % 8
            
            quantum_byte = self.QUANTUM_MATRIX[matrix_row][matrix_col]
            result[pos] ^= ((quantum_byte ^ byte ^ (entropy & 0xFF)) & 0xFF)
            
        for round_num in range(16):
            for i in range(32):
                prev_i = (i - 1) % 32
                next_i = (i + 1) % 32
                
                temp = (result[prev_i] ^ result[next_i] ^ 
                       ((self.QUANTUM_PRIME_2 >> (i % 64)) & 0xFF)) & 0xFF
                result[i] = ((result[i] + temp) % 256) & 0xFF
                
        return bytes(result)
        
    def _generate_quantum_key(self, seed_data):
        base_hash = self._quantum_hash(seed_data)
        expanded_key = bytearray()
        
        current = base_hash
        for expansion in range(8):
            next_hash = self._quantum_hash(current + struct.pack('<Q', expansion))
            expanded_key.extend(next_hash)
            current = next_hash
            
        return bytes(expanded_key[:256])
        
    def _quantum_encrypt_block(self, block, key_segment):
        encrypted = bytearray(len(block))
        
        for i, byte in enumerate(block):
            key_idx = i % len(key_segment)
            entropy_shift = (self.QUANTUM_PRIME_3 >> (i % 64)) & 0xFF
            
            matrix_selector = (byte + key_segment[key_idx] + entropy_shift) % 64
            matrix_row = (matrix_selector >> 3) % 8
            matrix_col = matrix_selector % 8
            
            quantum_transform = self.QUANTUM_MATRIX[matrix_row][matrix_col]
            
            encrypted[i] = ((byte ^ key_segment[key_idx] ^ quantum_transform ^ 
                           (self.SYSTEM_ENTROPY >> (i % 32))) & 0xFF)
            
        return bytes(encrypted)
        
    def _quantum_decrypt_block(self, block, key_segment):
        decrypted = bytearray(len(block))
        
        for i, byte in enumerate(block):
            key_idx = i % len(key_segment)
            entropy_shift = (self.QUANTUM_PRIME_3 >> (i % 64)) & 0xFF
            
            original_byte = ((byte ^ key_segment[key_idx] ^ 
                            (self.SYSTEM_ENTROPY >> (i % 32))) & 0xFF)
            
            matrix_selector = (original_byte + key_segment[key_idx] + entropy_shift) % 64
            matrix_row = (matrix_selector >> 3) % 8
            matrix_col = matrix_selector % 8
            
            quantum_transform = self.QUANTUM_MATRIX[matrix_row][matrix_col]
            
            decrypted[i] = (original_byte ^ quantum_transform) & 0xFF
            
        return bytes(decrypted)
        
    def quantum_encrypt(self, data, custom_seed=None):
        # Store original data type
        is_text = isinstance(data, str)
        if is_text:
            data = data.encode('utf-8')
            
        if custom_seed is None:
            custom_seed = os.urandom(16)
        elif isinstance(custom_seed, str):
            custom_seed = custom_seed.encode('utf-8')
            
        quantum_key = self._generate_quantum_key(custom_seed)
        
        header = bytearray()
        header.extend(b'MERO_QUANTUM_V1')
        header.extend(struct.pack('<I', len(data)))
        header.extend(struct.pack('B', 1 if is_text else 0))  # Data type flag
        header.extend(custom_seed[:16])
        
        encrypted_data = bytearray()
        block_size = 64
        
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            key_offset = (i // block_size) % (len(quantum_key) - 32)
            key_segment = quantum_key[key_offset:key_offset + 32]
            
            encrypted_block = self._quantum_encrypt_block(block, key_segment)
            encrypted_data.extend(encrypted_block)
            
        verification_hash = self._quantum_hash(encrypted_data)
        
        final_result = bytearray()
        final_result.extend(header)
        final_result.extend(encrypted_data)
        final_result.extend(verification_hash)
        
        return bytes(final_result)
        
    def quantum_decrypt(self, encrypted_data):
        if len(encrypted_data) < 68:  # Updated minimum size for new header format
            raise ValueError("Invalid quantum encrypted data")
            
        offset = 0
        
        magic = encrypted_data[offset:offset + 15]
        if magic != b'MERO_QUANTUM_V1':
            raise ValueError("Invalid quantum encryption header")
        offset += 15
        
        original_length = struct.unpack('<I', encrypted_data[offset:offset + 4])[0]
        offset += 4
        
        is_text = struct.unpack('B', encrypted_data[offset:offset + 1])[0] == 1
        offset += 1
        
        seed = encrypted_data[offset:offset + 16]
        offset += 16
        
        quantum_key = self._generate_quantum_key(seed)
        
        data_end = len(encrypted_data) - 32
        cipher_data = encrypted_data[offset:data_end]
        stored_hash = encrypted_data[data_end:]
        
        computed_hash = self._quantum_hash(cipher_data)
        if stored_hash != computed_hash:
            raise ValueError("Quantum data integrity verification failed")
            
        decrypted_data = bytearray()
        block_size = 64
        
        for i in range(0, len(cipher_data), block_size):
            block = cipher_data[i:i + block_size]
            key_offset = (i // block_size) % (len(quantum_key) - 32)
            key_segment = quantum_key[key_offset:key_offset + 32]
            
            decrypted_block = self._quantum_decrypt_block(block, key_segment)
            decrypted_data.extend(decrypted_block)
            
        result_data = bytes(decrypted_data[:original_length])
        
        # Return as text if originally was text
        if is_text:
            return result_data.decode('utf-8')
        else:
            return result_data
        
    def create_quantum_executable(self, source_code, identifier=None):
        if identifier is None:
            identifier = os.urandom(8).hex()
            
        platform_signature = f"{self.platform.get_platform_info()}-{identifier}"
        encrypted_code = self.quantum_encrypt(source_code, platform_signature)
        
        hex_data = encrypted_code.hex()
        
        stub_template = f'''#!/usr/bin/env python3
import sys
import os

class MeroQuantumDecryptor:
    def __init__(self):
        self.data = bytes.fromhex('{hex_data}')
        self.QUANTUM_PRIME_1 = 0x1F2E3D4C5B6A79685947362518F4E3D2
        self.QUANTUM_PRIME_2 = 0x9E8D7C6B5A49382716F5E4D3C2B1A098
        self.QUANTUM_PRIME_3 = 0x8C7B6A5948372615F4E3D2C1B0A09887
        self.QUANTUM_MATRIX = [
            [0x6A, 0x4F, 0x92, 0x3E, 0x81, 0xC5, 0x27, 0xB3],
            [0x95, 0x18, 0x7D, 0x42, 0xAE, 0x60, 0xF9, 0x34],
            [0x2B, 0x87, 0x5C, 0xE1, 0x46, 0x93, 0x0F, 0x72],
            [0xD8, 0x53, 0x1A, 0x6E, 0xB4, 0x29, 0x85, 0x47],
            [0x71, 0xCF, 0x38, 0x94, 0x2D, 0x86, 0x5B, 0xE0],
            [0x4A, 0x15, 0x79, 0xBE, 0x63, 0xA8, 0x37, 0xD2],
            [0x91, 0x56, 0x2F, 0x84, 0xC9, 0x1E, 0x73, 0xB7],
            [0x05, 0x4B, 0x97, 0x3C, 0x82, 0x6F, 0xA4, 0x59]
        ]
        
    def quantum_decrypt(self):
        import struct
        data = self.data
        if len(data) < 64 or data[:15] != b'MERO_QUANTUM_V1':
            raise ValueError("Invalid data")
        
        original_length = struct.unpack('<I', data[15:19])[0]
        seed = data[19:35]
        
        platform_info = self._get_platform_signature()
        system_hash = hash(platform_info)
        SYSTEM_ENTROPY = abs(system_hash) % 0xFFFFFFFF
        
        quantum_key = self._generate_quantum_key(seed, SYSTEM_ENTROPY)
        
        cipher_data = data[35:-32]
        decrypted_data = bytearray()
        
        for i in range(0, len(cipher_data), 64):
            block = cipher_data[i:i + 64]
            key_offset = (i // 64) % (len(quantum_key) - 32)
            key_segment = quantum_key[key_offset:key_offset + 32]
            
            decrypted_block = self._quantum_decrypt_block(block, key_segment, SYSTEM_ENTROPY)
            decrypted_data.extend(decrypted_block)
            
        return decrypted_data[:original_length].decode('utf-8')
        
    def _get_platform_signature(self):
        import platform
        return f"{{platform.system()}}-{{platform.machine()}}-{identifier}"
        
    def _quantum_hash(self, data, entropy):
        if isinstance(data, str):
            data = data.encode('utf-8')
        result = bytearray(32)
        for i, byte in enumerate(data):
            pos = i % 32
            entropy = (entropy * self.QUANTUM_PRIME_1 + byte) % 0xFFFFFFFFFFFFFFFF
            matrix_row = (entropy >> 8) % 8
            matrix_col = entropy % 8
            quantum_byte = self.QUANTUM_MATRIX[matrix_row][matrix_col]
            result[pos] ^= ((quantum_byte ^ byte ^ (entropy & 0xFF)) & 0xFF)
        for round_num in range(16):
            for i in range(32):
                prev_i = (i - 1) % 32
                next_i = (i + 1) % 32
                temp = (result[prev_i] ^ result[next_i] ^ ((self.QUANTUM_PRIME_2 >> (i % 64)) & 0xFF)) & 0xFF
                result[i] = ((result[i] + temp) % 256) & 0xFF
        return bytes(result)
        
    def _generate_quantum_key(self, seed_data, entropy):
        base_hash = self._quantum_hash(seed_data, entropy)
        expanded_key = bytearray()
        current = base_hash
        for expansion in range(8):
            import struct
            next_hash = self._quantum_hash(current + struct.pack('<Q', expansion), entropy)
            expanded_key.extend(next_hash)
            current = next_hash
        return bytes(expanded_key[:256])
        
    def _quantum_decrypt_block(self, block, key_segment, entropy):
        decrypted = bytearray(len(block))
        for i, byte in enumerate(block):
            key_idx = i % len(key_segment)
            entropy_shift = (self.QUANTUM_PRIME_3 >> (i % 64)) & 0xFF
            original_byte = ((byte ^ key_segment[key_idx] ^ (entropy >> (i % 32))) & 0xFF)
            matrix_selector = (original_byte + key_segment[key_idx] + entropy_shift) % 64
            matrix_row = (matrix_selector >> 3) % 8
            matrix_col = matrix_selector % 8
            quantum_transform = self.QUANTUM_MATRIX[matrix_row][matrix_col]
            decrypted[i] = (original_byte ^ quantum_transform) & 0xFF
        return bytes(decrypted)

if __name__ == "__main__":
    try:
        decryptor = MeroQuantumDecryptor()
        source_code = decryptor.quantum_decrypt()
        exec(source_code)
    except Exception as e:
        print(f"Quantum decryption failed: {{e}}")
        sys.exit(1)
'''
        
        return stub_template