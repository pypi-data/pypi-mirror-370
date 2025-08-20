import struct

class MeroHash:
    def __init__(self):
        self.sha256_h = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        
        self.sha256_k = [
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
        
        self.mero_iv = [
            0x9e3779b9, 0x6a09e667, 0xbb67ae85, 0x3c6ef372,
            0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab
        ]
        
    def compute_hash(self, data, algorithm="mero_sha"):
        if algorithm == "mero_sha":
            return self._mero_sha256(data)
        elif algorithm == "mero_blake":
            return self._mero_blake2b(data)
        elif algorithm == "mero_custom":
            return self._mero_custom_hash(data)
        else:
            raise ValueError(f"Unknown hash algorithm: {algorithm}")
            
    def _mero_sha256(self, data):
        h = self.mero_iv.copy()
        
        padded_data = self._pad_sha256(data)
        
        for chunk_start in range(0, len(padded_data), 64):
            chunk = padded_data[chunk_start:chunk_start + 64]
            w = list(struct.unpack('>16I', chunk)) + [0] * 48
            
            for i in range(16, 64):
                s0 = self._rotr(w[i-15], 7) ^ self._rotr(w[i-15], 18) ^ (w[i-15] >> 3)
                s1 = self._rotr(w[i-2], 17) ^ self._rotr(w[i-2], 19) ^ (w[i-2] >> 10)
                w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff
                
            a, b, c, d, e, f, g, h_temp = h
            
            for i in range(64):
                s1 = self._rotr(e, 6) ^ self._rotr(e, 11) ^ self._rotr(e, 25)
                ch = (e & f) ^ (~e & g)
                temp1 = (h_temp + s1 + ch + self.sha256_k[i] + w[i]) & 0xffffffff
                s0 = self._rotr(a, 2) ^ self._rotr(a, 13) ^ self._rotr(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (s0 + maj) & 0xffffffff
                
                h_temp, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xffffffff, c, b, a, (temp1 + temp2) & 0xffffffff
                
            h = [(h[i] + [a, b, c, d, e, f, g, h_temp][i]) & 0xffffffff for i in range(8)]
            
        return b''.join(struct.pack('>I', x) for x in h)
        
    def _mero_blake2b(self, data, digest_size=32):
        h = [
            0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
            0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
            0x510e527fade682d1, 0x9b05688c2b3e6c1f,
            0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
        ]
        
        h[0] ^= 0x01010000 ^ digest_size
        
        padded_data = data + b'\x00' * ((128 - len(data) % 128) % 128)
        
        for i in range(0, len(padded_data), 128):
            chunk = padded_data[i:i+128]
            is_last = (i + 128 >= len(padded_data))
            bytes_compressed = i + len(chunk) if not is_last else len(data)
            
            h = self._blake2b_compress(h, chunk, bytes_compressed, is_last)
            
        result = b''.join(struct.pack('<Q', x) for x in h)
        return result[:digest_size]
        
    def _blake2b_compress(self, h, chunk, bytes_compressed, is_last):
        sigma = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
            [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
            [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
            [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
            [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
            [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
            [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
            [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
            [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0]
        ]
        
        iv = [
            0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
            0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
            0x510e527fade682d1, 0x9b05688c2b3e6c1f,
            0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
        ]
        
        v = h[:8] + iv[:4] + [iv[4] ^ bytes_compressed, iv[5], iv[6], iv[7]]
        
        if is_last:
            v[14] ^= 0xffffffffffffffff
            
        m = list(struct.unpack('<16Q', chunk))
        
        for round_num in range(12):
            s = sigma[round_num % 10]
            
            self._blake2b_mix(v, 0, 4, 8, 12, m[s[0]], m[s[1]])
            self._blake2b_mix(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
            self._blake2b_mix(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
            self._blake2b_mix(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
            
            self._blake2b_mix(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
            self._blake2b_mix(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
            self._blake2b_mix(v, 2, 7, 8, 13, m[s[12]], m[s[13]])
            self._blake2b_mix(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
            
        return [h[i] ^ v[i] ^ v[i + 8] for i in range(8)]
        
    def _blake2b_mix(self, v, a, b, c, d, x, y):
        v[a] = (v[a] + v[b] + x) & 0xffffffffffffffff
        v[d] = self._rotr64(v[d] ^ v[a], 32)
        v[c] = (v[c] + v[d]) & 0xffffffffffffffff
        v[b] = self._rotr64(v[b] ^ v[c], 24)
        v[a] = (v[a] + v[b] + y) & 0xffffffffffffffff
        v[d] = self._rotr64(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & 0xffffffffffffffff
        v[b] = self._rotr64(v[b] ^ v[c], 63)
        
    def _mero_custom_hash(self, data):
        state = self.mero_iv.copy()
        
        padded_data = data + b'\x80'
        while len(padded_data) % 64 != 56:
            padded_data += b'\x00'
        padded_data += struct.pack('>Q', len(data) * 8)
        
        for chunk_start in range(0, len(padded_data), 64):
            chunk = padded_data[chunk_start:chunk_start + 64]
            words = list(struct.unpack('>16I', chunk))
            
            for round_num in range(16):
                for i in range(8):
                    state[i] = (state[i] + words[round_num % 16]) & 0xffffffff
                    state[i] = self._rotr(state[i], (round_num + i) % 32)
                    state[i] ^= state[(i + 1) % 8]
                    
                temp = state[0]
                for i in range(7):
                    state[i] = state[i + 1]
                state[7] = temp
                
        return b''.join(struct.pack('>I', x) for x in state)
        
    def _pad_sha256(self, data):
        msg_len = len(data)
        data += b'\x80'
        
        while len(data) % 64 != 56:
            data += b'\x00'
            
        data += struct.pack('>Q', msg_len * 8)
        return data
        
    def _rotr(self, n, b):
        return ((n >> b) | (n << (32 - b))) & 0xffffffff
        
    def _rotr64(self, n, b):
        return ((n >> b) | (n << (64 - b))) & 0xffffffffffffffff
        
    def hmac(self, key, message, algorithm="mero_sha"):
        block_size = 64
        
        if len(key) > block_size:
            key = self.compute_hash(key, algorithm)
        if len(key) < block_size:
            key = key + b'\x00' * (block_size - len(key))
            
        opad = bytes(x ^ 0x5c for x in key)
        ipad = bytes(x ^ 0x36 for x in key)
        
        inner = self.compute_hash(ipad + message, algorithm)
        return self.compute_hash(opad + inner, algorithm)
        
    def pbkdf2(self, password, salt, iterations, dklen, algorithm="mero_sha"):
        if isinstance(password, str):
            password = password.encode('utf-8')
            
        hash_len = 32
        num_blocks = (dklen + hash_len - 1) // hash_len
        result = bytearray()
        
        for block_num in range(1, num_blocks + 1):
            u = self.hmac(password, salt + struct.pack('>I', block_num), algorithm)
            block = bytearray(u)
            
            for _ in range(iterations - 1):
                u = self.hmac(password, u, algorithm)
                for i in range(len(block)):
                    block[i] ^= u[i]
                    
            result.extend(block)
            
        return bytes(result[:dklen])
        
    def merkle_tree_root(self, data_blocks, algorithm="mero_sha"):
        if not data_blocks:
            return b'\x00' * 32
            
        current_level = [self.compute_hash(block, algorithm) for block in data_blocks]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = self.compute_hash(left + right, algorithm)
                next_level.append(combined)
            current_level = next_level
            
        return current_level[0]
        
    def compute_file_hash(self, file_path, algorithm="mero_sha", chunk_size=8192):
        hash_obj = self._create_hasher(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            return hash_obj.finalize()
        except IOError as e:
            raise RuntimeError(f"Failed to hash file {file_path}: {e}")
            
    def _create_hasher(self, algorithm):
        return MeroHasher(self, algorithm)
        
class MeroHasher:
    def __init__(self, hash_instance, algorithm):
        self.hash_instance = hash_instance
        self.algorithm = algorithm
        self.buffer = bytearray()
        
    def update(self, data):
        self.buffer.extend(data)
        
    def finalize(self):
        return self.hash_instance.compute_hash(bytes(self.buffer), self.algorithm)
