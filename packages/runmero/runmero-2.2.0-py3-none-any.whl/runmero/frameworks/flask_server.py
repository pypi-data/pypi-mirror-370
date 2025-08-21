# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة الخليل الخليل فلسطين

from flask import Flask, request, jsonify, render_template_string, send_file, session
from flask_cors import CORS
import threading
import time
import os
import json
import psutil
from typing import Dict, Any, Optional, Callable
from werkzeug.serving import make_server, WSGIRequestHandler
import logging

class FlaskServer:
    def __init__(self, 
                 app_name: str = "RunMero Flask Server",
                 host: str = "0.0.0.0",
                 port: int = 5000,
                 debug: bool = False,
                 threaded: bool = True):
        
        self.app_name = app_name
        self.host = host
        self.port = port
        self.debug = debug
        self.threaded = threaded
        
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        self.app.config['JSON_AS_ASCII'] = False
        
        CORS(self.app)
        
        self._setup_routes()
        self._running = False
        self._server = None
        self._server_thread = None
        self._start_time = None
        self._request_count = 0
        self._error_count = 0
        
        if not debug:
            logging.getLogger('werkzeug').setLevel(logging.WARNING)

    def _setup_routes(self):
        @self.app.before_request
        def before_request():
            self._request_count += 1

        @self.app.errorhandler(404)
        def not_found(error):
            self._error_count += 1
            return jsonify({
                "error": "الصفحة غير موجودة",
                "status": 404,
                "message": "الرابط المطلوب غير متاح",
                "server": self.app_name
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            self._error_count += 1
            return jsonify({
                "error": "خطأ داخلي في الخادم",
                "status": 500,
                "message": "حدث خطأ غير متوقع",
                "server": self.app_name
            }), 500

        @self.app.route('/')
        def root():
            return jsonify({
                "message": "مرحباً بك في خادم Flask المدعوم بـ RunMero",
                "version": "2.5.0",
                "author": "mero",
                "country": "فلسطين الحبيبة",
                "status": "running",
                "uptime": time.time() - (self._start_time or time.time()),
                "requests_served": self._request_count
            })

        @self.app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "server": self.app_name,
                "process_id": os.getpid(),
                "memory_usage": psutil.Process().memory_info()._asdict()
            })

        @self.app.route('/status')
        def server_status():
            process = psutil.Process()
            
            return jsonify({
                "server_info": {
                    "name": self.app_name,
                    "host": self.host,
                    "port": self.port,
                    "running": self._running,
                    "uptime": time.time() - (self._start_time or time.time()),
                    "requests": self._request_count,
                    "errors": self._error_count
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
                    "pid": os.getpid()
                }
            })

        @self.app.route('/api/processes', methods=['GET', 'POST'])
        def handle_processes():
            if request.method == 'GET':
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                        try:
                            processes.append(proc.info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    return jsonify({
                        "processes": processes[:30],
                        "total": len(processes),
                        "timestamp": time.time()
                    })
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            
            elif request.method == 'POST':
                data = request.get_json()
                if not data:
                    return jsonify({"error": "لا توجد بيانات"}), 400
                
                return jsonify({
                    "message": f"تم إنشاء العملية: {data.get('name', 'unknown')}",
                    "process": data,
                    "timestamp": time.time()
                })

        @self.app.route('/api/system')
        def system_info():
            try:
                return jsonify({
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
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/logs/<int:lines>')
        def get_logs(lines=100):
            log_file = "/tmp/runmero_flask.log"
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        log_lines = f.readlines()[-lines:]
                    return jsonify({
                        "logs": log_lines,
                        "total_lines": len(log_lines),
                        "file": log_file
                    })
                else:
                    return jsonify({
                        "logs": [],
                        "message": "ملف السجل غير موجود"
                    })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/dashboard')
        def dashboard():
            dashboard_html = """
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>لوحة تحكم RunMero Flask</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
                    .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
                    .logs { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .refresh-btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>لوحة تحكم RunMero Flask Server</h1>
                        <p>خادم Flask قوي مدعوم بمكتبة RunMero - صنع في فلسطين الحبيبة</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>الطلبات المخدومة</h3>
                            <div class="stat-value" id="requests">{{ requests }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>الأخطاء</h3>
                            <div class="stat-value" id="errors">{{ errors }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>وقت التشغيل</h3>
                            <div class="stat-value" id="uptime">{{ uptime }} ثانية</div>
                        </div>
                        <div class="stat-card">
                            <h3>استخدام المعالج</h3>
                            <div class="stat-value" id="cpu">{{ cpu }}%</div>
                        </div>
                    </div>
                    
                    <div class="logs">
                        <h3>معلومات النظام</h3>
                        <button class="refresh-btn" onclick="location.reload()">تحديث</button>
                        <pre id="system-info">{{ system_info }}</pre>
                    </div>
                </div>
                
                <script>
                    setInterval(function() {
                        fetch('/status')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('requests').textContent = data.server_info.requests;
                                document.getElementById('errors').textContent = data.server_info.errors;
                                document.getElementById('uptime').textContent = Math.round(data.server_info.uptime);
                                document.getElementById('cpu').textContent = data.system_info.cpu_percent.toFixed(1);
                            });
                    }, 5000);
                </script>
            </body>
            </html>
            """
            
            process = psutil.Process()
            return render_template_string(dashboard_html,
                requests=self._request_count,
                errors=self._error_count,
                uptime=round(time.time() - (self._start_time or time.time())),
                cpu=process.cpu_percent(),
                system_info=json.dumps(psutil.virtual_memory()._asdict(), indent=2, ensure_ascii=False)
            )

    def add_route(self, path: str, endpoint: Callable, methods: list = None):
        if methods is None:
            methods = ['GET']
        
        self.app.route(path, methods=methods)(endpoint)

    def add_before_request(self, func: Callable):
        self.app.before_request(func)

    def add_after_request(self, func: Callable):
        self.app.after_request(func)

    def add_error_handler(self, code: int, handler: Callable):
        self.app.errorhandler(code)(handler)

    def run_in_background(self):
        if self._running:
            return False
        
        def server_worker():
            self._running = True
            self._start_time = time.time()
            
            class QuietHandler(WSGIRequestHandler):
                def log_request(self, code='-', size='-'):
                    if self.server.debug:
                        super().log_request(code, size)
            
            self._server = make_server(
                self.host, 
                self.port, 
                self.app,
                threaded=self.threaded,
                request_handler=QuietHandler
            )
            
            self._server.debug = self.debug
            
            try:
                print(f"Flask server بدأ العمل على {self.host}:{self.port}")
                self._server.serve_forever()
            except Exception as e:
                print(f"خطأ في تشغيل الخادم: {e}")
            finally:
                self._running = False
        
        self._server_thread = threading.Thread(target=server_worker, daemon=True)
        self._server_thread.start()
        
        time.sleep(1)
        return self._running

    def run_sync(self):
        self._running = True
        self._start_time = time.time()
        
        try:
            print(f"Flask server بدأ العمل على {self.host}:{self.port}")
            self.app.run(
                host=self.host,
                port=self.port,
                debug=self.debug,
                threaded=self.threaded,
                use_reloader=False
            )
        except KeyboardInterrupt:
            print("تم إيقاف الخادم بواسطة المستخدم")
        except Exception as e:
            print(f"خطأ في تشغيل الخادم: {e}")
        finally:
            self._running = False

    def stop(self):
        self._running = False
        if self._server:
            self._server.shutdown()
        
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=10)

    def is_running(self) -> bool:
        return self._running

    def get_app(self):
        return self.app

    def get_stats(self) -> Dict[str, Any]:
        return {
            "requests": self._request_count,
            "errors": self._error_count,
            "uptime": time.time() - (self._start_time or time.time()) if self._start_time else 0,
            "running": self._running,
            "host": self.host,
            "port": self.port
        }

    def setup_file_uploads(self, upload_folder: str = "uploads"):
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        self.app.config['UPLOAD_FOLDER'] = upload_folder
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

        @self.app.route('/upload', methods=['GET', 'POST'])
        def upload_file():
            if request.method == 'POST':
                if 'file' not in request.files:
                    return jsonify({"error": "لا يوجد ملف"}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({"error": "لم يتم اختيار ملف"}), 400
                
                if file:
                    filename = os.path.join(upload_folder, file.filename)
                    file.save(filename)
                    return jsonify({
                        "message": "تم رفع الملف بنجاح",
                        "filename": file.filename,
                        "size": os.path.getsize(filename)
                    })
            
            upload_form = """
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <button type="submit">رفع الملف</button>
            </form>
            """
            return upload_form

    def enable_session_management(self):
        @self.app.route('/session/set/<key>/<value>')
        def set_session(key, value):
            session[key] = value
            return jsonify({"message": f"تم حفظ {key} = {value}"})

        @self.app.route('/session/get/<key>')
        def get_session(key):
            value = session.get(key)
            return jsonify({"key": key, "value": value})

        @self.app.route('/session/clear')
        def clear_session():
            session.clear()
            return jsonify({"message": "تم مسح الجلسة"})
