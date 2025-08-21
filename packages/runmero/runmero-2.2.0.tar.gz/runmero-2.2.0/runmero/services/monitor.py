# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة القدس الشريفة فلسطين

import os
import time
import threading
import psutil
import json
import socket
import subprocess
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
import statistics
import platform

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: float
    metric_name: str
    current_value: float
    threshold_value: float
    resolved: bool = False
    resolved_at: Optional[float] = None

@dataclass
class MetricDefinition:
    name: str
    type: MetricType
    description: str
    unit: str
    collection_interval: float = 10.0
    retention_period: float = 3600.0
    alert_thresholds: Optional[Dict[AlertLevel, float]] = None

@dataclass
class MetricDataPoint:
    timestamp: float
    value: float
    labels: Optional[Dict[str, str]] = None

class MetricCollector:
    def __init__(self, definition: MetricDefinition):
        self.definition = definition
        self.data_points: deque = deque(maxlen=int(definition.retention_period / definition.collection_interval))
        self.labels_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.last_collection_time = 0.0
        self.collection_count = 0
        self.lock = threading.Lock()
        
    def add_data_point(self, value: float, labels: Optional[Dict[str, str]] = None):
        with self.lock:
            timestamp = time.time()
            data_point = MetricDataPoint(timestamp, value, labels)
            self.data_points.append(data_point)
            
            if labels:
                labels_key = json.dumps(labels, sort_keys=True)
                self.labels_data[labels_key].append(data_point)
            
            self.last_collection_time = timestamp
            self.collection_count += 1
    
    def get_latest_value(self) -> Optional[float]:
        with self.lock:
            if self.data_points:
                return self.data_points[-1].value
            return None
    
    def get_values_in_range(self, start_time: float, end_time: float) -> List[MetricDataPoint]:
        with self.lock:
            return [dp for dp in self.data_points if start_time <= dp.timestamp <= end_time]
    
    def get_statistics(self, duration: float = 300.0) -> Dict[str, float]:
        with self.lock:
            cutoff_time = time.time() - duration
            recent_values = [dp.value for dp in self.data_points if dp.timestamp >= cutoff_time]
            
            if not recent_values:
                return {}
            
            return {
                'count': len(recent_values),
                'min': min(recent_values),
                'max': max(recent_values),
                'mean': statistics.mean(recent_values),
                'median': statistics.median(recent_values),
                'stdev': statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0,
                'p95': statistics.quantiles(recent_values, n=20)[18] if len(recent_values) >= 20 else max(recent_values),
                'p99': statistics.quantiles(recent_values, n=100)[98] if len(recent_values) >= 100 else max(recent_values)
            }

