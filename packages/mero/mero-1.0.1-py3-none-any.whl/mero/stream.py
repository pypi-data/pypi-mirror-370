import struct
import time

class MeroStream:
    def __init__(self):
        self.state_size = 256
        self.rounds = 20
        self.constants = [
            0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5
        ]
        
    def encrypt_stream(self, plaintext, key, nonce=None):
        if nonce is None:
            nonce = struct.pack('<Q', int(time.time() * 1000000))
            
        keystream = self._generate_mero_stream(key, nonce, len(plaintext))
        ciphertext = bytearray()
        
        for i in range(len(plaintext)):
            ciphertext.append(plaintext[i] ^ keystream[i])
            
        return bytes(ciphertext)
        
    def decrypt_stream(self, ciphertext, key, nonce):
        return self.encrypt_stream(ciphertext, key, nonce)
        
    def _generate_mero_stream(self, key, nonce, length):
        state = self._initialize_state(key, nonce)
        keystream = bytearray()
        counter = 0
        
        while len(keystream) < length:
            block = self._generate_block(state, counter)
            keystream.extend(block)
            counter += 1
            
        return keystream[:length]
        
    def _initialize_state(self, key, nonce):
        state = [0] * 16
        
        state[0:4] = self.constants[0:4]
        
        if len(key) >= 32:
            for i in range(8):
                state[4 + i] = struct.unpack('<I', key[i*4:(i+1)*4])[0]
        else:
            key = key + b'\x00' * (32 - len(key))
            for i in range(8):
                state[4 + i] = struct.unpack('<I', key[i*4:(i+1)*4])[0]
                
        if len(nonce) >= 8:
            state[12] = struct.unpack('<I', nonce[0:4])[0]
            state[13] = struct.unpack('<I', nonce[4:8])[0]
        else:
            nonce = nonce + b'\x00' * (8 - len(nonce))
            state[12] = struct.unpack('<I', nonce[0:4])[0]
            state[13] = struct.unpack('<I', nonce[4:8])[0]
            
        state[14] = 0
        state[15] = 0
        
        return state
        
    def _generate_block(self, initial_state, counter):
        state = initial_state.copy()
        state[14] = counter & 0xffffffff
        state[15] = (counter >> 32) & 0xffffffff
        
        working_state = state.copy()
        
        for _ in range(self.rounds):
            self._quarter_round(working_state, 0, 4, 8, 12)
            self._quarter_round(working_state, 1, 5, 9, 13)
            self._quarter_round(working_state, 2, 6, 10, 14)
            self._quarter_round(working_state, 3, 7, 11, 15)
            
            self._quarter_round(working_state, 0, 5, 10, 15)
            self._quarter_round(working_state, 1, 6, 11, 12)
            self._quarter_round(working_state, 2, 7, 8, 13)
            self._quarter_round(working_state, 3, 4, 9, 14)
            
        for i in range(16):
            working_state[i] = (working_state[i] + state[i]) & 0xffffffff
            
        block = bytearray()
        for word in working_state:
            block.extend(struct.pack('<I', word))
            
        return block
        
    def _quarter_round(self, state, a, b, c, d):
        state[a] = (state[a] + state[b]) & 0xffffffff
        state[d] ^= state[a]
        state[d] = self._rotl32(state[d], 16)
        
        state[c] = (state[c] + state[d]) & 0xffffffff
        state[b] ^= state[c]
        state[b] = self._rotl32(state[b], 12)
        
        state[a] = (state[a] + state[b]) & 0xffffffff
        state[d] ^= state[a]
        state[d] = self._rotl32(state[d], 8)
        
        state[c] = (state[c] + state[d]) & 0xffffffff
        state[b] ^= state[c]
        state[b] = self._rotl32(state[b], 7)
        
    def _rotl32(self, value, amount):
        return ((value << amount) | (value >> (32 - amount))) & 0xffffffff
        
    def create_authenticated_stream(self, plaintext, key, nonce=None, associated_data=b''):
        if nonce is None:
            nonce = struct.pack('<Q', int(time.time() * 1000000))
            
        auth_key = self._derive_auth_key(key, nonce)
        ciphertext = self.encrypt_stream(plaintext, key, nonce)
        
        tag = self._compute_auth_tag(auth_key, associated_data, ciphertext, nonce)
        
        return ciphertext + tag
        
    def decrypt_authenticated_stream(self, authenticated_ciphertext, key, nonce, associated_data=b''):
        if len(authenticated_ciphertext) < 16:
            raise ValueError("Invalid authenticated ciphertext")
            
        ciphertext = authenticated_ciphertext[:-16]
        received_tag = authenticated_ciphertext[-16:]
        
        auth_key = self._derive_auth_key(key, nonce)
        expected_tag = self._compute_auth_tag(auth_key, associated_data, ciphertext, nonce)
        
        if not self._constant_time_compare(received_tag, expected_tag):
            raise ValueError("Authentication tag verification failed")
            
        return self.decrypt_stream(ciphertext, key, nonce)
        
    def _derive_auth_key(self, key, nonce):
        auth_state = self._initialize_state(key, nonce)
        auth_state[12] = 0xffffffff
        auth_state[13] = 0xffffffff
        
        auth_block = self._generate_block(auth_state, 0)
        return auth_block[:32]
        
    def _compute_auth_tag(self, auth_key, associated_data, ciphertext, nonce):
        poly_key = auth_key[:32]
        
        mac_data = bytearray()
        mac_data.extend(associated_data)
        mac_data.extend(b'\x00' * ((16 - len(associated_data) % 16) % 16))
        mac_data.extend(ciphertext)
        mac_data.extend(b'\x00' * ((16 - len(ciphertext) % 16) % 16))
        mac_data.extend(struct.pack('<Q', len(associated_data)))
        mac_data.extend(struct.pack('<Q', len(ciphertext)))
        
        return self._poly1305(poly_key, mac_data)
        
    def _poly1305(self, key, message):
        r = struct.unpack('<IIII', key[:16])
        r = [(r[i] & 0x0fffffff) if i < 3 else (r[i] & 0x0ffffffc) for i in range(4)]
        
        s = struct.unpack('<IIII', key[16:32])
        
        accumulator = [0, 0, 0, 0, 0]
        
        for i in range(0, len(message), 16):
            block = message[i:i+16]
            if len(block) < 16:
                block += b'\x00' * (16 - len(block))
                
            n = struct.unpack('<IIII', block) + (1,)
            
            for j in range(5):
                accumulator[j] += n[j]
                
            self._poly1305_multiply(accumulator, r)
            
        for i in range(4):
            accumulator[i] += s[i]
            
        return struct.pack('<IIII', *accumulator[:4])
        
    def _poly1305_multiply(self, a, r):
        p = 0x3fffffffb
        
        result = [0] * 9
        for i in range(5):
            for j in range(5):
                result[i + j] += a[i] * r[j]
                
        for i in range(4, 9):
            carry = result[i]
            result[i - 4] += carry * 5
            result[i] = 0
            
        for i in range(4):
            carry = result[i] >> 32
            result[i] &= 0xffffffff
            result[i + 1] += carry
            
        a[:4] = result[:4]
        a[4] = result[4] & 3
        
    def _constant_time_compare(self, a, b):
        if len(a) != len(b):
            return False
            
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
            
        return result == 0
        
    def generate_keystream_only(self, key, nonce, length):
        return self._generate_mero_stream(key, nonce, length)
        
    def seek_stream_position(self, key, nonce, position):
        block_size = 64
        block_number = position // block_size
        offset = position % block_size
        
        state = self._initialize_state(key, nonce)
        block = self._generate_block(state, block_number)
        
        return block[offset:]
