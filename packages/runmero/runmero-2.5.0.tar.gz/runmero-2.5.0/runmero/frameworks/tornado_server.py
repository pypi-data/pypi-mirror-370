# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة غزة العزة فلسطين

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.netutil
import tornado.process
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import json
import time
import os
import threading
import asyncio
import psutil
from typing import Dict, Any, List, Optional, Callable

class TornadoServer:
    def __init__(self, 
                 app_name: str = "RunMero Tornado Server",
                 host: str = "0.0.0.0",
                 port: int = 8888,
                 debug: bool = False,
                 auto_reload: bool = False,
                 max_workers: int = 4):
        
        self.app_name = app_name
        self.host = host
        self.port = port
        self.debug = debug
        self.auto_reload = auto_reload
        self.max_workers = max_workers
        
        self._running = False
        self._server = None
        self._ioloop = None
        self._server_thread = None
        self._start_time = None
        self._request_count = 0
        self._websocket_connections = set()
        
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._setup_handlers()
        self._create_application()

    def _setup_handlers(self):
        class BaseHandler(tornado.web.RequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.server_instance = self.application.settings.get('server_instance')

            def set_default_headers(self):
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                self.set_header("X-Powered-By", "RunMero Tornado - فلسطين")
                self.set_header("X-Server-Time", str(time.time()))

            def options(self, *args):
                self.set_status(200)
                self.finish()

            def write_json(self, data):
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(json.dumps(data, ensure_ascii=False, indent=2))

        class HomeHandler(BaseHandler):
            def get(self):
                if self.server_instance:
                    self.server_instance._request_count += 1
                
                self.write_json({
                    "message": "مرحباً بك في خادم Tornado المدعوم بـ RunMero",
                    "version": "2.5.0",
                    "author": "mero", 
                    "country": "فلسطين الحبيبة",
                    "status": "running",
                    "uptime": time.time() - (self.server_instance._start_time or time.time()) if self.server_instance else 0,
                    "requests_served": self.server_instance._request_count if self.server_instance else 0,
                    "framework": "Tornado",
                    "server": self.server_instance.app_name if self.server_instance else "RunMero Tornado"
                })

        class HealthHandler(BaseHandler):
            def get(self):
                self.write_json({
                    "status": "healthy",
                    "timestamp": time.time(),
                    "server": self.server_instance.app_name if self.server_instance else "RunMero Tornado",
                    "process_id": os.getpid(),
                    "tornado_version": tornado.version
                })

        class StatusHandler(BaseHandler):
            def get(self):
                process = psutil.Process()
                
                self.write_json({
                    "server_info": {
                        "name": self.server_instance.app_name if self.server_instance else "RunMero Tornado",
                        "host": self.server_instance.host if self.server_instance else "unknown",
                        "port": self.server_instance.port if self.server_instance else 0,
                        "running": self.server_instance._running if self.server_instance else False,
                        "uptime": time.time() - (self.server_instance._start_time or time.time()) if self.server_instance and self.server_instance._start_time else 0,
                        "requests": self.server_instance._request_count if self.server_instance else 0,
                        "websocket_connections": len(self.server_instance._websocket_connections) if self.server_instance else 0
                    },
                    "system_info": {
                        "cpu_percent": process.cpu_percent(),
                        "memory_info": process.memory_info()._asdict(),
                        "threads": process.num_threads(),
                        "connections": len(process.connections()) if hasattr(process, 'connections') else 0
                    },
                    "environment": {
                        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                        "platform": os.name,
                        "pid": os.getpid(),
                        "tornado_version": tornado.version
                    }
                })

        class ProcessesHandler(BaseHandler):
            @run_on_executor
            def get_processes(self):
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return processes

            async def get(self):
                try:
                    processes = await self.get_processes()
                    self.write_json({
                        "processes": processes[:30],
                        "total": len(processes),
                        "timestamp": time.time()
                    })
                except Exception as e:
                    self.set_status(500)
                    self.write_json({"error": str(e)})

            async def post(self):
                try:
                    data = json.loads(self.request.body)
                    self.write_json({
                        "message": f"تم إنشاء العملية: {data.get('name', 'unknown')}",
                        "process": data,
                        "timestamp": time.time()
                    })
                except json.JSONDecodeError:
                    self.set_status(400)
                    self.write_json({"error": "بيانات JSON غير صالحة"})

        class SystemHandler(BaseHandler):
            @run_on_executor
            def get_system_info(self):
                return {
                    "cpu": {
                        "percent": psutil.cpu_percent(interval=1),
                        "count": psutil.cpu_count(),
                        "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                    },
                    "memory": psutil.virtual_memory()._asdict(),
                    "disk": psutil.disk_usage('/')._asdict(),
                    "network": {name: stats._asdict() for name, stats in psutil.net_io_counters(pernic=True).items()},
                    "boot_time": psutil.boot_time(),
                    "uptime": time.time() - psutil.boot_time()
                }

            async def get(self):
                try:
                    system_info = await self.get_system_info()
                    self.write_json(system_info)
                except Exception as e:
                    self.set_status(500)
                    self.write_json({"error": str(e)})

        class DashboardHandler(BaseHandler):
            def get(self):
                dashboard_html = """
                <!DOCTYPE html>
                <html dir="rtl" lang="ar">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>لوحة تحكم RunMero Tornado</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Arial, sans-serif; 
                            margin: 0; padding: 20px; 
                            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                            min-height: 100vh; color: #333;
                        }
                        .container { max-width: 1400px; margin: 0 auto; }
                        .header { 
                            background: rgba(255,255,255,0.95); 
                            color: #333; padding: 30px; 
                            border-radius: 20px; 
                            margin-bottom: 30px; 
                            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
                            backdrop-filter: blur(20px);
                        }
                        .stats { 
                            display: grid; 
                            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                            gap: 25px; margin-bottom: 30px; 
                        }
                        .stat-card { 
                            background: rgba(255,255,255,0.95); 
                            padding: 30px; border-radius: 20px; 
                            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
                            backdrop-filter: blur(20px);
                            transition: all 0.4s ease;
                            position: relative;
                            overflow: hidden;
                        }
                        .stat-card:before {
                            content: '';
                            position: absolute;
                            top: 0; right: 0;
                            width: 100%; height: 4px;
                            background: linear-gradient(45deg, #1e3c72, #2a5298);
                        }
                        .stat-card:hover { 
                            transform: translateY(-8px) scale(1.02); 
                            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
                        }
                        .stat-value { 
                            font-size: 3em; font-weight: bold; 
                            color: #1e3c72; margin: 15px 0;
                            text-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                            display: flex; align-items: center;
                        }
                        .stat-icon {
                            font-size: 1.2em; margin-left: 15px;
                            opacity: 0.8;
                        }
                        .stat-label { 
                            color: #666; font-size: 1.1em; 
                            font-weight: 600; margin-bottom: 10px;
                        }
                        .info-section { 
                            background: rgba(255,255,255,0.95); 
                            padding: 30px; border-radius: 20px; 
                            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
                            backdrop-filter: blur(20px);
                            margin-bottom: 25px;
                        }
                        .refresh-btn { 
                            background: linear-gradient(45deg, #1e3c72, #2a5298); 
                            color: white; border: none; 
                            padding: 15px 30px; border-radius: 30px; 
                            cursor: pointer; font-weight: bold;
                            font-size: 1.1em;
                            transition: all 0.4s ease;
                            box-shadow: 0 6px 20px rgba(30, 60, 114, 0.3);
                        }
                        .refresh-btn:hover { 
                            transform: scale(1.05) translateY(-2px); 
                            box-shadow: 0 10px 30px rgba(30, 60, 114, 0.5);
                        }
                        h1 { margin: 0; font-size: 2.8em; color: #1e3c72; }
                        h2 { color: #1e3c72; font-size: 1.8em; }
                        pre { 
                            background: #f8f9fa; padding: 20px; 
                            border-radius: 15px; overflow-x: auto;
                            border-right: 6px solid #1e3c72;
                            font-family: 'Courier New', monospace;
                            font-size: 0.9em; line-height: 1.5;
                        }
                        .websocket-status {
                            display: inline-block;
                            padding: 8px 16px;
                            background: linear-gradient(45deg, #28a745, #20c997);
                            color: white;
                            border-radius: 20px;
                            font-size: 0.9em;
                            font-weight: bold;
                        }
                        .realtime-data {
                            animation: pulse 2s infinite;
                        }
                        @keyframes pulse {
                            0% { opacity: 1; }
                            50% { opacity: 0.7; }
                            100% { opacity: 1; }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🌪️ لوحة تحكم RunMero Tornado Server</h1>
                            <p style="font-size: 1.2em; margin: 10px 0;">خادم Tornado فائق السرعة مدعوم بمكتبة RunMero - صنع بقوة في فلسطين الحبيبة 🇵🇸</p>
                            <div class="websocket-status">🔗 WebSocket متاح</div>
                            <small style="margin-right: 15px;">Tornado Version: """ + tornado.version + """</small>
                        </div>
                        
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-label">📊 الطلبات المخدومة</div>
                                <div class="stat-value realtime-data" id="requests">
                                    <span class="stat-icon">📈</span>
                                    """ + str(self._request_count) + """
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">⏱️ وقت التشغيل (ثانية)</div>
                                <div class="stat-value realtime-data" id="uptime">
                                    <span class="stat-icon">🕐</span>
                                    """ + str(int(time.time() - (self._start_time or time.time()))) + """
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">🔗 اتصالات WebSocket</div>
                                <div class="stat-value realtime-data" id="websockets">
                                    <span class="stat-icon">🌐</span>
                                    """ + str(len(self._websocket_connections)) + """
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">🆔 معرف العملية</div>
                                <div class="stat-value">
                                    <span class="stat-icon">⚙️</span>
                                    """ + str(os.getpid()) + """
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">💾 استخدام الذاكرة</div>
                                <div class="stat-value realtime-data" id="memory">
                                    <span class="stat-icon">🧠</span>
                                    """ + f"{psutil.Process().memory_percent():.1f}%" + """
                                </div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">⚡ حالة الخادم</div>
                                <div class="stat-value" style="color: #28a745; font-size: 2em;">
                                    <span class="stat-icon">✅</span>
                                    نشط
                                </div>
                            </div>
                        </div>
                        
                        <div class="info-section">
                            <h2>📋 معلومات النظام المتقدمة</h2>
                            <button class="refresh-btn" onclick="loadData()">🔄 تحديث البيانات</button>
                            <button class="refresh-btn" onclick="connectWebSocket()">🔗 اتصال WebSocket</button>
                            <pre id="system-info">معلومات النظام جاري التحميل...</pre>
                        </div>
                        
                        <div class="info-section">
                            <h2>📡 رسائل الوقت الفعلي</h2>
                            <div id="websocket-messages" style="background: #f8f9fa; padding: 15px; border-radius: 10px; min-height: 150px; max-height: 300px; overflow-y: auto; font-family: monospace;"></div>
                        </div>
                    </div>
                    
                    <script>
                        let ws = null;
                        
                        function updateStats() {
                            fetch('/status')
                                .then(response => response.json())
                                .then(data => {
                                    document.getElementById('requests').innerHTML = 
                                        '<span class="stat-icon">📈</span>' + data.server_info.requests;
                                    document.getElementById('uptime').innerHTML = 
                                        '<span class="stat-icon">🕐</span>' + Math.round(data.server_info.uptime);
                                    document.getElementById('websockets').innerHTML = 
                                        '<span class="stat-icon">🌐</span>' + data.server_info.websocket_connections;
                                    document.getElementById('memory').innerHTML = 
                                        '<span class="stat-icon">🧠</span>' + data.system_info.memory_info.percent.toFixed(1) + '%';
                                })
                                .catch(error => console.error('خطأ في جلب البيانات:', error));
                        }
                        
                        function loadData() {
                            Promise.all([
                                fetch('/api/system').then(r => r.json()),
                                fetch('/status').then(r => r.json())
                            ])
                            .then(([systemData, statusData]) => {
                                const info = {
                                    system: systemData,
                                    server: statusData
                                };
                                document.getElementById('system-info').textContent = JSON.stringify(info, null, 2);
                            })
                            .catch(error => {
                                document.getElementById('system-info').textContent = 'خطأ في تحميل البيانات: ' + error.message;
                            });
                        }
                        
                        function connectWebSocket() {
                            if (ws && ws.readyState === WebSocket.OPEN) return;
                            
                            ws = new WebSocket('ws://localhost:""" + str(self.port) + """/ws');
                            
                            ws.onopen = function(event) {
                                addMessage('✅ تم الاتصال بـ WebSocket');
                                ws.send(JSON.stringify({type: 'ping', timestamp: new Date().getTime()}));
                            };
                            
                            ws.onmessage = function(event) {
                                const data = JSON.parse(event.data);
                                addMessage('📨 رسالة واردة: ' + JSON.stringify(data));
                            };
                            
                            ws.onclose = function(event) {
                                addMessage('❌ انقطع الاتصال بـ WebSocket');
                            };
                            
                            ws.onerror = function(error) {
                                addMessage('🚨 خطأ في WebSocket: ' + error);
                            };
                        }
                        
                        function addMessage(message) {
                            const messagesDiv = document.getElementById('websocket-messages');
                            const timestamp = new Date().toLocaleString('ar-EG');
                            messagesDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }
                        
                        updateStats();
                        loadData();
                        connectWebSocket();
                        
                        setInterval(updateStats, 3000);
                        setInterval(() => {
                            if (ws && ws.readyState === WebSocket.OPEN) {
                                ws.send(JSON.stringify({type: 'heartbeat', timestamp: new Date().getTime()}));
                            }
                        }, 10000);
                    </script>
                </body>
                </html>
                """
                self.set_header("Content-Type", "text/html; charset=utf-8")
                self.write(dashboard_html)

        class WebSocketHandler(tornado.websocket.WebSocketHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.server_instance = self.application.settings.get('server_instance')

            def check_origin(self, origin):
                return True

            def open(self):
                if self.server_instance:
                    self.server_instance._websocket_connections.add(self)
                
                self.write_message(json.dumps({
                    "type": "connection",
                    "message": "مرحباً بك في WebSocket الخاص بـ RunMero Tornado",
                    "timestamp": time.time(),
                    "server": self.server_instance.app_name if self.server_instance else "RunMero Tornado"
                }))

            def on_message(self, message):
                try:
                    data = json.loads(message)
                    
                    if data.get('type') == 'ping':
                        self.write_message(json.dumps({
                            "type": "pong",
                            "timestamp": time.time(),
                            "original_timestamp": data.get('timestamp')
                        }))
                    
                    elif data.get('type') == 'heartbeat':
                        self.write_message(json.dumps({
                            "type": "heartbeat_response",
                            "timestamp": time.time(),
                            "server_status": "healthy",
                            "connections": len(self.server_instance._websocket_connections) if self.server_instance else 1
                        }))
                    
                    else:
                        self.write_message(json.dumps({
                            "type": "echo",
                            "message": f"تم استلام الرسالة: {message}",
                            "timestamp": time.time()
                        }))
                        
                except json.JSONDecodeError:
                    self.write_message(json.dumps({
                        "type": "error",
                        "message": "رسالة JSON غير صالحة",
                        "timestamp": time.time()
                    }))

            def on_close(self):
                if self.server_instance and self in self.server_instance._websocket_connections:
                    self.server_instance._websocket_connections.remove(self)

        self.handler_classes = {
            'HomeHandler': HomeHandler,
            'HealthHandler': HealthHandler,
            'StatusHandler': StatusHandler,
            'ProcessesHandler': ProcessesHandler,
            'SystemHandler': SystemHandler,
            'DashboardHandler': DashboardHandler,
            'WebSocketHandler': WebSocketHandler
        }

    def _create_application(self):
        handlers = [
            (r"/", self.handler_classes['HomeHandler']),
            (r"/health", self.handler_classes['HealthHandler']),
            (r"/status", self.handler_classes['StatusHandler']),
            (r"/api/processes", self.handler_classes['ProcessesHandler']),
            (r"/api/system", self.handler_classes['SystemHandler']),
            (r"/dashboard", self.handler_classes['DashboardHandler']),
            (r"/ws", self.handler_classes['WebSocketHandler']),
        ]
        
        settings = {
            "debug": self.debug,
            "autoreload": self.auto_reload,
            "server_instance": self,
            "compress_response": True,
        }
        
        self.application = tornado.web.Application(handlers, **settings)

    def add_handler(self, pattern: str, handler_class):
        self.application.add_handlers(r".*$", [(pattern, handler_class)])

    def run_in_background(self):
        if self._running:
            return False
        
        def server_worker():
            self._running = True
            self._start_time = time.time()
            
            try:
                asyncio.set_event_loop(asyncio.new_event_loop())
                self._ioloop = tornado.ioloop.IOLoop.current()
                
                self._server = tornado.httpserver.HTTPServer(self.application)
                self._server.listen(self.port, address=self.host)
                
                print(f"Tornado server بدأ العمل على {self.host}:{self.port}")
                self._ioloop.start()
                
            except Exception as e:
                print(f"خطأ في تشغيل خادم Tornado: {e}")
            finally:
                self._running = False
        
        self._server_thread = threading.Thread(target=server_worker, daemon=True)
        self._server_thread.start()
        
        time.sleep(2)
        return self._running

    def run_sync(self):
        self._running = True
        self._start_time = time.time()
        
        try:
            self._ioloop = tornado.ioloop.IOLoop.current()
            
            self._server = tornado.httpserver.HTTPServer(self.application)
            self._server.listen(self.port, address=self.host)
            
            print(f"Tornado server بدأ العمل على {self.host}:{self.port}")
            self._ioloop.start()
            
        except KeyboardInterrupt:
            print("تم إيقاف الخادم بواسطة المستخدم")
        except Exception as e:
            print(f"خطأ في تشغيل الخادم: {e}")
        finally:
            self._running = False

    def stop(self):
        self._running = False
        
        if self._server:
            self._server.stop()
        
        if self._ioloop:
            self._ioloop.add_callback(self._ioloop.stop)
        
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=10)

    def is_running(self) -> bool:
        return self._running

    def get_application(self):
        return self.application

    def get_stats(self) -> Dict[str, Any]:
        return {
            "requests": self._request_count,
            "uptime": time.time() - (self._start_time or time.time()) if self._start_time else 0,
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "websocket_connections": len(self._websocket_connections),
            "tornado_version": tornado.version
        }

    def broadcast_to_websockets(self, message: dict):
        dead_connections = []
        for ws in self._websocket_connections:
            try:
                ws.write_message(json.dumps(message))
            except Exception:
                dead_connections.append(ws)
        
        for dead_ws in dead_connections:
            self._websocket_connections.discard(dead_ws)

    def create_custom_handler(self, path: str, methods: List[str] = None):
        if methods is None:
            methods = ['GET']
        
        class CustomHandler(tornado.web.RequestHandler):
            def set_default_headers(self):
                self.set_header("Access-Control-Allow-Origin", "*")
                self.set_header("Access-Control-Allow-Headers", "Content-Type")
                self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                self.set_header("X-Powered-By", "RunMero Tornado - فلسطين")

            def options(self):
                self.set_status(200)
                self.finish()

            def get(self):
                if 'GET' in methods:
                    self.write({"message": f"Custom GET handler for {path}", "timestamp": time.time()})
                else:
                    self.set_status(405)
                    self.write({"error": "Method not allowed"})

            def post(self):
                if 'POST' in methods:
                    self.write({"message": f"Custom POST handler for {path}", "timestamp": time.time()})
                else:
                    self.set_status(405)
                    self.write({"error": "Method not allowed"})
        
        return CustomHandler