class SystemMonitor:
    def __init__(self):
        self.metrics: Dict[str, MetricCollector] = {}
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.running = False
        self.monitor_thread = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.lock = threading.Lock()
        self.collection_interval = 5.0
        
        self.logger = logging.getLogger('runmero.system_monitor')
        self._setup_logging()
        
        self._setup_default_metrics()
        
        self.is_termux = self._detect_termux()
        self.system_info = self._collect_system_info()
    
    def _setup_logging(self):
        handler = logging.FileHandler('/tmp/runmero_system_monitor.log')
        formatter = logging.Formatter(
            '[%(asctime)s] [SYSTEM_MONITOR] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _detect_termux(self) -> bool:
        return (
            os.path.exists('/data/data/com.termux') or
            os.getenv('TERMUX_VERSION') is not None or
            'termux' in os.getenv('PREFIX', '').lower()
        )
    
    def _collect_system_info(self) -> Dict[str, Any]:
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'is_termux': self.is_termux,
            'boot_time': psutil.boot_time()
        }
        
        if self.is_termux:
            try:
                info['termux_version'] = os.getenv('TERMUX_VERSION', 'unknown')
                info['android_version'] = self._get_android_version()
                info['device_model'] = self._get_device_model()
            except:
                pass
        
        return info
    
    def _get_android_version(self) -> str:
        try:
            result = subprocess.run('getprop ro.build.version.release', 
                                  shell=True, capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _get_device_model(self) -> str:
        try:
            result = subprocess.run('getprop ro.product.model', 
                                  shell=True, capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
    
    def _setup_default_metrics(self):
        default_metrics = [
            MetricDefinition(
                name="cpu_percent",
                type=MetricType.GAUGE,
                description="CPU usage percentage",
                unit="percent",
                collection_interval=5.0,
                alert_thresholds={
                    AlertLevel.WARNING: 80.0,
                    AlertLevel.CRITICAL: 95.0
                }
            ),
            MetricDefinition(
                name="memory_percent",
                type=MetricType.GAUGE,
                description="Memory usage percentage",
                unit="percent",
                collection_interval=5.0,
                alert_thresholds={
                    AlertLevel.WARNING: 85.0,
                    AlertLevel.CRITICAL: 95.0
                }
            ),
            MetricDefinition(
                name="disk_percent",
                type=MetricType.GAUGE,
                description="Disk usage percentage",
                unit="percent",
                collection_interval=30.0,
                alert_thresholds={
                    AlertLevel.WARNING: 85.0,
                    AlertLevel.CRITICAL: 95.0
                }
            ),
            MetricDefinition(
                name="load_average_1m",
                type=MetricType.GAUGE,
                description="System load average (1 minute)",
                unit="load",
                collection_interval=10.0,
                alert_thresholds={
                    AlertLevel.WARNING: psutil.cpu_count() * 0.8,
                    AlertLevel.CRITICAL: psutil.cpu_count() * 1.2
                }
            ),
            MetricDefinition(
                name="network_bytes_sent",
                type=MetricType.COUNTER,
                description="Network bytes sent",
                unit="bytes",
                collection_interval=10.0
            ),
            MetricDefinition(
                name="network_bytes_recv",
                type=MetricType.COUNTER,
                description="Network bytes received",
                unit="bytes",
                collection_interval=10.0
            ),
            MetricDefinition(
                name="process_count",
                type=MetricType.GAUGE,
                description="Number of running processes",
                unit="count",
                collection_interval=15.0,
                alert_thresholds={
                    AlertLevel.WARNING: 500,
                    AlertLevel.CRITICAL: 1000
                }
            ),
            MetricDefinition(
                name="open_files",
                type=MetricType.GAUGE,
                description="Number of open file descriptors",
                unit="count",
                collection_interval=15.0
            ),
            MetricDefinition(
                name="temperature",
                type=MetricType.GAUGE,
                description="System temperature",
                unit="celsius",
                collection_interval=30.0,
                alert_thresholds={
                    AlertLevel.WARNING: 70.0,
                    AlertLevel.CRITICAL: 85.0
                }
            )
        ]
        
        for metric_def in default_metrics:
            self.register_metric(metric_def)
    
    def register_metric(self, definition: MetricDefinition):
        with self.lock:
            self.metrics[definition.name] = MetricCollector(definition)
            self.logger.info(f"تم تسجيل المقياس: {definition.name}")
    
    def unregister_metric(self, metric_name: str):
        with self.lock:
            if metric_name in self.metrics:
                del self.metrics[metric_name]
                self.logger.info(f"تم إلغاء تسجيل المقياس: {metric_name}")
    
    def add_metric_value(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        with self.lock:
            if metric_name in self.metrics:
                self.metrics[metric_name].add_data_point(value, labels)
                self._check_alerts(metric_name, value)
    
    def get_metric_value(self, metric_name: str) -> Optional[float]:
        with self.lock:
            if metric_name in self.metrics:
                return self.metrics[metric_name].get_latest_value()
            return None
    
    def get_metric_statistics(self, metric_name: str, duration: float = 300.0) -> Dict[str, float]:
        with self.lock:
            if metric_name in self.metrics:
                return self.metrics[metric_name].get_statistics(duration)
            return {}
    
    def start_monitoring(self):
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("بدء مراقبة النظام")
    
    def stop_monitoring(self):
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        self.executor.shutdown(wait=True, timeout=10)
        self.logger.info("تم إيقاف مراقبة النظام")
    
    def _monitoring_loop(self):
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"خطأ في حلقة المراقبة: {e}")
                time.sleep(self.collection_interval * 2)
    
    def _collect_system_metrics(self):
        current_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric_value("cpu_percent", cpu_percent)
        except:
            pass
        
        try:
            memory = psutil.virtual_memory()
            self.add_metric_value("memory_percent", memory.percent)
        except:
            pass
        
        try:
            disk = psutil.disk_usage('/')
            self.add_metric_value("disk_percent", disk.percent)
        except:
            pass
        
        try:
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                self.add_metric_value("load_average_1m", load_avg[0])
        except:
            pass
        
        try:
            net_io = psutil.net_io_counters()
            self.add_metric_value("network_bytes_sent", net_io.bytes_sent)
            self.add_metric_value("network_bytes_recv", net_io.bytes_recv)
        except:
            pass
        
        try:
            process_count = len(psutil.pids())
            self.add_metric_value("process_count", process_count)
        except:
            pass
        
        try:
            current_process = psutil.Process()
            open_files = len(current_process.open_files())
            self.add_metric_value("open_files", open_files)
        except:
            pass
        
        if self.is_termux:
            self._collect_termux_specific_metrics()
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current:
                            self.add_metric_value("temperature", entry.current, {"sensor": name})
                            break
        except:
            pass
    
    def _collect_termux_specific_metrics(self):
        try:
            battery_info = self._get_battery_info()
            if battery_info:
                if 'percentage' in battery_info:
                    self.add_metric_value("battery_percent", battery_info['percentage'])
                if 'temperature' in battery_info:
                    self.add_metric_value("battery_temperature", battery_info['temperature'])
        except:
            pass
    
    def _get_battery_info(self) -> Optional[Dict[str, Any]]:
        try:
            result = subprocess.run('termux-battery-status', 
                                  shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
    
    def _check_alerts(self, metric_name: str, value: float):
        with self.lock:
            if metric_name not in self.metrics:
                return
            
            collector = self.metrics[metric_name]
            thresholds = collector.definition.alert_thresholds
            
            if not thresholds:
                return
            
            for level, threshold in thresholds.items():
                if value >= threshold:
                    alert_id = f"{metric_name}_{level.value}_{int(time.time())}"
                    
                    existing_alert = None
                    for alert in self.alerts:
                        if (alert.metric_name == metric_name and 
                            alert.level == level and 
                            not alert.resolved and
                            time.time() - alert.timestamp < 300):
                            existing_alert = alert
                            break
                    
                    if not existing_alert:
                        alert = Alert(
                            id=alert_id,
                            level=level,
                            title=f"تنبيه {level.value.upper()}: {metric_name}",
                            message=f"المقياس {metric_name} وصل إلى {value:.2f} {collector.definition.unit} (الحد: {threshold})",
                            timestamp=time.time(),
                            metric_name=metric_name,
                            current_value=value,
                            threshold_value=threshold
                        )
                        
                        self.alerts.append(alert)
                        self._trigger_alert_handlers(alert)
                        
                        self.logger.warning(f"تنبيه جديد: {alert.title} - {alert.message}")
                        
                        if len(self.alerts) > 1000:
                            self.alerts = self.alerts[-500:]
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        self.alert_handlers.append(handler)
    
    def _trigger_alert_handlers(self, alert: Alert):
        for handler in self.alert_handlers:
            try:
                self.executor.submit(handler, alert)
            except Exception as e:
                self.logger.error(f"خطأ في معالج التنبيه: {e}")
    
    def get_alerts(self, level: Optional[AlertLevel] = None, resolved: Optional[bool] = None) -> List[Alert]:
        with self.lock:
            alerts = self.alerts.copy()
            
            if level:
                alerts = [a for a in alerts if a.level == level]
            
            if resolved is not None:
                alerts = [a for a in alerts if a.resolved == resolved]
            
            return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str):
        with self.lock:
            for alert in self.alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = time.time()
                    self.logger.info(f"تم حل التنبيه: {alert_id}")
                    return True
            return False
    
    def get_system_overview(self) -> Dict[str, Any]:
        overview = {
            'timestamp': time.time(),
            'system_info': self.system_info,
            'metrics': {},
            'alerts_summary': {
                'total': len(self.alerts),
                'unresolved': len([a for a in self.alerts if not a.resolved]),
                'critical': len([a for a in self.alerts if a.level == AlertLevel.CRITICAL and not a.resolved]),
                'warning': len([a for a in self.alerts if a.level == AlertLevel.WARNING and not a.resolved])
            }
        }
        
        for name, collector in self.metrics.items():
            latest_value = collector.get_latest_value()
            if latest_value is not None:
                overview['metrics'][name] = {
                    'current_value': latest_value,
                    'unit': collector.definition.unit,
                    'statistics': collector.get_statistics(300)
                }
        
        return overview
    
    def export_metrics(self, filepath: str, duration: float = 3600.0):
        export_data = {
            'timestamp': time.time(),
            'duration': duration,
            'system_info': self.system_info,
            'metrics': {}
        }
        
        cutoff_time = time.time() - duration
        
        with self.lock:
            for name, collector in self.metrics.items():
                metric_data = {
                    'definition': asdict(collector.definition),
                    'data_points': []
                }
                
                for dp in collector.data_points:
                    if dp.timestamp >= cutoff_time:
                        metric_data['data_points'].append(asdict(dp))
                
                export_data['metrics'][name] = metric_data
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"تم تصدير المقاييس إلى: {filepath}")

class ResourceMonitor:
    def __init__(self, process_ids: Optional[List[int]] = None):
        self.process_ids = process_ids or []
        self.resource_data: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.monitoring = False
        self.monitor_thread = None
        self.collection_interval = 5.0
        self.retention_period = 3600.0
        self.lock = threading.Lock()
        
        self.logger = logging.getLogger('runmero.resource_monitor')
    
    def add_process(self, pid: int):
        with self.lock:
            if pid not in self.process_ids:
                self.process_ids.append(pid)
                self.logger.info(f"إضافة العملية للمراقبة: {pid}")
    
    def remove_process(self, pid: int):
        with self.lock:
            if pid in self.process_ids:
                self.process_ids.remove(pid)
                if pid in self.resource_data:
                    del self.resource_data[pid]
                self.logger.info(f"إزالة العملية من المراقبة: {pid}")
    
    def start_monitoring(self):
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("بدء مراقبة الموارد")
    
    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        self.logger.info("تم إيقاف مراقبة الموارد")
    
    def _monitoring_loop(self):
        while self.monitoring:
            try:
                self._collect_process_data()
                self._cleanup_old_data()
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"خطأ في مراقبة الموارد: {e}")
                time.sleep(self.collection_interval * 2)
    
    def _collect_process_data(self):
        current_time = time.time()
        
        with self.lock:
            for pid in self.process_ids.copy():
                try:
                    process = psutil.Process(pid)
                    
                    data = {
                        'timestamp': current_time,
                        'pid': pid,
                        'name': process.name(),
                        'status': process.status(),
                        'cpu_percent': process.cpu_percent(),
                        'memory_info': process.memory_info()._asdict(),
                        'memory_percent': process.memory_percent(),
                        'num_threads': process.num_threads(),
                        'create_time': process.create_time()
                    }
                    
                    try:
                        data['connections'] = len(process.connections())
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        data['connections'] = 0
                    
                    try:
                        data['open_files'] = len(process.open_files())
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        data['open_files'] = 0
                    
                    try:
                        io_counters = process.io_counters()
                        data['io_counters'] = io_counters._asdict()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        data['io_counters'] = {}
                    
                    self.resource_data[pid].append(data)
                    
                except psutil.NoSuchProcess:
                    self.process_ids.remove(pid)
                    if pid in self.resource_data:
                        del self.resource_data[pid]
                    self.logger.info(f"العملية {pid} لم تعد موجودة")
                except Exception as e:
                    self.logger.error(f"خطأ في جمع بيانات العملية {pid}: {e}")
    
    def _cleanup_old_data(self):
        cutoff_time = time.time() - self.retention_period
        
        with self.lock:
            for pid in self.resource_data:
                self.resource_data[pid] = [
                    data for data in self.resource_data[pid]
                    if data['timestamp'] >= cutoff_time
                ]
    
    def get_process_data(self, pid: int, duration: float = 300.0) -> List[Dict[str, Any]]:
        cutoff_time = time.time() - duration
        
        with self.lock:
            if pid in self.resource_data:
                return [
                    data for data in self.resource_data[pid]
                    if data['timestamp'] >= cutoff_time
                ]
            return []
    
    def get_process_statistics(self, pid: int, duration: float = 300.0) -> Dict[str, Any]:
        data_points = self.get_process_data(pid, duration)
        
        if not data_points:
            return {}
        
        cpu_values = [dp['cpu_percent'] for dp in data_points if 'cpu_percent' in dp]
        memory_values = [dp['memory_percent'] for dp in data_points if 'memory_percent' in dp]
        
        stats = {
            'duration': duration,
            'data_points_count': len(data_points),
            'first_timestamp': min(dp['timestamp'] for dp in data_points),
            'last_timestamp': max(dp['timestamp'] for dp in data_points)
        }
        
        if cpu_values:
            stats['cpu_stats'] = {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'mean': statistics.mean(cpu_values),
                'median': statistics.median(cpu_values)
            }
        
        if memory_values:
            stats['memory_stats'] = {
                'min': min(memory_values),
                'max': max(memory_values),
                'mean': statistics.mean(memory_values),
                'median': statistics.median(memory_values)
            }
        
        return stats
    
    def get_all_processes_summary(self) -> Dict[str, Any]:
        summary = {
            'monitored_processes': len(self.process_ids),
            'total_data_points': sum(len(data) for data in self.resource_data.values()),
            'processes': {}
        }
        
        with self.lock:
            for pid in self.process_ids:
                if pid in self.resource_data and self.resource_data[pid]:
                    latest_data = self.resource_data[pid][-1]
                    summary['processes'][pid] = {
                        'name': latest_data.get('name', 'unknown'),
                        'status': latest_data.get('status', 'unknown'),
                        'cpu_percent': latest_data.get('cpu_percent', 0),
                        'memory_percent': latest_data.get('memory_percent', 0),
                        'last_update': latest_data.get('timestamp', 0)
                    }
        
        return summary

