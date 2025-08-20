import struct
import time

class MeroCipher:
    def __init__(self):
        self.sbox = self._generate_sbox()
        self.inv_sbox = self._generate_inv_sbox()
        self.rcon = self._generate_rcon()
        
    def _generate_sbox(self):
        sbox = list(range(256))
        key = 0x9e
        for i in range(256):
            for _ in range(3):
                key = ((key << 1) | (key >> 7)) & 0xFF
                key ^= 0x63
            sbox[i] = key ^ i ^ 0x63
        return sbox
        
    def _generate_inv_sbox(self):
        inv_sbox = [0] * 256
        for i in range(256):
            inv_sbox[self.sbox[i]] = i
        return inv_sbox
        
    def _generate_rcon(self):
        rcon = [1]
        for i in range(1, 10):
            rcon.append((rcon[i-1] << 1) ^ (0x1b if rcon[i-1] & 0x80 else 0))
        return rcon
        
    def _sub_bytes(self, state):
        for i in range(16):
            state[i] = self.sbox[state[i]]
            
    def _inv_sub_bytes(self, state):
        for i in range(16):
            state[i] = self.inv_sbox[state[i]]
            
    def _shift_rows(self, state):
        temp = bytearray(16)
        temp[0] = state[0]; temp[1] = state[5]; temp[2] = state[10]; temp[3] = state[15]
        temp[4] = state[4]; temp[5] = state[9]; temp[6] = state[14]; temp[7] = state[3]
        temp[8] = state[8]; temp[9] = state[13]; temp[10] = state[2]; temp[11] = state[7]
        temp[12] = state[12]; temp[13] = state[1]; temp[14] = state[6]; temp[15] = state[11]
        state[:] = temp
        
    def _inv_shift_rows(self, state):
        temp = bytearray(16)
        temp[0] = state[0]; temp[1] = state[13]; temp[2] = state[10]; temp[3] = state[7]
        temp[4] = state[4]; temp[5] = state[1]; temp[6] = state[14]; temp[7] = state[11]
        temp[8] = state[8]; temp[9] = state[5]; temp[10] = state[2]; temp[11] = state[15]
        temp[12] = state[12]; temp[13] = state[9]; temp[14] = state[6]; temp[15] = state[3]
        state[:] = temp
        
    def _gmul(self, a, b):
        result = 0
        for _ in range(8):
            if b & 1:
                result ^= a
            hi_bit_set = a & 0x80
            a = (a << 1) & 0xFF
            if hi_bit_set:
                a ^= 0x1b
            b >>= 1
        return result
        
    def _mix_columns(self, state):
        for c in range(4):
            col = [state[c], state[c+4], state[c+8], state[c+12]]
            state[c] = self._gmul(2, col[0]) ^ self._gmul(3, col[1]) ^ col[2] ^ col[3]
            state[c+4] = col[0] ^ self._gmul(2, col[1]) ^ self._gmul(3, col[2]) ^ col[3]
            state[c+8] = col[0] ^ col[1] ^ self._gmul(2, col[2]) ^ self._gmul(3, col[3])
            state[c+12] = self._gmul(3, col[0]) ^ col[1] ^ col[2] ^ self._gmul(2, col[3])
            
    def _inv_mix_columns(self, state):
        for c in range(4):
            col = [state[c], state[c+4], state[c+8], state[c+12]]
            state[c] = self._gmul(14, col[0]) ^ self._gmul(11, col[1]) ^ self._gmul(13, col[2]) ^ self._gmul(9, col[3])
            state[c+4] = self._gmul(9, col[0]) ^ self._gmul(14, col[1]) ^ self._gmul(11, col[2]) ^ self._gmul(13, col[3])
            state[c+8] = self._gmul(13, col[0]) ^ self._gmul(9, col[1]) ^ self._gmul(14, col[2]) ^ self._gmul(11, col[3])
            state[c+12] = self._gmul(11, col[0]) ^ self._gmul(13, col[1]) ^ self._gmul(9, col[2]) ^ self._gmul(14, col[3])
            
    def _add_round_key(self, state, round_key):
        for i in range(16):
            state[i] ^= round_key[i]
            
    def _key_expansion(self, key):
        key_size = len(key)
        if key_size == 16:
            rounds = 10
        elif key_size == 24:
            rounds = 12
        elif key_size == 32:
            rounds = 14
        else:
            raise ValueError("Invalid key size")
            
        expanded_key = bytearray(16 * (rounds + 1))
        expanded_key[:key_size] = key
        
        for i in range(key_size, len(expanded_key), 4):
            temp = expanded_key[i-4:i]
            if i % key_size == 0:
                temp = temp[1:] + temp[:1]
                for j in range(4):
                    temp[j] = self.sbox[temp[j]]
                temp[0] ^= self.rcon[i // key_size - 1]
            elif key_size == 32 and i % key_size == 16:
                for j in range(4):
                    temp[j] = self.sbox[temp[j]]
            for j in range(4):
                expanded_key[i+j] = expanded_key[i+j-key_size] ^ temp[j]
                
        return expanded_key
        
    def mero_aes_encrypt(self, plaintext, key, nonce):
        expanded_key = self._key_expansion(key)
        result = bytearray()
        
        counter = int.from_bytes(nonce, 'big')
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            if len(block) < 16:
                block += b'\x00' * (16 - len(block))
                
            counter_block = counter.to_bytes(16, 'big')
            encrypted_counter = self._encrypt_block(bytearray(counter_block), expanded_key)
            
            for j in range(len(block)):
                result.append(block[j] ^ encrypted_counter[j])
                
            counter = (counter + 1) & ((1 << 128) - 1)
            
        return bytes(result)
        
    def mero_aes_decrypt(self, ciphertext, key, nonce):
        return self.mero_aes_encrypt(ciphertext, key, nonce)
        
    def _encrypt_block(self, state, expanded_key):
        rounds = len(expanded_key) // 16 - 1
        
        self._add_round_key(state, expanded_key[0:16])
        
        for round_num in range(1, rounds):
            self._sub_bytes(state)
            self._shift_rows(state)
            self._mix_columns(state)
            self._add_round_key(state, expanded_key[round_num*16:(round_num+1)*16])
            
        self._sub_bytes(state)
        self._shift_rows(state)
        self._add_round_key(state, expanded_key[rounds*16:(rounds+1)*16])
        
        return state
        
    def _decrypt_block(self, state, expanded_key):
        rounds = len(expanded_key) // 16 - 1
        
        self._add_round_key(state, expanded_key[rounds*16:(rounds+1)*16])
        
        for round_num in range(rounds-1, 0, -1):
            self._inv_shift_rows(state)
            self._inv_sub_bytes(state)
            self._add_round_key(state, expanded_key[round_num*16:(round_num+1)*16])
            self._inv_mix_columns(state)
            
        self._inv_shift_rows(state)
        self._inv_sub_bytes(state)
        self._add_round_key(state, expanded_key[0:16])
        
        return state
        
    def mero_stream_encrypt(self, plaintext, key, nonce):
        keystream = self._generate_keystream(key, nonce, len(plaintext))
        result = bytearray()
        for i in range(len(plaintext)):
            result.append(plaintext[i] ^ keystream[i])
        return bytes(result)
        
    def mero_stream_decrypt(self, ciphertext, key, nonce):
        return self.mero_stream_encrypt(ciphertext, key, nonce)
        
    def _generate_keystream(self, key, nonce, length):
        state = [0] * 16
        for i in range(min(len(key), 16)):
            state[i] = key[i]
        for i in range(min(len(nonce), 16)):
            state[i] ^= nonce[i]
            
        keystream = bytearray()
        counter = 0
        
        while len(keystream) < length:
            state[15] = counter & 0xFF
            state[14] = (counter >> 8) & 0xFF
            
            for _ in range(20):
                for i in range(16):
                    state[i] = (state[i] + state[(i+1) % 16]) & 0xFF
                    state[i] = ((state[i] << 1) | (state[i] >> 7)) & 0xFF
                    
            keystream.extend(state)
            counter += 1
            
        return keystream[:length]
        
    def mero_hybrid_encrypt(self, plaintext, key, nonce):
        if len(plaintext) <= 1024:
            return self.mero_aes_encrypt(plaintext, key, nonce)
        else:
            first_part = self.mero_aes_encrypt(plaintext[:512], key, nonce)
            second_part = self.mero_stream_encrypt(plaintext[512:], key, nonce[-8:])
            return first_part + second_part
            
    def mero_hybrid_decrypt(self, ciphertext, key, nonce):
        if len(ciphertext) <= 1024:
            return self.mero_aes_decrypt(ciphertext, key, nonce)
        else:
            first_part = self.mero_aes_decrypt(ciphertext[:512], key, nonce)
            second_part = self.mero_stream_decrypt(ciphertext[512:], key, nonce[-8:])
            return first_part + second_part
