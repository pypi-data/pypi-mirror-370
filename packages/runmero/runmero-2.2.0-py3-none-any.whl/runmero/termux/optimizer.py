# حقوق الطبع والنشر محفوظة © 2025 mero - من قلب القدس الشريفة فلسطين

import os
import sys
import subprocess
import threading
import time
import signal
import psutil
from typing import Dict, List, Any, Optional
import json

class TermuxOptimizer:
    def __init__(self):
        self.is_termux = self._detect_termux()
        self.optimizations = {}
        self.background_processes = []
        self.system_monitor = None
        self.battery_optimizer = None
        self.memory_manager = None
        
    def _detect_termux(self) -> bool:
        return (
            os.path.exists('/data/data/com.termux') or
            os.getenv('TERMUX_VERSION') is not None or
            os.path.exists('/system/bin/am') or
            'termux' in os.getenv('PREFIX', '').lower()
        )
    
    def optimize_for_android(self):
        if not self.is_termux:
            return False
            
        optimizations = []
        
        try:
            self._optimize_cpu_governor()
            optimizations.append("CPU Governor")
        except:
            pass
            
        try:
            self._optimize_memory_management()
            optimizations.append("Memory Management")
        except:
            pass
            
        try:
            self._optimize_network_settings()
            optimizations.append("Network Settings")
        except:
            pass
            
        try:
            self._optimize_battery_usage()
            optimizations.append("Battery Usage")
        except:
            pass
            
        try:
            self._setup_background_persistence()
            optimizations.append("Background Persistence")
        except:
            pass
            
        self.optimizations['android'] = optimizations
        return len(optimizations) > 0
    
    def _optimize_cpu_governor(self):
        try:
            cpu_paths = [
                '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor',
                '/sys/devices/system/cpu/cpufreq/policy0/scaling_governor'
            ]
            
            for path in cpu_paths:
                if os.path.exists(path):
                    try:
                        with open(path, 'w') as f:
                            f.write('performance')
                        break
                    except PermissionError:
                        pass
                        
        except Exception:
            pass
    
    def _optimize_memory_management(self):
        try:
            if hasattr(os, 'nice'):
                os.nice(-5)
        except:
            pass
            
        try:
            memory_settings = {
                '/proc/sys/vm/swappiness': '10',
                '/proc/sys/vm/vfs_cache_pressure': '50',
                '/proc/sys/vm/dirty_ratio': '15',
                '/proc/sys/vm/dirty_background_ratio': '5'
            }
            
            for path, value in memory_settings.items():
                try:
                    if os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(value)
                except PermissionError:
                    pass
                    
        except Exception:
            pass
    
    def _optimize_network_settings(self):
        try:
            network_settings = {
                '/proc/sys/net/core/rmem_max': '134217728',
                '/proc/sys/net/core/wmem_max': '134217728',
                '/proc/sys/net/ipv4/tcp_rmem': '4096 65536 134217728',
                '/proc/sys/net/ipv4/tcp_wmem': '4096 65536 134217728',
                '/proc/sys/net/ipv4/tcp_congestion_control': 'bbr'
            }
            
            for path, value in network_settings.items():
                try:
                    if os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(value)
                except PermissionError:
                    pass
                    
        except Exception:
            pass
    
    def _optimize_battery_usage(self):
        self.battery_optimizer = BatteryOptimizer()
        self.battery_optimizer.start_optimization()
    
    def _setup_background_persistence(self):
        self.background_processes = BackgroundPersistence()
        self.background_processes.setup_persistence()
    
    def optimize_process_priority(self, pid: int, priority: int = -10):
        try:
            if self.is_termux:
                process = psutil.Process(pid)
                current_nice = process.nice()
                new_nice = max(current_nice + priority, -20)
                process.nice(new_nice)
                return True
        except Exception:
            pass
        return False
    
    def setup_wakelock(self, tag: str = "runmero_wakelock"):
        if not self.is_termux:
            return False
            
        try:
            cmd = f'termux-wake-lock {tag}'
            subprocess.run(cmd, shell=True, capture_output=True)
            return True
        except Exception:
            pass
        return False
    
    def release_wakelock(self):
        if not self.is_termux:
            return False
            
        try:
            cmd = 'termux-wake-unlock'
            subprocess.run(cmd, shell=True, capture_output=True)
            return True
        except Exception:
            pass
        return False
    
    def prevent_android_killing(self):
        if not self.is_termux:
            return False
            
        strategies = []
        
        try:
            self.setup_wakelock()
            strategies.append("WakeLock")
        except:
            pass
            
        try:
            self._setup_foreground_service()
            strategies.append("Foreground Service")
        except:
            pass
            
        try:
            self._disable_doze_mode()
            strategies.append("Doze Mode Bypass")
        except:
            pass
            
        try:
            self._setup_persistent_notification()
            strategies.append("Persistent Notification")
        except:
            pass
        
        return strategies
    
    def _setup_foreground_service(self):
        service_code = '''
        am startforeground-service -n com.termux/.app.RunMeroService
        '''
        try:
            subprocess.run(service_code, shell=True, capture_output=True)
        except:
            pass
    
    def _disable_doze_mode(self):
        try:
            cmd = 'dumpsys deviceidle disable'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    def _setup_persistent_notification(self):
        try:
            notification_data = {
                "title": "RunMero Active",
                "content": "خدمة RunMero تعمل في الخلفية",
                "id": "runmero_persistent",
                "priority": "high",
                "ongoing": True
            }
            
            cmd = f'termux-notification --title "{notification_data["title"]}" --content "{notification_data["content"]}" --id {notification_data["id"]} --priority {notification_data["priority"]} --ongoing'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    def get_system_info(self) -> Dict[str, Any]:
        info = {
            "is_termux": self.is_termux,
            "platform": sys.platform,
            "python_version": sys.version,
            "optimizations_applied": self.optimizations
        }
        
        if self.is_termux:
            try:
                info["termux_version"] = os.getenv('TERMUX_VERSION', 'unknown')
                info["prefix"] = os.getenv('PREFIX', 'unknown')
                info["android_version"] = self._get_android_version()
                info["device_model"] = self._get_device_model()
                info["battery_info"] = self._get_battery_info()
            except:
                pass
                
        return info
    
    def _get_android_version(self) -> str:
        try:
            result = subprocess.run('getprop ro.build.version.release', shell=True, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_device_model(self) -> str:
        try:
            result = subprocess.run('getprop ro.product.model', shell=True, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_battery_info(self) -> Dict[str, Any]:
        try:
            result = subprocess.run('termux-battery-status', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return {}
    
    def monitor_system_resources(self, interval: int = 30):
        self.system_monitor = SystemResourceMonitor(interval)
        self.system_monitor.start()
        return self.system_monitor
    
    def apply_termux_specific_optimizations(self):
        if not self.is_termux:
            return []
            
        optimizations = []
        
        env_optimizations = {
            'TMPDIR': '/data/data/com.termux/files/usr/tmp',
            'LD_LIBRARY_PATH': '/data/data/com.termux/files/usr/lib',
            'PATH': '/data/data/com.termux/files/usr/bin:' + os.getenv('PATH', ''),
            'PYTHONUNBUFFERED': '1',
            'PYTHONIOENCODING': 'utf-8'
        }
        
        for key, value in env_optimizations.items():
            os.environ[key] = value
            optimizations.append(f"Environment: {key}")
        
        try:
            import threading
            threading.stack_size(2 * 1024 * 1024)
            optimizations.append("Thread Stack Size")
        except:
            pass
        
        try:
            import gc
            gc.set_threshold(700, 10, 10)
            optimizations.append("GC Threshold")
        except:
            pass
        
        return optimizations

class BatteryOptimizer:
    def __init__(self):
        self.optimization_active = False
        self.monitor_thread = None
        
    def start_optimization(self):
        if self.optimization_active:
            return
            
        self.optimization_active = True
        self.monitor_thread = threading.Thread(target=self._battery_monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop_optimization(self):
        self.optimization_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _battery_monitor(self):
        while self.optimization_active:
            try:
                battery_info = self._get_battery_status()
                if battery_info:
                    self._apply_battery_optimizations(battery_info)
            except:
                pass
            time.sleep(60)
    
    def _get_battery_status(self) -> Optional[Dict]:
        try:
            result = subprocess.run('termux-battery-status', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
    
    def _apply_battery_optimizations(self, battery_info: Dict):
        percentage = battery_info.get('percentage', 100)
        
        if percentage < 20:
            self._enable_power_save_mode()
        elif percentage > 80:
            self._enable_performance_mode()
        else:
            self._enable_balanced_mode()
    
    def _enable_power_save_mode(self):
        try:
            for cpu in range(psutil.cpu_count()):
                cpu_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                if os.path.exists(cpu_path):
                    try:
                        with open(cpu_path, 'w') as f:
                            f.write('powersave')
                    except:
                        pass
        except:
            pass
    
    def _enable_performance_mode(self):
        try:
            for cpu in range(psutil.cpu_count()):
                cpu_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                if os.path.exists(cpu_path):
                    try:
                        with open(cpu_path, 'w') as f:
                            f.write('performance')
                    except:
                        pass
        except:
            pass
    
    def _enable_balanced_mode(self):
        try:
            for cpu in range(psutil.cpu_count()):
                cpu_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                if os.path.exists(cpu_path):
                    try:
                        with open(cpu_path, 'w') as f:
                            f.write('ondemand')
                    except:
                        pass
        except:
            pass

class BackgroundPersistence:
    def __init__(self):
        self.persistence_active = False
        self.keepalive_thread = None
        
    def setup_persistence(self):
        if self.persistence_active:
            return
            
        self.persistence_active = True
        self._setup_signal_handlers()
        self._start_keepalive()
        self._create_pid_file()
    
    def _setup_signal_handlers(self):
        def signal_handler(signum, frame):
            pass
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def _start_keepalive(self):
        self.keepalive_thread = threading.Thread(target=self._keepalive_loop, daemon=True)
        self.keepalive_thread.start()
    
    def _keepalive_loop(self):
        while self.persistence_active:
            try:
                self._send_keepalive_signal()
                time.sleep(30)
            except:
                pass
    
    def _send_keepalive_signal(self):
        try:
            pid = os.getpid()
            os.kill(pid, 0)
        except:
            pass
    
    def _create_pid_file(self):
        try:
            pid_file = '/tmp/runmero_background.pid'
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except:
            pass
    
    def cleanup(self):
        self.persistence_active = False
        if self.keepalive_thread:
            self.keepalive_thread.join(timeout=5)

class SystemResourceMonitor:
    def __init__(self, interval: int = 30):
        self.interval = interval
        self.monitoring = False
        self.monitor_thread = None
        self.resource_data = []
        
    def start(self):
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def _monitoring_loop(self):
        while self.monitoring:
            try:
                resource_info = self._collect_resource_data()
                self.resource_data.append(resource_info)
                
                if len(self.resource_data) > 100:
                    self.resource_data = self.resource_data[-50:]
                
                self._apply_resource_optimizations(resource_info)
                
            except:
                pass
            
            time.sleep(self.interval)
    
    def _collect_resource_data(self) -> Dict[str, Any]:
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'network': psutil.net_io_counters()._asdict(),
            'process_count': len(psutil.pids()),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def _apply_resource_optimizations(self, resource_info: Dict[str, Any]):
        memory_percent = resource_info['memory']['percent']
        cpu_percent = resource_info['cpu_percent']
        
        if memory_percent > 85:
            self._trigger_memory_cleanup()
        
        if cpu_percent > 90:
            self._reduce_cpu_usage()
    
    def _trigger_memory_cleanup(self):
        try:
            import gc
            gc.collect()
        except:
            pass
    
    def _reduce_cpu_usage(self):
        try:
            current_process = psutil.Process()
            current_nice = current_process.nice()
            if current_nice < 10:
                current_process.nice(current_nice + 1)
        except:
            pass
    
    def get_resource_history(self) -> List[Dict[str, Any]]:
        return self.resource_data.copy()