class PerformanceMonitor:
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.resource_monitor = ResourceMonitor()
        self.performance_profiles: Dict[str, Dict[str, Any]] = {}
        self.benchmarks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.optimization_suggestions: List[Dict[str, Any]] = []
        self.monitoring_active = False
        
        self.logger = logging.getLogger('runmero.performance_monitor')
        
        self._setup_performance_profiles()
    
    def _setup_performance_profiles(self):
        self.performance_profiles = {
            'battery_saver': {
                'description': 'توفير البطارية',
                'cpu_limit': 50,
                'memory_limit': 70,
                'network_limit': 'low',
                'background_processes_limit': 5
            },
            'balanced': {
                'description': 'متوازن',
                'cpu_limit': 80,
                'memory_limit': 85,
                'network_limit': 'medium',
                'background_processes_limit': 10
            },
            'performance': {
                'description': 'أداء عالي',
                'cpu_limit': 95,
                'memory_limit': 90,
                'network_limit': 'high',
                'background_processes_limit': 20
            }
        }
    
    def start_monitoring(self):
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.system_monitor.start_monitoring()
        self.resource_monitor.start_monitoring()
        
        self.system_monitor.add_alert_handler(self._handle_performance_alert)
        
        self.logger.info("بدء مراقبة الأداء الشاملة")
    
    def stop_monitoring(self):
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.system_monitor.stop_monitoring()
        self.resource_monitor.stop_monitoring()
        
        self.logger.info("تم إيقاف مراقبة الأداء")
    
    def _handle_performance_alert(self, alert: Alert):
        suggestion = self._generate_optimization_suggestion(alert)
        if suggestion:
            self.optimization_suggestions.append(suggestion)
            self.logger.info(f"اقتراح تحسين جديد: {suggestion['title']}")
    
    def _generate_optimization_suggestion(self, alert: Alert) -> Optional[Dict[str, Any]]:
        suggestions_map = {
            'cpu_percent': {
                'title': 'تحسين استخدام المعالج',
                'description': 'استخدام المعالج مرتفع، يُنصح بتقليل العمليات المتزامنة',
                'actions': [
                    'تقليل عدد العمليات النشطة',
                    'تحسين خوارزميات المعالجة',
                    'تفعيل وضع توفير الطاقة'
                ]
            },
            'memory_percent': {
                'title': 'تحسين استخدام الذاكرة',
                'description': 'استخدام الذاكرة مرتفع، يُنصح بتحرير الذاكرة غير المستخدمة',
                'actions': [
                    'تنظيف cache غير الضروري',
                    'إغلاق العمليات غير المستخدمة',
                    'تحسين إدارة الذاكرة'
                ]
            },
            'disk_percent': {
                'title': 'تحسين استخدام القرص',
                'description': 'مساحة القرص منخفضة، يُنصح بتنظيف الملفات',
                'actions': [
                    'حذف الملفات المؤقتة',
                    'تنظيف ملفات السجل القديمة',
                    'ضغط الملفات الكبيرة'
                ]
            }
        }
        
        if alert.metric_name in suggestions_map:
            suggestion = suggestions_map[alert.metric_name].copy()
            suggestion.update({
                'timestamp': time.time(),
                'alert_id': alert.id,
                'severity': alert.level.value,
                'current_value': alert.current_value,
                'threshold': alert.threshold_value
            })
            return suggestion
        
        return None
    
    def run_benchmark(self, benchmark_name: str, duration: float = 60.0) -> Dict[str, Any]:
        self.logger.info(f"بدء تشغيل معيار الأداء: {benchmark_name}")
        
        start_time = time.time()
        
        initial_metrics = self.system_monitor.get_system_overview()
        
        benchmark_data = {
            'name': benchmark_name,
            'start_time': start_time,
            'duration': duration,
            'initial_metrics': initial_metrics['metrics'],
            'samples': []
        }
        
        sample_interval = 5.0
        samples_count = int(duration / sample_interval)
        
        for i in range(samples_count):
            time.sleep(sample_interval)
            
            current_metrics = self.system_monitor.get_system_overview()
            sample = {
                'timestamp': time.time(),
                'elapsed': time.time() - start_time,
                'metrics': current_metrics['metrics']
            }
            benchmark_data['samples'].append(sample)
        
        end_time = time.time()
        final_metrics = self.system_monitor.get_system_overview()
        
        benchmark_data.update({
            'end_time': end_time,
            'actual_duration': end_time - start_time,
            'final_metrics': final_metrics['metrics'],
            'statistics': self._calculate_benchmark_statistics(benchmark_data)
        })
        
        self.benchmarks[benchmark_name].append(benchmark_data)
        
        self.logger.info(f"انتهاء معيار الأداء: {benchmark_name}")
        return benchmark_data
    
    def _calculate_benchmark_statistics(self, benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        stats = {}
        
        for metric_name in ['cpu_percent', 'memory_percent']:
            values = []
            for sample in benchmark_data['samples']:
                if metric_name in sample['metrics']:
                    values.append(sample['metrics'][metric_name]['current_value'])
            
            if values:
                stats[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0.0
                }
        
        return stats
    
    def get_performance_report(self) -> Dict[str, Any]:
        system_overview = self.system_monitor.get_system_overview()
        resource_summary = self.resource_monitor.get_all_processes_summary()
        
        report = {
            'timestamp': time.time(),
            'system_overview': system_overview,
            'resource_summary': resource_summary,
            'active_alerts': len(self.system_monitor.get_alerts(resolved=False)),
            'optimization_suggestions': self.optimization_suggestions[-10:],
            'recent_benchmarks': {
                name: benchmarks[-1] if benchmarks else None
                for name, benchmarks in self.benchmarks.items()
            },
            'performance_score': self._calculate_performance_score()
        }
        
        return report
    
    def _calculate_performance_score(self) -> int:
        try:
            cpu_value = self.system_monitor.get_metric_value('cpu_percent') or 0
            memory_value = self.system_monitor.get_metric_value('memory_percent') or 0
            
            cpu_score = max(0, 100 - cpu_value)
            memory_score = max(0, 100 - memory_value)
            
            unresolved_alerts = len(self.system_monitor.get_alerts(resolved=False))
            alert_penalty = min(50, unresolved_alerts * 10)
            
            total_score = int((cpu_score + memory_score) / 2 - alert_penalty)
            return max(0, min(100, total_score))
            
        except Exception:
            return 50
    
    def apply_performance_profile(self, profile_name: str) -> bool:
        if profile_name not in self.performance_profiles:
            return False
        
        profile = self.performance_profiles[profile_name]
        
        try:
            if profile_name == 'battery_saver':
                self._apply_battery_saver_optimizations()
            elif profile_name == 'performance':
                self._apply_performance_optimizations()
            
            self.logger.info(f"تم تطبيق ملف الأداء: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تطبيق ملف الأداء: {e}")
            return False
    
    def _apply_battery_saver_optimizations(self):
        try:
            for cpu in range(psutil.cpu_count()):
                cpu_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                if os.path.exists(cpu_path):
                    try:
                        with open(cpu_path, 'w') as f:
                            f.write('powersave')
                    except (PermissionError, OSError):
                        pass
        except Exception:
            pass
    
    def _apply_performance_optimizations(self):
        try:
            for cpu in range(psutil.cpu_count()):
                cpu_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                if os.path.exists(cpu_path):
                    try:
                        with open(cpu_path, 'w') as f:
                            f.write('performance')
                    except (PermissionError, OSError):
                        pass
        except Exception:
            pass
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        return self.optimization_suggestions.copy()
    
    def clear_optimization_suggestions(self):
        self.optimization_suggestions.clear()
        self.logger.info("تم مسح اقتراحات التحسين")
    
    def export_performance_data(self, filepath: str):
        performance_data = {
            'timestamp': time.time(),
            'report': self.get_performance_report(),
            'benchmarks': dict(self.benchmarks),
            'optimization_suggestions': self.optimization_suggestions,
            'performance_profiles': self.performance_profiles
        }
        
        with open(filepath, 'w') as f:
            json.dump(performance_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"تم تصدير بيانات الأداء إلى: {filepath}")
