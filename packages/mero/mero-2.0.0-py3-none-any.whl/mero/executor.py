#!/usr/bin/env python3
"""
Mero V2.0 - Executive Execution Engine
محرك التنفيذ المباشر للملفات المحمية
"""

import sys
import os
import hashlib
import struct
from typing import Any, Dict, Optional

class MeroExecutor:
    """محرك تنفيذ الملفات المحمية مباشرة"""
    
    def __init__(self):
        self.execution_cache = {}
        self.security_layers = []
        self._initialize_security()
        
    def _initialize_security(self):
        """تهيئة طبقات الأمان"""
        self.security_layers = [
            self._verify_environment,
            self._check_integrity, 
            self._validate_signature,
            self._decrypt_layers,
            self._prepare_execution
        ]
        
    def _verify_environment(self, data: bytes) -> bool:
        """التحقق من بيئة التنفيذ"""
        # Check if running in Python/Pydroid3/Termux
        platform_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'executable': sys.executable
        }
        
        # Verify compatibility
        if sys.version_info < (3, 6):
            return False
            
        return True
        
    def _check_integrity(self, data: bytes) -> bool:
        """فحص سلامة البيانات"""
        if len(data) < 100:
            return False
            
        # Extract and verify integrity hash
        integrity_hash = data[-32:]
        content = data[:-32]
        
        calculated_hash = hashlib.sha256(content).digest()
        return integrity_hash == calculated_hash
        
    def _validate_signature(self, data: bytes) -> bool:
        """التحقق من التوقيع"""
        # Look for Mero signature
        signatures = [
            b'MeroQuantumDecryptor',
            b'MERO_QUANTUM_V1',
            b'QUANTUM_MATRIX'
        ]
        
        for signature in signatures:
            if signature in data:
                return True
                
        return False
        
    def _decrypt_layers(self, data: bytes) -> bytes:
        """فك طبقات التشفير"""
        try:
            from .quantum_cipher import QuantumCipher
            cipher = QuantumCipher()
            
            # Extract encrypted content
            start_marker = b'QUANTUM_DATA:'
            if start_marker in data:
                start_idx = data.find(start_marker) + len(start_marker)
                end_marker = b':END_QUANTUM'
                end_idx = data.find(end_marker, start_idx)
                
                if end_idx != -1:
                    hex_data = data[start_idx:end_idx]
                    encrypted_bytes = bytes.fromhex(hex_data.decode('ascii'))
                    return cipher.quantum_decrypt(encrypted_bytes)
                    
        except Exception:
            pass
            
        # Return bytes always for consistency
        if isinstance(data, str):
            return data.encode('utf-8')
        return data
        
    def _prepare_execution(self, data: bytes) -> bool:
        """تحضير البيانات للتنفيذ"""
        try:
            # Try to decode as source code
            if isinstance(data, bytes):
                data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
            
    def execute_protected_file(self, file_path: str) -> Any:
        """تنفيذ ملف محمي مباشرة"""
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"Cannot read protected file: {e}")
            
        return self.execute_protected_content(content)
        
    def execute_protected_content(self, content: str) -> Any:
        """تنفيذ محتوى محمي مباشرة"""
        
        # Check if already in cache
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.execution_cache:
            return self.execution_cache[content_hash]
            
        # Extract and execute the protected content
        try:
            # Look for MeroQuantumDecryptor class
            if 'MeroQuantumDecryptor' in content:
                result = self._execute_quantum_protected(content)
            else:
                result = self._execute_standard_protected(content)
                
            # Cache the result
            self.execution_cache[content_hash] = result
            return result
            
        except Exception as e:
            raise RuntimeError(f"Execution failed: {e}")
            
    def _execute_quantum_protected(self, content: str) -> Any:
        """تنفيذ المحتوى المحمي بالتشفير الكمي"""
        
        # Create execution environment
        exec_globals = {
            '__name__': '__main__',
            '__file__': '<mero_protected>',
            'sys': sys,
            'os': os
        }
        
        # Execute the protected content
        try:
            exec(content, exec_globals)
            return exec_globals
        except Exception as e:
            # Try to extract and decrypt manually
            return self._manual_quantum_extraction(content)
            
    def _manual_quantum_extraction(self, content: str) -> Any:
        """استخراج وتنفيذ يدوي للمحتوى الكمي"""
        
        try:
            # Extract hex data
            lines = content.split('\n')
            hex_data = ""
            
            for line in lines:
                if 'fromhex(' in line:
                    start = line.find("'") + 1
                    end = line.rfind("'")
                    if start > 0 and end > start:
                        hex_data = line[start:end]
                        break
                        
            if hex_data:
                # Convert hex to bytes and decrypt
                encrypted_bytes = bytes.fromhex(hex_data)
                
                # Apply security layers
                data_bytes = encrypted_bytes
                for layer in self.security_layers:
                    if not layer(data_bytes):
                        raise ValueError("Security layer validation failed")
                        
                # Decrypt the data
                decrypted = self._decrypt_layers(data_bytes)
                
                if isinstance(decrypted, str):
                    source_code = decrypted
                elif isinstance(decrypted, bytes):
                    source_code = decrypted.decode('utf-8')
                else:
                    source_code = str(decrypted)
                    
                # Execute decrypted source
                exec_globals = {'__name__': '__main__'}
                exec(source_code, exec_globals)
                return exec_globals
                
        except Exception as e:
            raise RuntimeError(f"Manual extraction failed: {e}")
            
        return None
        
    def _execute_standard_protected(self, content: str) -> Any:
        """تنفيذ المحتوى المحمي العادي"""
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': '<mero_protected>',
        }
        
        exec(content, exec_globals)
        return exec_globals
        
    def create_direct_executable(self, source_code: str, output_file: str) -> str:
        """إنشاء ملف تنفيذي مباشر"""
        
        from .quantum_cipher import QuantumCipher
        cipher = QuantumCipher()
        
        # Encrypt the source code
        encrypted_data = cipher.quantum_encrypt(source_code)
        hex_data = encrypted_data.hex()
        
        # Create executable wrapper
        wrapper = f'''#!/usr/bin/env python3
# Mero V2.0 Protected Executable
# تنفيذ مباشر بدون فك تشفير منفصل

import sys
import os

def main():
    try:
        import mero
        
        # Direct execution via mero
        encrypted_hex = '{hex_data}'
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        
        # Decrypt and execute directly
        decrypted = mero.quantum_decrypt(encrypted_bytes)
        
        # Execute the decrypted source
        if isinstance(decrypted, bytes):
            source_code = decrypted.decode('utf-8')
        else:
            source_code = decrypted
            
        # Direct execution
        exec(source_code, {{'__name__': '__main__'}})
        
    except ImportError:
        print("خطأ: مكتبة mero غير مثبتة")
        print("Error: mero library not installed")
        print("Install with: pip install mero")
        sys.exit(1)
    except Exception as e:
        print(f"خطأ في التنفيذ: {{e}}")
        print(f"Execution error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        # Write executable file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wrapper)
            
        # Make executable on Unix systems
        try:
            os.chmod(output_file, 0o755)
        except:
            pass
            
        return output_file
        
    def batch_create_executables(self, source_files: list, output_dir: str) -> list:
        """إنشاء ملفات تنفيذية متعددة"""
        
        os.makedirs(output_dir, exist_ok=True)
        created_files = []
        
        for source_file in source_files:
            if not os.path.exists(source_file):
                continue
                
            # Read source
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Create output filename
            basename = os.path.splitext(os.path.basename(source_file))[0]
            output_file = os.path.join(output_dir, f"{basename}_protected.py")
            
            # Create executable
            self.create_direct_executable(source_code, output_file)
            created_files.append(output_file)
            
        return created_files

# Global executor instance
_executor = None

def get_executor():
    """الحصول على محرك التنفيذ"""
    global _executor
    if _executor is None:
        _executor = MeroExecutor()
    return _executor

def execute_file(file_path: str) -> Any:
    """تنفيذ ملف محمي"""
    executor = get_executor()
    return executor.execute_protected_file(file_path)

def execute_content(content: str) -> Any:
    """تنفيذ محتوى محمي"""
    executor = get_executor()
    return executor.execute_protected_content(content)

def create_executable(source_code: str, output_file: str) -> str:
    """إنشاء ملف تنفيذي"""
    executor = get_executor()
    return executor.create_direct_executable(source_code, output_file)