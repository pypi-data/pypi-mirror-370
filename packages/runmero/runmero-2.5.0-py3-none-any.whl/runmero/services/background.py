# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة جنين الصامدة فلسطين

import os
import time
import threading
import subprocess
import signal
import json
import multiprocessing
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
from queue import Queue, Empty
import logging

class ServiceStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    CRASHED = "crashed"
    UNKNOWN = "unknown"

@dataclass
class ServiceConfig:
    name: str
    description: str
    command: Union[str, List[str]]
    working_directory: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    user: Optional[str] = None
    group: Optional[str] = None
    auto_restart: bool = True
    max_restarts: int = 3
    restart_delay: float = 5.0
    timeout: float = 30.0
    stdout_file: Optional[str] = None
    stderr_file: Optional[str] = None
    pid_file: Optional[str] = None
    depends_on: Optional[List[str]] = None
    priority: int = 0
    resource_limits: Optional[Dict[str, Any]] = None

class ServiceInstance:
    def __init__(self, config: ServiceConfig, service_manager):
        self.config = config
        self.service_manager = service_manager
        self.status = ServiceStatus.STOPPED
        self.process = None
        self.pid = None
        self.start_time = None
        self.stop_time = None
        self.restart_count = 0
        self.last_restart_time = None
        self.status_lock = threading.Lock()
        self.monitor_thread = None
        self.log_queue = Queue()
        self.metrics = {
            'starts': 0,
            'stops': 0,
            'crashes': 0,
            'total_uptime': 0.0,
            'last_exit_code': None
        }
        
        self.logger = logging.getLogger(f'runmero.service.{self.config.name}')
        self._setup_logging()
    
    def _setup_logging(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[%(asctime)s] [SERVICE:{self.config.name}] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def start(self) -> bool:
        with self.status_lock:
            if self.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]:
                return False
            
            self.status = ServiceStatus.STARTING
            self.logger.info(f"بدء تشغيل الخدمة: {self.config.name}")
        
        try:
            if isinstance(self.config.command, str):
                cmd = self.config.command.split()
            else:
                cmd = self.config.command
            
            env = os.environ.copy()
            if self.config.environment:
                env.update(self.config.environment)
            
            stdout_file = None
            stderr_file = None
            
            if self.config.stdout_file:
                stdout_file = open(self.config.stdout_file, 'a')
            if self.config.stderr_file:
                stderr_file = open(self.config.stderr_file, 'a')
            
            self.process = subprocess.Popen(
                cmd,
                cwd=self.config.working_directory,
                env=env,
                stdout=stdout_file or subprocess.PIPE,
                stderr=stderr_file or subprocess.PIPE,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            self.pid = self.process.pid
            self.start_time = time.time()
            
            if self.config.pid_file:
                with open(self.config.pid_file, 'w') as f:
                    f.write(str(self.pid))
            
            time.sleep(1)
            
            if self.process.poll() is None:
                with self.status_lock:
                    self.status = ServiceStatus.RUNNING
                self.metrics['starts'] += 1
                self.logger.info(f"تم تشغيل الخدمة بنجاح - PID: {self.pid}")
                
                self._start_monitoring()
                return True
            else:
                with self.status_lock:
                    self.status = ServiceStatus.FAILED
                self.logger.error(f"فشل في تشغيل الخدمة - Exit code: {self.process.returncode}")
                return False
                
        except Exception as e:
            with self.status_lock:
                self.status = ServiceStatus.FAILED
            self.logger.error(f"خطأ في تشغيل الخدمة: {e}")
            return False
    
    def stop(self, timeout: Optional[float] = None) -> bool:
        timeout = timeout or self.config.timeout
        
        with self.status_lock:
            if self.status in [ServiceStatus.STOPPED, ServiceStatus.STOPPING]:
                return True
            
            self.status = ServiceStatus.STOPPING
            self.logger.info(f"بدء إيقاف الخدمة: {self.config.name}")
        
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                
                try:
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self.logger.warning("انتهت مهلة الإيقاف الآمن، الانتقال للإيقاف القسري")
                    self.process.kill()
                    self.process.wait(timeout=5)
                
                self.metrics['last_exit_code'] = self.process.returncode
            
            self.stop_time = time.time()
            if self.start_time:
                self.metrics['total_uptime'] += self.stop_time - self.start_time
            
            with self.status_lock:
                self.status = ServiceStatus.STOPPED
            
            self.metrics['stops'] += 1
            self._stop_monitoring()
            
            if self.config.pid_file and os.path.exists(self.config.pid_file):
                os.remove(self.config.pid_file)
            
            self.logger.info("تم إيقاف الخدمة بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إيقاف الخدمة: {e}")
            with self.status_lock:
                self.status = ServiceStatus.FAILED
            return False
    
    def restart(self) -> bool:
        self.logger.info(f"إعادة تشغيل الخدمة: {self.config.name}")
        
        if not self.stop():
            return False
        
        time.sleep(self.config.restart_delay)
        
        if self.restart_count >= self.config.max_restarts:
            self.logger.error(f"تم الوصول للحد الأقصى من إعادات التشغيل: {self.config.max_restarts}")
            return False
        
        self.restart_count += 1
        self.last_restart_time = time.time()
        
        return self.start()
    
    def _start_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.monitor_thread = threading.Thread(target=self._monitor_process, daemon=True)
        self.monitor_thread.start()
    
    def _stop_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def _monitor_process(self):
        while self.status == ServiceStatus.RUNNING and self.process:
            try:
                exit_code = self.process.poll()
                
                if exit_code is not None:
                    self.logger.warning(f"العملية توقفت بشكل غير متوقع - Exit code: {exit_code}")
                    
                    with self.status_lock:
                        if exit_code == 0:
                            self.status = ServiceStatus.STOPPED
                        else:
                            self.status = ServiceStatus.CRASHED
                            self.metrics['crashes'] += 1
                    
                    if self.config.auto_restart and self.restart_count < self.config.max_restarts:
                        self.logger.info("محاولة إعادة التشغيل التلقائي...")
                        time.sleep(self.config.restart_delay)
                        self.restart()
                    
                    break
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"خطأ في مراقبة العملية: {e}")
                break
    
    def get_status_info(self) -> Dict[str, Any]:
        info = {
            'name': self.config.name,
            'status': self.status.value,
            'pid': self.pid,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'restart_count': self.restart_count,
            'last_restart_time': self.last_restart_time,
            'metrics': self.metrics.copy()
        }
        
        if self.status == ServiceStatus.RUNNING and self.pid:
            try:
                process = psutil.Process(self.pid)
                info.update({
                    'cpu_percent': process.cpu_percent(),
                    'memory_info': process.memory_info()._asdict(),
                    'num_threads': process.num_threads(),
                    'connections': len(process.connections()) if hasattr(process, 'connections') else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return info
    
    def send_signal(self, sig: int) -> bool:
        if not self.pid:
            return False
        
        try:
            os.kill(self.pid, sig)
            self.logger.info(f"تم إرسال الإشارة {sig} للعملية {self.pid}")
            return True
        except (OSError, ProcessLookupError):
            self.logger.error(f"فشل في إرسال الإشارة {sig} للعملية {self.pid}")
            return False

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.registry_file = '/tmp/runmero_services.json'
        self.lock = threading.Lock()
        
        self._load_registry()
    
    def register_service(self, config: ServiceConfig):
        with self.lock:
            self.services[config.name] = config
            
            if config.depends_on:
                self.dependencies[config.name] = config.depends_on.copy()
            
            self._save_registry()
    
    def unregister_service(self, service_name: str):
        with self.lock:
            if service_name in self.services:
                del self.services[service_name]
            
            if service_name in self.dependencies:
                del self.dependencies[service_name]
            
            for deps in self.dependencies.values():
                if service_name in deps:
                    deps.remove(service_name)
            
            self._save_registry()
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        return self.services.get(service_name)
    
    def list_services(self) -> List[str]:
        return list(self.services.keys())
    
    def get_service_dependencies(self, service_name: str) -> List[str]:
        return self.dependencies.get(service_name, [])
    
    def resolve_start_order(self, service_names: List[str]) -> List[str]:
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_name: str):
            if service_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {service_name}")
            
            if service_name in visited:
                return
            
            temp_visited.add(service_name)
            
            for dependency in self.get_service_dependencies(service_name):
                if dependency in service_names:
                    visit(dependency)
            
            temp_visited.remove(service_name)
            visited.add(service_name)
            result.append(service_name)
        
        for service_name in service_names:
            visit(service_name)
        
        return result
    
    def _save_registry(self):
        try:
            registry_data = {
                'services': {name: asdict(config) for name, config in self.services.items()},
                'dependencies': self.dependencies,
                'saved_at': time.time()
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
                
        except Exception as e:
            print(f"خطأ في حفظ سجل الخدمات: {e}")
    
    def _load_registry(self):
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r') as f:
                    registry_data = json.load(f)
                
                for name, config_dict in registry_data.get('services', {}).items():
                    config = ServiceConfig(**config_dict)
                    self.services[name] = config
                
                self.dependencies = registry_data.get('dependencies', {})
                
        except Exception as e:
            print(f"خطأ في تحميل سجل الخدمات: {e}")

class BackgroundServiceManager:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.running_services: Dict[str, ServiceInstance] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.monitor_thread = None
        
        self.logger = logging.getLogger('runmero.service_manager')
        self._setup_logging()
        
        self._setup_signal_handlers()
        self._start_global_monitoring()
    
    def _setup_logging(self):
        handler = logging.FileHandler('/tmp/runmero_service_manager.log')
        formatter = logging.Formatter(
            '[%(asctime)s] [SERVICE_MANAGER] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _setup_signal_handlers(self):
        def signal_handler(signum, frame):
            self.logger.info(f"تم استلام إشارة الإيقاف: {signum}")
            self.shutdown_all()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def register_service(self, config: ServiceConfig) -> bool:
        try:
            self.registry.register_service(config)
            self.logger.info(f"تم تسجيل الخدمة: {config.name}")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الخدمة {config.name}: {e}")
            return False
    
    def start_service(self, service_name: str) -> bool:
        with self.lock:
            if service_name in self.running_services:
                if self.running_services[service_name].status == ServiceStatus.RUNNING:
                    return True
            
            config = self.registry.get_service_config(service_name)
            if not config:
                self.logger.error(f"الخدمة غير مسجلة: {service_name}")
                return False
            
            dependencies = self.registry.get_service_dependencies(service_name)
            for dep in dependencies:
                if not self.is_service_running(dep):
                    if not self.start_service(dep):
                        self.logger.error(f"فشل في تشغيل التبعية: {dep}")
                        return False
            
            service_instance = ServiceInstance(config, self)
            self.running_services[service_name] = service_instance
            
            success = service_instance.start()
            if not success:
                del self.running_services[service_name]
            
            return success
    
    def stop_service(self, service_name: str, timeout: Optional[float] = None) -> bool:
        with self.lock:
            if service_name not in self.running_services:
                return True
            
            service_instance = self.running_services[service_name]
            success = service_instance.stop(timeout)
            
            if success:
                del self.running_services[service_name]
            
            return success
    
    def restart_service(self, service_name: str) -> bool:
        with self.lock:
            if service_name not in self.running_services:
                return self.start_service(service_name)
            
            return self.running_services[service_name].restart()
    
    def is_service_running(self, service_name: str) -> bool:
        if service_name not in self.running_services:
            return False
        
        return self.running_services[service_name].status == ServiceStatus.RUNNING
    
    def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        if service_name not in self.running_services:
            config = self.registry.get_service_config(service_name)
            if config:
                return {
                    'name': service_name,
                    'status': ServiceStatus.STOPPED.value,
                    'registered': True
                }
            return None
        
        return self.running_services[service_name].get_status_info()
    
    def list_services(self) -> List[Dict[str, Any]]:
        services_info = []
        
        all_services = set(self.registry.list_services()) | set(self.running_services.keys())
        
        for service_name in all_services:
            status_info = self.get_service_status(service_name)
            if status_info:
                services_info.append(status_info)
        
        return services_info
    
    def start_services_batch(self, service_names: List[str]) -> Dict[str, bool]:
        try:
            ordered_services = self.registry.resolve_start_order(service_names)
            results = {}
            
            for service_name in ordered_services:
                success = self.start_service(service_name)
                results[service_name] = success
                
                if not success:
                    self.logger.error(f"فشل في تشغيل الخدمة {service_name}, إيقاف المجموعة")
                    
                    for running_service in reversed(ordered_services[:ordered_services.index(service_name)]):
                        self.stop_service(running_service)
                    
                    break
            
            return results
            
        except ValueError as e:
            self.logger.error(f"خطأ في ترتيب الخدمات: {e}")
            return {service: False for service in service_names}
    
    def stop_services_batch(self, service_names: List[str]) -> Dict[str, bool]:
        results = {}
        
        for service_name in reversed(service_names):
            results[service_name] = self.stop_service(service_name)
        
        return results
    
    def send_signal_to_service(self, service_name: str, signal_num: int) -> bool:
        if service_name not in self.running_services:
            return False
        
        return self.running_services[service_name].send_signal(signal_num)
    
    def get_system_stats(self) -> Dict[str, Any]:
        running_count = sum(1 for s in self.running_services.values() if s.status == ServiceStatus.RUNNING)
        
        stats = {
            'total_services': len(self.registry.list_services()),
            'running_services': running_count,
            'stopped_services': len(self.running_services) - running_count,
            'system_load': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            'memory_usage': psutil.virtual_memory()._asdict(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'uptime': time.time()
        }
        
        return stats
    
    def _start_global_monitoring(self):
        self.monitor_thread = threading.Thread(target=self._global_monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _global_monitor_loop(self):
        while not self.shutdown_event.is_set():
            try:
                self._check_service_health()
                time.sleep(30)
            except Exception as e:
                self.logger.error(f"خطأ في المراقبة العامة: {e}")
                time.sleep(10)
    
    def _check_service_health(self):
        for service_name, service_instance in list(self.running_services.items()):
            if service_instance.status == ServiceStatus.RUNNING:
                if not service_instance.process or service_instance.process.poll() is not None:
                    self.logger.warning(f"اكتشف توقف غير متوقع للخدمة: {service_name}")
    
    def shutdown_all(self):
        self.logger.info("بدء إيقاف جميع الخدمات...")
        
        self.shutdown_event.set()
        
        running_services = list(self.running_services.keys())
        
        for service_name in reversed(running_services):
            self.stop_service(service_name, timeout=10)
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True, timeout=10)
        
        self.logger.info("تم إيقاف جميع الخدمات بنجاح")
    
    def create_service_from_dict(self, service_dict: Dict[str, Any]) -> ServiceConfig:
        return ServiceConfig(
            name=service_dict['name'],
            description=service_dict.get('description', ''),
            command=service_dict['command'],
            working_directory=service_dict.get('working_directory'),
            environment=service_dict.get('environment'),
            user=service_dict.get('user'),
            group=service_dict.get('group'),
            auto_restart=service_dict.get('auto_restart', True),
            max_restarts=service_dict.get('max_restarts', 3),
            restart_delay=service_dict.get('restart_delay', 5.0),
            timeout=service_dict.get('timeout', 30.0),
            stdout_file=service_dict.get('stdout_file'),
            stderr_file=service_dict.get('stderr_file'),
            pid_file=service_dict.get('pid_file'),
            depends_on=service_dict.get('depends_on'),
            priority=service_dict.get('priority', 0),
            resource_limits=service_dict.get('resource_limits')
        )
    
    def export_services_config(self, filepath: str):
        config_data = {
            'services': {},
            'export_time': time.time(),
            'version': '2.5.0'
        }
        
        for service_name in self.registry.list_services():
            config = self.registry.get_service_config(service_name)
            if config:
                config_data['services'][service_name] = asdict(config)
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"تم تصدير تكوين الخدمات إلى: {filepath}")
    
    def import_services_config(self, filepath: str):
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
            
            for service_name, service_config in config_data.get('services', {}).items():
                config = ServiceConfig(**service_config)
                self.register_service(config)
            
            self.logger.info(f"تم استيراد تكوين الخدمات من: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في استيراد التكوين: {e}")
            return False

