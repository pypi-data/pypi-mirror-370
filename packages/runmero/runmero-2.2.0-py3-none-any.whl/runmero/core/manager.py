# حقوق الطبع والنشر محفوظة © 2025 mero - من قلب فلسطين الحبيبة

import os
import sys
import json
import time
import signal
import threading
import multiprocessing
from typing import Dict, List, Optional, Any, Callable
import psutil
from .process import BackgroundProcess
from .signal_handler import SignalHandler
from ..termux.persistence import PersistenceManager
from ..utils.console import Console

class ProcessManager:
    def __init__(self):
        self.processes: Dict[str, BackgroundProcess] = {}
        self.active_processes: Dict[str, multiprocessing.Process] = {}
        self.signal_handler = SignalHandler()
        self.persistence = PersistenceManager()
        self.console = Console()
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None
        self._setup_signal_handlers()
        self._load_persistent_processes()

    def _setup_signal_handlers(self):
        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT]:
            signal.signal(sig, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self.console.info(f"تم استلام إشارة الإيقاف: {signum}")
        self.stop_all_processes()
        sys.exit(0)

    def _load_persistent_processes(self):
        persistent_data = self.persistence.load_processes()
        for process_id, process_data in persistent_data.items():
            try:
                if psutil.pid_exists(process_data['pid']):
                    process = BackgroundProcess(
                        process_id=process_id,
                        target=None,
                        args=process_data.get('args', []),
                        kwargs=process_data.get('kwargs', {})
                    )
                    process._pid = process_data['pid']
                    process._status = 'running'
                    self.processes[process_id] = process
                    self.console.success(f"تم استعادة العملية: {process_id}")
                else:
                    self.persistence.remove_process(process_id)
            except Exception as e:
                self.console.error(f"خطأ في استعادة العملية {process_id}: {e}")

    def create_process(self, 
                      process_id: str, 
                      target: Callable,
                      args: tuple = (),
                      kwargs: dict = None,
                      daemon: bool = True,
                      persistent: bool = True) -> BackgroundProcess:
        
        if kwargs is None:
            kwargs = {}
            
        with self._lock:
            if process_id in self.processes:
                raise ValueError(f"العملية {process_id} موجودة بالفعل")
            
            process = BackgroundProcess(
                process_id=process_id,
                target=target,
                args=args,
                kwargs=kwargs,
                daemon=daemon
            )
            
            self.processes[process_id] = process
            
            if persistent:
                self.persistence.save_process(process_id, {
                    'target': target.__name__ if target else None,
                    'args': args,
                    'kwargs': kwargs,
                    'daemon': daemon,
                    'created_at': time.time()
                })
            
            self.console.success(f"تم إنشاء العملية: {process_id}")
            return process

    def start_process(self, process_id: str) -> bool:
        with self._lock:
            if process_id not in self.processes:
                self.console.error(f"العملية {process_id} غير موجودة")
                return False
            
            process = self.processes[process_id]
            
            try:
                mp_process = multiprocessing.Process(
                    target=process.target,
                    args=process.args,
                    kwargs=process.kwargs,
                    daemon=process.daemon
                )
                mp_process.start()
                
                self.active_processes[process_id] = mp_process
                process._pid = mp_process.pid
                process._status = 'running'
                process._start_time = time.time()
                
                self.persistence.update_process(process_id, {
                    'pid': mp_process.pid,
                    'status': 'running',
                    'start_time': time.time()
                })
                
                self.console.success(f"تم تشغيل العملية: {process_id} (PID: {mp_process.pid})")
                
                if not self._monitoring:
                    self._start_monitoring()
                
                return True
                
            except Exception as e:
                self.console.error(f"خطأ في تشغيل العملية {process_id}: {e}")
                process._status = 'failed'
                return False

    def stop_process(self, process_id: str, timeout: int = 10) -> bool:
        with self._lock:
            if process_id not in self.processes:
                self.console.error(f"العملية {process_id} غير موجودة")
                return False
            
            process = self.processes[process_id]
            
            if process_id in self.active_processes:
                mp_process = self.active_processes[process_id]
                
                try:
                    mp_process.terminate()
                    mp_process.join(timeout=timeout)
                    
                    if mp_process.is_alive():
                        mp_process.kill()
                        mp_process.join()
                    
                    del self.active_processes[process_id]
                    process._status = 'stopped'
                    process._end_time = time.time()
                    
                    self.persistence.update_process(process_id, {
                        'status': 'stopped',
                        'end_time': time.time()
                    })
                    
                    self.console.success(f"تم إيقاف العملية: {process_id}")
                    return True
                    
                except Exception as e:
                    self.console.error(f"خطأ في إيقاف العملية {process_id}: {e}")
                    return False
            else:
                self.console.warning(f"العملية {process_id} غير نشطة")
                return True

    def restart_process(self, process_id: str) -> bool:
        self.console.info(f"إعادة تشغيل العملية: {process_id}")
        self.stop_process(process_id)
        time.sleep(2)
        return self.start_process(process_id)

    def get_process_status(self, process_id: str) -> Optional[Dict[str, Any]]:
        if process_id not in self.processes:
            return None
        
        process = self.processes[process_id]
        status = {
            'id': process_id,
            'status': process._status,
            'pid': process._pid,
            'start_time': process._start_time,
            'end_time': process._end_time,
            'running_time': None
        }
        
        if process._start_time and process._status == 'running':
            status['running_time'] = time.time() - process._start_time
        
        if process._pid and psutil.pid_exists(process._pid):
            try:
                ps_process = psutil.Process(process._pid)
                status['cpu_percent'] = ps_process.cpu_percent()
                status['memory_info'] = ps_process.memory_info()._asdict()
                status['num_threads'] = ps_process.num_threads()
            except psutil.NoSuchProcess:
                status['status'] = 'dead'
        
        return status

    def list_processes(self) -> List[Dict[str, Any]]:
        processes_info = []
        for process_id in self.processes:
            process_info = self.get_process_status(process_id)
            if process_info:
                processes_info.append(process_info)
        return processes_info

    def stop_all_processes(self):
        self.console.info("إيقاف جميع العمليات...")
        process_ids = list(self.processes.keys())
        for process_id in process_ids:
            self.stop_process(process_id)
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitoring = False
            self._monitor_thread.join(timeout=5)

    def _start_monitoring(self):
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self._monitor_thread.start()
        self.console.info("بدء مراقبة العمليات")

    def _monitor_processes(self):
        while self._monitoring:
            try:
                dead_processes = []
                
                for process_id, mp_process in list(self.active_processes.items()):
                    if not mp_process.is_alive():
                        dead_processes.append(process_id)
                
                for process_id in dead_processes:
                    self.console.warning(f"العملية {process_id} توقفت بشكل غير متوقع")
                    if process_id in self.active_processes:
                        del self.active_processes[process_id]
                    
                    if process_id in self.processes:
                        self.processes[process_id]._status = 'dead'
                        self.processes[process_id]._end_time = time.time()
                        
                        self.persistence.update_process(process_id, {
                            'status': 'dead',
                            'end_time': time.time()
                        })
                
                time.sleep(5)
                
            except Exception as e:
                self.console.error(f"خطأ في مراقبة العمليات: {e}")
                time.sleep(10)

    def cleanup_dead_processes(self):
        dead_process_ids = []
        for process_id, process in self.processes.items():
            if process._status in ['dead', 'failed', 'stopped']:
                dead_process_ids.append(process_id)
        
        for process_id in dead_process_ids:
            del self.processes[process_id]
            self.persistence.remove_process(process_id)
            self.console.info(f"تم تنظيف العملية: {process_id}")

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict(),
            'active_processes': len(self.active_processes),
            'total_processes': len(self.processes),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }

    def export_processes(self, filepath: str):
        data = {
            'processes': {},
            'export_time': time.time(),
            'version': '2.5.0'
        }
        
        for process_id, process in self.processes.items():
            data['processes'][process_id] = {
                'status': process._status,
                'pid': process._pid,
                'start_time': process._start_time,
                'end_time': process._end_time,
                'args': process.args,
                'kwargs': process.kwargs
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.console.success(f"تم تصدير العمليات إلى: {filepath}")
