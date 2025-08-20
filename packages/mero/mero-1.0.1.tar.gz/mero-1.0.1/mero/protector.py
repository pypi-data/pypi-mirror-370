import os
import sys
from .quantum_cipher import QuantumCipher

class MeroProtector:
    def __init__(self):
        self.quantum_cipher = QuantumCipher()
        
    def protect_file(self, source_file, output_file, identifier=None):
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        if identifier is None:
            identifier = os.urandom(8).hex()
            
        # Use quantum cipher for ultra-secure protection
        protected_stub = self.quantum_cipher.create_quantum_executable(source_code, identifier)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(protected_stub)
            
        os.chmod(output_file, 0o755)
        return identifier
        

        
    def create_executable(self, source_file, output_name=None):
        if output_name is None:
            output_name = os.path.splitext(source_file)[0] + '_protected.py'
            
        identifier = self.protect_file(source_file, output_name)
        
        print(f"Quantum protected: {output_name}")
        print(f"Identity signature: {identifier}")
        
        return output_name, identifier
        
    def protect_directory(self, source_dir, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        protected_files = []
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py'):
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, source_dir)
                    output_path = os.path.join(output_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    identifier = self.protect_file(source_path, output_path)
                    protected_files.append((output_path, identifier))
                    
        return protected_files
        
    def verify_protection(self, protected_file):
        try:
            with open(protected_file, 'r') as f:
                content = f.read()
                
            if 'MeroQuantumDecryptor' in content and 'QUANTUM_MATRIX' in content:
                return True
            return False
        except:
            return False
            
    def extract_metadata(self, protected_file):
        try:
            with open(protected_file, 'r') as f:
                content = f.read()
                
            if 'MeroQuantumDecryptor' in content:
                hex_start = content.find("self.data = bytes.fromhex('") + 27
                hex_end = content.find("')", hex_start)
                
                if hex_start > 26 and hex_end > hex_start:
                    hex_data = content[hex_start:hex_end]
                    return {
                        'encryption_type': 'Quantum Cipher',
                        'data_size': len(hex_data) // 2,
                        'protected': True,
                        'quantum_level': 'Maximum Security'
                    }
                    
            return {'protected': False}
        except:
            return {'protected': False}

def protect_file(source_file, output_file=None, identifier=None):
    protector = MeroProtector()
    if output_file is None:
        output_file = os.path.splitext(source_file)[0] + '_protected.py'
    return protector.protect_file(source_file, output_file, identifier)

def create_executable(source_file, output_name=None):
    protector = MeroProtector()
    return protector.create_executable(source_file, output_name)