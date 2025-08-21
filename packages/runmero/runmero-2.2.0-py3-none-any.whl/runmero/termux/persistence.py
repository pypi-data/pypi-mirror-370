# حقوق الطبع والنشر محفوظة © 2025 mero - من أرض الكرم حبرون فلسطين

import os
import json
import time
import threading
import subprocess
import signal
import psutil
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path

class PersistenceManager:
    def __init__(self):
        self.data_dir = self._get_data_directory()
        self.db_path = os.path.join(self.data_dir, 'runmero_persistence.db')
        self.processes_file = os.path.join(self.data_dir, 'processes.json')
        self.config_file = os.path.join(self.data_dir, 'config.json')
        self.lock_file = os.path.join(self.data_dir, 'runmero.lock')
        
        self._ensure_data_directory()
        self._init_database()
        self._setup_signal_handlers()
        
        self.auto_save_thread = None
        self.auto_save_enabled = True
        self._start_auto_save()
        
    def _get_data_directory(self) -> str:
        if os.getenv('TERMUX_VERSION'):
            base_dir = '/data/data/com.termux/files/usr/var/lib/runmero'
        else:
            home_dir = os.path.expanduser('~')
            base_dir = os.path.join(home_dir, '.runmero')
        return base_dir
    
    def _ensure_data_directory(self):
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        subdirs = ['processes', 'logs', 'configs', 'backups', 'temp']
        for subdir in subdirs:
            Path(os.path.join(self.data_dir, subdir)).mkdir(exist_ok=True)
    
    def _init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processes (
                        id TEXT PRIMARY KEY,
                        pid INTEGER,
                        status TEXT,
                        start_time REAL,
                        end_time REAL,
                        command TEXT,
                        args TEXT,
                        kwargs TEXT,
                        metadata TEXT,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS process_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        process_id TEXT,
                        timestamp REAL,
                        level TEXT,
                        message TEXT,
                        FOREIGN KEY (process_id) REFERENCES processes(id)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        event_type TEXT,
                        event_data TEXT,
                        severity TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configurations (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        created_at REAL,
                        updated_at REAL
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"خطأ في تهيئة قاعدة البيانات: {e}")
    
    def _setup_signal_handlers(self):
        def save_on_signal(signum, frame):
            self.force_save_all()
        
        signal.signal(signal.SIGTERM, save_on_signal)
        signal.signal(signal.SIGINT, save_on_signal)
        
        if hasattr(signal, 'SIGUSR1'):
            signal.signal(signal.SIGUSR1, save_on_signal)
    
    def save_process(self, process_id: str, process_data: Dict[str, Any]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = time.time()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO processes 
                    (id, pid, status, start_time, end_time, command, args, kwargs, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    process_id,
                    process_data.get('pid'),
                    process_data.get('status', 'created'),
                    process_data.get('start_time'),
                    process_data.get('end_time'),
                    process_data.get('command'),
                    json.dumps(process_data.get('args', [])),
                    json.dumps(process_data.get('kwargs', {})),
                    json.dumps(process_data.get('metadata', {})),
                    process_data.get('created_at', now),
                    now
                ))
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في حفظ العملية {process_id}: {e}")
    
    def load_processes(self) -> Dict[str, Dict[str, Any]]:
        processes = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM processes')
                rows = cursor.fetchall()
                
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    process_data = dict(zip(columns, row))
                    
                    try:
                        process_data['args'] = json.loads(process_data['args'] or '[]')
                        process_data['kwargs'] = json.loads(process_data['kwargs'] or '{}')
                        process_data['metadata'] = json.loads(process_data['metadata'] or '{}')
                    except json.JSONDecodeError:
                        process_data['args'] = []
                        process_data['kwargs'] = {}
                        process_data['metadata'] = {}
                    
                    processes[process_data['id']] = process_data
                    
        except Exception as e:
            print(f"خطأ في تحميل العمليات: {e}")
        
        return processes
    
    def update_process(self, process_id: str, updates: Dict[str, Any]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['args', 'kwargs', 'metadata']:
                        value = json.dumps(value)
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                set_clauses.append("updated_at = ?")
                values.append(time.time())
                values.append(process_id)
                
                query = f"UPDATE processes SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في تحديث العملية {process_id}: {e}")
    
    def remove_process(self, process_id: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM process_logs WHERE process_id = ?', (process_id,))
                cursor.execute('DELETE FROM processes WHERE id = ?', (process_id,))
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في حذف العملية {process_id}: {e}")
    
    def log_process_event(self, process_id: str, level: str, message: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO process_logs (process_id, timestamp, level, message)
                    VALUES (?, ?, ?, ?)
                ''', (process_id, time.time(), level, message))
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في تسجيل حدث العملية: {e}")
    
    def get_process_logs(self, process_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        logs = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, level, message FROM process_logs 
                    WHERE process_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (process_id, limit))
                
                for row in cursor.fetchall():
                    logs.append({
                        'timestamp': row[0],
                        'level': row[1],
                        'message': row[2]
                    })
                    
        except Exception as e:
            print(f"خطأ في جلب سجلات العملية: {e}")
        
        return logs
    
    def log_system_event(self, event_type: str, event_data: Any, severity: str = 'info'):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO system_events (timestamp, event_type, event_data, severity)
                    VALUES (?, ?, ?, ?)
                ''', (time.time(), event_type, json.dumps(event_data), severity))
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في تسجيل حدث النظام: {e}")
    
    def get_system_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        events = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if event_type:
                    query = '''
                        SELECT timestamp, event_type, event_data, severity FROM system_events 
                        WHERE event_type = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    '''
                    cursor.execute(query, (event_type, limit))
                else:
                    query = '''
                        SELECT timestamp, event_type, event_data, severity FROM system_events 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    '''
                    cursor.execute(query, (limit,))
                
                for row in cursor.fetchall():
                    try:
                        event_data = json.loads(row[2])
                    except json.JSONDecodeError:
                        event_data = row[2]
                    
                    events.append({
                        'timestamp': row[0],
                        'event_type': row[1],
                        'event_data': event_data,
                        'severity': row[3]
                    })
                    
        except Exception as e:
            print(f"خطأ في جلب أحداث النظام: {e}")
        
        return events
    
    def save_configuration(self, key: str, value: Any):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = time.time()
                cursor.execute('''
                    INSERT OR REPLACE INTO configurations (key, value, created_at, updated_at)
                    VALUES (?, ?, COALESCE((SELECT created_at FROM configurations WHERE key = ?), ?), ?)
                ''', (key, json.dumps(value), key, now, now))
                
                conn.commit()
                
        except Exception as e:
            print(f"خطأ في حفظ التكوين {key}: {e}")
    
    def load_configuration(self, key: str, default: Any = None) -> Any:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT value FROM configurations WHERE key = ?', (key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                    
        except Exception as e:
            print(f"خطأ في تحميل التكوين {key}: {e}")
        
        return default
    
    def backup_data(self, backup_name: Optional[str] = None) -> str:
        if not backup_name:
            backup_name = f"backup_{int(time.time())}"
        
        backup_dir = os.path.join(self.data_dir, 'backups', backup_name)
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            backup_db = os.path.join(backup_dir, 'runmero_persistence.db')
            
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_db) as backup:
                    source.backup(backup)
            
            backup_info = {
                'backup_name': backup_name,
                'timestamp': time.time(),
                'database_size': os.path.getsize(backup_db) if os.path.exists(backup_db) else 0,
                'version': '2.5.0'
            }
            
            info_file = os.path.join(backup_dir, 'backup_info.json')
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return backup_dir
            
        except Exception as e:
            print(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return ""
    
    def restore_from_backup(self, backup_name: str) -> bool:
        backup_dir = os.path.join(self.data_dir, 'backups', backup_name)
        backup_db = os.path.join(backup_dir, 'runmero_persistence.db')
        
        if not os.path.exists(backup_db):
            return False
        
        try:
            current_db_backup = f"{self.db_path}.before_restore"
            if os.path.exists(self.db_path):
                os.rename(self.db_path, current_db_backup)
            
            with sqlite3.connect(backup_db) as source:
                with sqlite3.connect(self.db_path) as target:
                    source.backup(target)
            
            return True
            
        except Exception as e:
            print(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            if os.path.exists(f"{self.db_path}.before_restore"):
                os.rename(f"{self.db_path}.before_restore", self.db_path)
            return False
    
    def cleanup_old_data(self, days: int = 30):
        cutoff_time = time.time() - (days * 24 * 3600)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM process_logs WHERE timestamp < ?', (cutoff_time,))
                cursor.execute('DELETE FROM system_events WHERE timestamp < ?', (cutoff_time,))
                
                cursor.execute('''
                    DELETE FROM processes 
                    WHERE status IN ('stopped', 'failed', 'completed') 
                    AND updated_at < ?
                ''', (cutoff_time,))
                
                conn.commit()
                
                cursor.execute('VACUUM')
                
        except Exception as e:
            print(f"خطأ في تنظيف البيانات القديمة: {e}")
    
    def _start_auto_save(self):
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.auto_save_thread.start()
    
    def _auto_save_loop(self):
        while self.auto_save_enabled:
            try:
                time.sleep(300)
                self._perform_maintenance()
            except Exception as e:
                print(f"خطأ في الحفظ التلقائي: {e}")
    
    def _perform_maintenance(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM process_logs WHERE id NOT IN (SELECT id FROM process_logs ORDER BY timestamp DESC LIMIT 10000)')
                cursor.execute('DELETE FROM system_events WHERE id NOT IN (SELECT id FROM system_events ORDER BY timestamp DESC LIMIT 5000)')
                
                conn.commit()
                
                if time.time() % 86400 < 300:
                    cursor.execute('VACUUM')
                    
        except Exception as e:
            print(f"خطأ في صيانة قاعدة البيانات: {e}")
    
    def force_save_all(self):
        try:
            processes = {}
            for pid in psutil.pids():
                try:
                    process = psutil.Process(pid)
                    if 'runmero' in ' '.join(process.cmdline()).lower():
                        processes[str(pid)] = {
                            'pid': pid,
                            'status': process.status(),
                            'name': process.name(),
                            'cmdline': process.cmdline(),
                            'create_time': process.create_time(),
                            'saved_at': time.time()
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            emergency_file = os.path.join(self.data_dir, 'emergency_processes.json')
            with open(emergency_file, 'w') as f:
                json.dump(processes, f, indent=2)
                
        except Exception as e:
            print(f"خطأ في الحفظ الطارئ: {e}")
    
    def get_persistence_stats(self) -> Dict[str, Any]:
        stats = {
            'data_directory': self.data_dir,
            'database_size': 0,
            'total_processes': 0,
            'active_processes': 0,
            'total_logs': 0,
            'total_events': 0,
            'configurations_count': 0,
            'disk_usage': 0
        }
        
        try:
            if os.path.exists(self.db_path):
                stats['database_size'] = os.path.getsize(self.db_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM processes')
                stats['total_processes'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM processes WHERE status = ?', ('running',))
                stats['active_processes'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM process_logs')
                stats['total_logs'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM system_events')
                stats['total_events'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM configurations')
                stats['configurations_count'] = cursor.fetchone()[0]
            
            total_size = 0
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            stats['disk_usage'] = total_size
            
        except Exception as e:
            print(f"خطأ في جلب إحصائيات المثابرة: {e}")
        
        return stats
    
    def __del__(self):
        self.auto_save_enabled = False
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.auto_save_thread.join(timeout=5)
