# حقوق الطبع والنشر محفوظة © 2025 mero - من أرض فلسطين الطاهرة

import os
import time
import threading
from typing import Callable, Any, Optional, Dict
import multiprocessing

class BackgroundProcess:
    def __init__(self, 
                 process_id: str, 
                 target: Optional[Callable] = None,
                 args: tuple = (),
                 kwargs: dict = None,
                 daemon: bool = True,
                 max_restarts: int = 3,
                 restart_delay: int = 5):
        
        self.process_id = process_id
        self.target = target
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.daemon = daemon
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        
        self._pid: Optional[int] = None
        self._status: str = 'created'
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._restart_count: int = 0
        self._lock = threading.Lock()
        
        self._metadata: Dict[str, Any] = {
            'created_at': time.time(),
            'created_by': os.getenv('USER', 'unknown'),
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'platform': os.name
        }

    @property
    def pid(self) -> Optional[int]:
        return self._pid

    @property 
    def status(self) -> str:
        return self._status

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    @property
    def end_time(self) -> Optional[float]:
        return self._end_time

    @property
    def running_time(self) -> Optional[float]:
        if self._start_time is None:
            return None
        
        end_time = self._end_time or time.time()
        return end_time - self._start_time

    @property
    def restart_count(self) -> int:
        return self._restart_count

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any):
        with self._lock:
            self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def is_alive(self) -> bool:
        if self._pid is None:
            return False
        
        try:
            import psutil
            return psutil.pid_exists(self._pid)
        except ImportError:
            try:
                os.kill(self._pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False

    def get_process_info(self) -> Optional[Dict[str, Any]]:
        if not self.is_alive() or self._pid is None:
            return None
        
        try:
            import psutil
            process = psutil.Process(self._pid)
            return {
                'pid': self._pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_info': process.memory_info()._asdict(),
                'create_time': process.create_time(),
                'num_threads': process.num_threads(),
                'connections': len(process.connections()) if hasattr(process, 'connections') else 0,
                'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
            }
        except Exception:
            return {'pid': self._pid, 'status': 'unknown'}

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        if not self.is_alive():
            return True
        
        start_time = time.time()
        while self.is_alive():
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return True

    def send_signal(self, signal_num: int) -> bool:
        if self._pid is None or not self.is_alive():
            return False
        
        try:
            os.kill(self._pid, signal_num)
            return True
        except (OSError, ProcessLookupError):
            return False

    def terminate(self) -> bool:
        import signal
        return self.send_signal(signal.SIGTERM)

    def kill(self) -> bool:
        import signal  
        return self.send_signal(signal.SIGKILL)

    def pause(self) -> bool:
        import signal
        return self.send_signal(signal.SIGSTOP)

    def resume(self) -> bool:
        import signal
        return self.send_signal(signal.SIGCONT)

    def get_children(self) -> list:
        if not self.is_alive() or self._pid is None:
            return []
        
        try:
            import psutil
            process = psutil.Process(self._pid)
            return [child.pid for child in process.children(recursive=True)]
        except Exception:
            return []

    def kill_children(self) -> int:
        children = self.get_children()
        killed_count = 0
        
        import signal
        for child_pid in children:
            try:
                os.kill(child_pid, signal.SIGKILL)
                killed_count += 1
            except (OSError, ProcessLookupError):
                pass
        
        return killed_count

    def get_logs(self, lines: int = 100) -> list:
        log_file = f"/tmp/runmero_{self.process_id}.log"
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                return f.readlines()[-lines:]
        except Exception:
            return []

    def clear_logs(self) -> bool:
        log_file = f"/tmp/runmero_{self.process_id}.log"
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            return True
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'process_id': self.process_id,
            'pid': self._pid,
            'status': self._status,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'running_time': self.running_time,
            'restart_count': self._restart_count,
            'max_restarts': self.max_restarts,
            'restart_delay': self.restart_delay,
            'daemon': self.daemon,
            'metadata': self._metadata,
            'is_alive': self.is_alive()
        }

    def __repr__(self) -> str:
        return f"BackgroundProcess(id='{self.process_id}', pid={self._pid}, status='{self._status}')"

    def __str__(self) -> str:
        return f"Process {self.process_id} (PID: {self._pid}, Status: {self._status})"
