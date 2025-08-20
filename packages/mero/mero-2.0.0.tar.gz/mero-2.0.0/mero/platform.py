import sys
import os
import platform
import subprocess

class MeroPlatform:
    def __init__(self):
        self.platform_info = self._detect_platform()
        self.supported_platforms = {
            'windows': ['win32', 'cygwin'],
            'linux': ['linux', 'linux2'],
            'darwin': ['darwin'],
            'android': ['linux'],
            'ios': ['darwin']
        }
        
    def _detect_platform(self):
        info = {
            'system': platform.system().lower(),
            'machine': platform.machine().lower(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version_info,
            'os': os.name,
            'platform_module': sys.platform
        }
        
        info['is_android'] = self._is_android()
        info['is_ios'] = self._is_ios()
        info['is_termux'] = self._is_termux()
        info['arch'] = self._get_architecture()
        info['simd'] = self._has_simd_support()
        info['entropy_sources'] = self._get_entropy_sources()
        
        return info
        
    def _is_android(self):
        try:
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                return 'android' in version
        except:
            pass
            
        try:
            result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                 capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            pass
            
        return 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ
        
    def _is_ios(self):
        return (sys.platform == 'darwin' and 
                (os.uname().machine.startswith('iPhone') or 
                 os.uname().machine.startswith('iPad')))
                 
    def _is_termux(self):
        return ('PREFIX' in os.environ and 
                '/data/data/com.termux' in os.environ.get('PREFIX', ''))
                
    def _get_architecture(self):
        arch = platform.machine().lower()
        if arch in ['x86_64', 'amd64']:
            return 'x86_64'
        elif arch in ['i386', 'i686', 'x86']:
            return 'x86'
        elif arch.startswith('arm'):
            if '64' in arch:
                return 'arm64'
            return 'arm'
        elif arch.startswith('aarch64'):
            return 'arm64'
        else:
            return arch
            
    def _has_simd_support(self):
        arch = self._get_architecture()
        if arch == 'x86_64':
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    return any(flag in cpuinfo for flag in ['sse2', 'avx', 'avx2'])
            except:
                pass
        elif arch in ['arm', 'arm64']:
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    return 'neon' in cpuinfo or 'asimd' in cpuinfo
            except:
                pass
        return False
        
    def _get_entropy_sources(self):
        sources = []
        
        if os.path.exists('/dev/urandom'):
            sources.append('/dev/urandom')
        if os.path.exists('/dev/random'):
            sources.append('/dev/random')
            
        system = platform.system().lower()
        if system == 'windows':
            sources.append('CryptGenRandom')
            
        is_android = self._is_android()
        if is_android:
            sources.append('/dev/hw_random')
            
        return sources
        
    def get_platform_info(self):
        return self.platform_info.copy()
        
    def is_supported(self):
        system = self.platform_info['system']
        platform_module = self.platform_info['platform_module']
        
        for supported_system, platforms in self.supported_platforms.items():
            if system == supported_system or platform_module in platforms:
                return True
                
        return self.platform_info['is_android'] or self.platform_info['is_ios']
        
    def get_optimal_settings(self):
        arch = self.platform_info['arch']
        is_mobile = self.platform_info['is_android'] or self.platform_info['is_ios']
        
        settings = {
            'encryption_rounds': 10,
            'key_derivation_iterations': 100000,
            'memory_limit': 64 * 1024 * 1024,
            'thread_count': 1,
            'use_simd': False
        }
        
        if arch == 'x86_64':
            settings['encryption_rounds'] = 14
            settings['key_derivation_iterations'] = 150000
            settings['memory_limit'] = 128 * 1024 * 1024
            settings['thread_count'] = 2
            settings['use_simd'] = self.platform_info.get('simd', False)
            
        elif arch == 'arm64':
            settings['encryption_rounds'] = 12
            settings['key_derivation_iterations'] = 120000
            
        if is_mobile:
            settings['memory_limit'] //= 2
            settings['key_derivation_iterations'] //= 2
            
        if self.platform_info['is_termux']:
            settings['memory_limit'] //= 4
            
        return settings
        
    def get_secure_temp_dir(self):
        temp_dirs = []
        
        if self.platform_info['system'] == 'windows':
            temp_dirs.extend([
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                'C:\\Windows\\Temp'
            ])
        else:
            temp_dirs.extend([
                '/tmp',
                '/var/tmp',
                os.environ.get('TMPDIR'),
                os.environ.get('TMP')
            ])
            
        if self.platform_info['is_android']:
            temp_dirs.insert(0, '/data/local/tmp')
            
        if self.platform_info['is_termux']:
            temp_dirs.insert(0, os.environ.get('PREFIX', '') + '/tmp')
            
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir) and os.access(temp_dir, os.W_OK):
                return temp_dir
                
        return os.getcwd()
        
    def supports_feature(self, feature):
        features = {
            'hardware_acceleration': self.platform_info.get('simd', False),
            'secure_memory': not (self.platform_info['is_android'] or self.platform_info['is_ios']),
            'file_locking': self.platform_info['system'] != 'windows',
            'process_isolation': not self.platform_info['is_ios'],
            'network_crypto': True,
            'persistent_storage': True
        }
        
        return features.get(feature, False)
        
    def get_performance_profile(self):
        if self.platform_info['arch'] == 'x86_64' and not self.platform_info['is_android']:
            return 'high_performance'
        elif self.platform_info['arch'] in ['arm64', 'x86_64']:
            return 'balanced'
        else:
            return 'low_power'
            
    def setup_platform_specific_optimizations(self):
        optimizations = {}
        
        if self.platform_info['system'] == 'windows':
            optimizations['use_cryptoapi'] = True
            
        elif self.platform_info['system'] == 'linux':
            optimizations['use_getrandom'] = True
            
        if self.platform_info['is_android']:
            optimizations['use_android_keystore'] = True
            
        if self.platform_info['is_ios']:
            optimizations['use_secure_enclave'] = True
            
        return optimizations
