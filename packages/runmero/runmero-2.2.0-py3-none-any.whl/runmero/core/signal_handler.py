# حقوق الطبع والنشر محفوظة © 2025 mero - من قلب القدس الشريفة

import signal
import threading
import time
from typing import Dict, Callable, Any, List
from collections import defaultdict

class SignalHandler:
    def __init__(self):
        self._handlers: Dict[int, List[Callable]] = defaultdict(list)
        self._original_handlers: Dict[int, Any] = {}
        self._lock = threading.Lock()
        self._shutdown_callbacks: List[Callable] = []
        self._graceful_shutdown = False
        self._shutdown_timeout = 30
        
    def register_handler(self, signal_num: int, handler: Callable):
        with self._lock:
            if signal_num not in self._original_handlers:
                self._original_handlers[signal_num] = signal.signal(signal_num, self._signal_dispatcher)
            
            self._handlers[signal_num].append(handler)

    def unregister_handler(self, signal_num: int, handler: Callable):
        with self._lock:
            if signal_num in self._handlers and handler in self._handlers[signal_num]:
                self._handlers[signal_num].remove(handler)
                
                if not self._handlers[signal_num] and signal_num in self._original_handlers:
                    signal.signal(signal_num, self._original_handlers[signal_num])
                    del self._original_handlers[signal_num]

    def _signal_dispatcher(self, signal_num: int, frame):
        handlers = self._handlers.get(signal_num, [])
        
        for handler in handlers:
            try:
                if callable(handler):
                    handler(signal_num, frame)
            except Exception as e:
                print(f"خطأ في معالج الإشارة {signal_num}: {e}")

    def register_shutdown_callback(self, callback: Callable):
        with self._lock:
            self._shutdown_callbacks.append(callback)

    def unregister_shutdown_callback(self, callback: Callable):
        with self._lock:
            if callback in self._shutdown_callbacks:
                self._shutdown_callbacks.remove(callback)

    def setup_graceful_shutdown(self, timeout: int = 30):
        self._shutdown_timeout = timeout
        self._graceful_shutdown = True
        
        shutdown_signals = [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT]
        
        for sig in shutdown_signals:
            self.register_handler(sig, self._handle_graceful_shutdown)

    def _handle_graceful_shutdown(self, signal_num: int, frame):
        print(f"تم استلام إشارة الإغلاق الآمن: {signal_num}")
        
        shutdown_thread = threading.Thread(target=self._execute_shutdown, daemon=True)
        shutdown_thread.start()

    def _execute_shutdown(self):
        start_time = time.time()
        
        print("بدء عملية الإغلاق الآمن...")
        
        for i, callback in enumerate(self._shutdown_callbacks):
            try:
                print(f"تنفيذ callback رقم {i + 1}")
                callback()
                
                elapsed = time.time() - start_time
                if elapsed > self._shutdown_timeout:
                    print("انتهت مهلة الإغلاق الآمن")
                    break
                    
            except Exception as e:
                print(f"خطأ في تنفيذ shutdown callback: {e}")
        
        print("انتهاء عملية الإغلاق الآمن")
        import os
        os._exit(0)

    def block_signals(self, signals: List[int]):
        for sig in signals:
            signal.signal(sig, signal.SIG_IGN)

    def unblock_signals(self, signals: List[int]):
        for sig in signals:
            if sig in self._original_handlers:
                signal.signal(sig, self._original_handlers[sig])
            else:
                signal.signal(sig, signal.SIG_DFL)

    def send_signal_to_process(self, pid: int, signal_num: int) -> bool:
        try:
            import os
            os.kill(pid, signal_num)
            return True
        except (OSError, ProcessLookupError):
            return False

    def create_signal_mask(self, signals: List[int]) -> int:
        mask = 0
        for sig in signals:
            mask |= (1 << (sig - 1))
        return mask

    def wait_for_signal(self, signals: List[int], timeout: int = None) -> int:
        received_signal = None
        event = threading.Event()
        
        def signal_catcher(sig_num, frame):
            nonlocal received_signal
            received_signal = sig_num
            event.set()
        
        original_handlers = {}
        for sig in signals:
            original_handlers[sig] = signal.signal(sig, signal_catcher)
        
        try:
            if event.wait(timeout):
                return received_signal
            else:
                return None
        finally:
            for sig, handler in original_handlers.items():
                signal.signal(sig, handler)

    def is_signal_pending(self, signal_num: int) -> bool:
        try:
            import os
            if hasattr(signal, 'sigpending'):
                pending = signal.sigpending()
                return signal_num in pending
            return False
        except:
            return False

    def get_signal_name(self, signal_num: int) -> str:
        signal_names = {
            1: 'SIGHUP',
            2: 'SIGINT', 
            3: 'SIGQUIT',
            9: 'SIGKILL',
            15: 'SIGTERM',
            17: 'SIGCHLD',
            18: 'SIGCONT',
            19: 'SIGSTOP',
            20: 'SIGTSTP',
            21: 'SIGTTIN',
            22: 'SIGTTOU'
        }
        return signal_names.get(signal_num, f'SIGNAL_{signal_num}')

    def install_signal_handlers(self):
        common_signals = {
            signal.SIGTERM: self._handle_termination,
            signal.SIGINT: self._handle_interruption,
            signal.SIGUSR1: self._handle_user_signal_1,
            signal.SIGUSR2: self._handle_user_signal_2
        }
        
        for sig, handler in common_signals.items():
            self.register_handler(sig, handler)

    def _handle_termination(self, signal_num, frame):
        print("تم استلام إشارة SIGTERM - بدء الإنهاء")

    def _handle_interruption(self, signal_num, frame):
        print("تم استلام إشارة SIGINT - مقاطعة المستخدم")

    def _handle_user_signal_1(self, signal_num, frame):
        print("تم استلام إشارة SIGUSR1")

    def _handle_user_signal_2(self, signal_num, frame):
        print("تم استلام إشارة SIGUSR2")

    def cleanup(self):
        with self._lock:
            for sig, handler in self._original_handlers.items():
                try:
                    signal.signal(sig, handler)
                except ValueError:
                    pass
            
            self._handlers.clear()
            self._original_handlers.clear()
            self._shutdown_callbacks.clear()

    def __del__(self):
        self.cleanup()
