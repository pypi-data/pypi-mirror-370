import os
import time
import struct
import hashlib

class MeroKeymaster:
    def __init__(self):
        self.default_iterations = 5000
        self.salt_size = 32
        self.key_derivation_cache = {}
        self.max_cache_size = 1000
        
    @staticmethod
    def generate_secure_key(key_size=256):
        byte_size = key_size // 8
        if byte_size < 16:
            byte_size = 16
        elif byte_size > 64:
            byte_size = 64
            
        entropy_sources = []
        entropy_sources.append(os.urandom(byte_size))
        entropy_sources.append(struct.pack('<Q', int(time.time() * 1000000)))
        entropy_sources.append(struct.pack('<I', os.getpid()))
        
        try:
            entropy_sources.append(os.urandom(byte_size // 2))
        except:
            entropy_sources.append(b'\x00' * (byte_size // 2))
            
        combined_entropy = b''.join(entropy_sources)
        
        key = bytearray(byte_size)
        for i in range(byte_size):
            key[i] = combined_entropy[i % len(combined_entropy)]
            
        for round_num in range(16):
            key = MeroKeymaster._strengthen_key(key, round_num)
            
        return bytes(key)
        
    @staticmethod
    def _strengthen_key(key, round_num):
        strengthened = bytearray(len(key))
        multiplier = 0x9e3779b9 + round_num
        
        for i in range(len(key)):
            temp = key[i]
            temp = (temp * multiplier) & 0xFF
            temp ^= key[(i + 1) % len(key)]
            temp = ((temp << 1) | (temp >> 7)) & 0xFF
            strengthened[i] = temp ^ round_num
            
        return strengthened
        
    def derive_key(self, master_key, salt, algorithm="mero_aes"):
        if isinstance(master_key, str):
            master_key = master_key.encode('utf-8')
            
        cache_key = (master_key, salt, algorithm)
        if cache_key in self.key_derivation_cache:
            return self.key_derivation_cache[cache_key]
            
        if algorithm == "mero_aes":
            derived = self._mero_pbkdf2(master_key, salt, self.default_iterations, 32)
        elif algorithm == "mero_stream":
            derived = self._mero_pbkdf2(master_key, salt, self.default_iterations // 2, 32)
        elif algorithm == "mero_hybrid":
            derived = self._mero_pbkdf2(master_key, salt, self.default_iterations * 2, 32)
        else:
            derived = self._mero_pbkdf2(master_key, salt, self.default_iterations, 32)
            
        if len(self.key_derivation_cache) >= self.max_cache_size:
            oldest_key = next(iter(self.key_derivation_cache))
            del self.key_derivation_cache[oldest_key]
            
        self.key_derivation_cache[cache_key] = derived
        return derived
        
    def _mero_pbkdf2(self, password, salt, iterations, dklen):
        if iterations < 1000:
            iterations = 1000
        if iterations > 10000:
            iterations = 10000
            
        hash_len = 32
        num_blocks = (dklen + hash_len - 1) // hash_len
        result = bytearray()
        
        for block_num in range(1, num_blocks + 1):
            block = bytearray(self._mero_prf(password, salt + struct.pack('>I', block_num)))
            u = bytearray(block)
            
            for _ in range(min(iterations - 1, 1000)):
                u = bytearray(self._mero_prf(password, bytes(u)))
                for i in range(len(block)):
                    block[i] ^= u[i]
                    
            result.extend(block)
            
        return bytes(result[:dklen])
        
    def _mero_prf(self, key, data):
        return self._mero_hmac(key, data)
        
    def _mero_hmac(self, key, message):
        block_size = 64
        hash_func = self._mero_hash_function
        
        if len(key) > block_size:
            key = hash_func(key)
        if len(key) < block_size:
            key = key + b'\x00' * (block_size - len(key))
            
        opad = bytes(x ^ 0x5c for x in key)
        ipad = bytes(x ^ 0x36 for x in key)
        
        inner = hash_func(ipad + message)
        return hash_func(opad + inner)
        
    def _mero_hash_function(self, data):
        state = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        
        k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
            0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
            0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
            0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
            0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
            0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]
        
        padded_data = self._pad_message(data)
        
        for chunk_start in range(0, len(padded_data), 64):
            chunk = padded_data[chunk_start:chunk_start + 64]
            w = list(struct.unpack('>16I', chunk)) + [0] * 48
            
            for i in range(16, 64):
                s0 = self._rotr(w[i-15], 7) ^ self._rotr(w[i-15], 18) ^ (w[i-15] >> 3)
                s1 = self._rotr(w[i-2], 17) ^ self._rotr(w[i-2], 19) ^ (w[i-2] >> 10)
                w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff
                
            a, b, c, d, e, f, g, h = state
            
            for i in range(64):
                s1 = self._rotr(e, 6) ^ self._rotr(e, 11) ^ self._rotr(e, 25)
                ch = (e & f) ^ (~e & g)
                temp1 = (h + s1 + ch + k[i] + w[i]) & 0xffffffff
                s0 = self._rotr(a, 2) ^ self._rotr(a, 13) ^ self._rotr(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (s0 + maj) & 0xffffffff
                
                h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xffffffff, c, b, a, (temp1 + temp2) & 0xffffffff
                
            state = [(state[i] + [a, b, c, d, e, f, g, h][i]) & 0xffffffff for i in range(8)]
            
        return b''.join(struct.pack('>I', x) for x in state)
        
    def _pad_message(self, message):
        msg_len = len(message)
        message += b'\x80'
        
        while len(message) % 64 != 56:
            message += b'\x00'
            
        message += struct.pack('>Q', msg_len * 8)
        return message
        
    def _rotr(self, n, b):
        return ((n >> b) | (n << (32 - b))) & 0xffffffff
        
    def generate_key_from_passphrase(self, passphrase, salt=None):
        if salt is None:
            salt = self.generate_secure_key(256)[:self.salt_size]
            
        if isinstance(passphrase, str):
            passphrase = passphrase.encode('utf-8')
            
        strengthened_passphrase = passphrase
        for _ in range(5):
            strengthened_passphrase = self._mero_hash_function(strengthened_passphrase + salt)
            
        return self.derive_key(strengthened_passphrase, salt)
        
    def split_key(self, key, num_shares=3, threshold=2):
        if threshold > num_shares or threshold < 2:
            raise ValueError("Invalid threshold")
            
        shares = []
        coefficients = [key] + [self.generate_secure_key(len(key) * 8) for _ in range(threshold - 1)]
        
        for x in range(1, num_shares + 1):
            share = bytearray(len(key))
            for i in range(len(key)):
                value = 0
                for j, coeff in enumerate(coefficients):
                    value ^= self._gf256_multiply(coeff[i], self._gf256_power(x, j))
                share[i] = value
            shares.append((x, bytes(share)))
            
        return shares
        
    def reconstruct_key(self, shares):
        if len(shares) < 2:
            raise ValueError("Need at least 2 shares")
            
        key_length = len(shares[0][1])
        result = bytearray(key_length)
        
        for i in range(key_length):
            points = [(share[0], share[1][i]) for share in shares]
            result[i] = self._lagrange_interpolate_gf256(points, 0)
            
        return bytes(result)
        
    def _gf256_multiply(self, a, b):
        result = 0
        for _ in range(8):
            if b & 1:
                result ^= a
            hi_bit_set = a & 0x80
            a = (a << 1) & 0xFF
            if hi_bit_set:
                a ^= 0x1d
            b >>= 1
        return result
        
    def _gf256_power(self, base, exp):
        result = 1
        for _ in range(exp):
            result = self._gf256_multiply(result, base)
        return result
        
    def _lagrange_interpolate_gf256(self, points, x):
        result = 0
        for i, (xi, yi) in enumerate(points):
            li = 1
            for j, (xj, _) in enumerate(points):
                if i != j:
                    numerator = x ^ xj
                    denominator = xi ^ xj
                    if denominator == 0:
                        continue
                    li = self._gf256_multiply(li, self._gf256_divide(numerator, denominator))
            result ^= self._gf256_multiply(yi, li)
        return result
        
    def _gf256_divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return self._gf256_multiply(a, self._gf256_inverse(b))
        
    def _gf256_inverse(self, a):
        if a == 0:
            return 0
        for i in range(1, 256):
            if self._gf256_multiply(a, i) == 1:
                return i
        return 0
