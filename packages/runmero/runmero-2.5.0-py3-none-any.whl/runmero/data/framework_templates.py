# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة نابلس الصامدة فلسطين

from typing import Dict, Any, List

FRAMEWORK_TEMPLATES = {
    'fastapi': {
        'basic_app': '''
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
import os

app = FastAPI(
    title="RunMero FastAPI Application",
    description="تطبيق FastAPI مدعوم بمكتبة RunMero - صنع في فلسطين",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    name: str
    command: str
    args: list = []

@app.get("/")
async def root():
    return {{
        "message": "مرحباً بك في تطبيق RunMero FastAPI",
        "version": "2.5.0",
        "author": "mero",
        "country": "فلسطين الحبيبة",
        "timestamp": time.time()
    }}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": time.time()}}

@app.post("/process")
async def create_process(request: ProcessRequest, background_tasks: BackgroundTasks):
    def run_process():
        # هنا يتم تنفيذ العملية في الخلفية
        time.sleep(5)
        print(f"تم تنفيذ العملية: {{request.name}}")
    
    background_tasks.add_task(run_process)
    return {{"message": f"تم إنشاء العملية: {{request.name}}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        
        'advanced_app': '''
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import time
import os
import psutil

app = FastAPI(
    title="RunMero Advanced FastAPI Server",
    description="خادم FastAPI متقدم مدعوم بمكتبة RunMero",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# Models
class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: float

class ProcessInfo(BaseModel):
    name: str = Field(..., description="اسم العملية")
    command: str = Field(..., description="الأمر المراد تنفيذه")
    args: List[str] = Field(default=[], description="معاملات الأمر")
    environment: Dict[str, str] = Field(default={}, description="متغيرات البيئة")
    priority: int = Field(default=0, description="أولوية العملية")

# Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    return {{
        "message": "RunMero Advanced FastAPI Server",
        "version": "2.5.0",
        "author": "mero",
        "country": "فلسطين الحبيبة",
        "features": ["background_processes", "websockets", "monitoring", "security"],
        "endpoints": ["/docs", "/health", "/system", "/processes", "/ws"],
        "timestamp": time.time()
    }}

@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "uptime": time.time(),
        "pid": os.getpid(),
        "version": "2.5.0"
    }}

@app.get("/system", response_model=SystemStats)
async def get_system_stats():
    return SystemStats(
        cpu_percent=psutil.cpu_percent(interval=1),
        memory_percent=psutil.virtual_memory().percent,
        disk_percent=psutil.disk_usage('/').percent,
        timestamp=time.time()
    )

@app.post("/processes")
async def create_process(process: ProcessInfo, background_tasks: BackgroundTasks):
    def execute_process():
        try:
            # تنفيذ العملية هنا
            time.sleep(2)
            print(f"تم تنفيذ العملية: {{process.name}}")
        except Exception as e:
            print(f"خطأ في تنفيذ العملية: {{e}}")
    
    background_tasks.add_task(execute_process)
    return {{
        "message": f"تم إنشاء العملية: {{process.name}}",
        "process_id": f"proc_{{int(time.time())}}",
        "status": "created"
    }}

@app.get("/stream")
async def stream_data():
    async def generate_data():
        for i in range(100):
            data = {{
                "index": i,
                "timestamp": time.time(),
                "message": f"رسالة رقم {{i+1}}"
            }}
            yield f"data: {{json.dumps(data)}}\\n\\n"
            await asyncio.sleep(0.1)
    
    return StreamingResponse(generate_data(), media_type="text/plain")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"رسالة: {{data}}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
'''
    },
    
    'flask': {
        'basic_app': '''
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import time
import os
import psutil
import threading

app = Flask(__name__)
app.secret_key = 'runmero_flask_secret_palestine_2025'
CORS(app)

@app.route('/')
def index():
    return jsonify({{
        "message": "مرحباً بك في تطبيق RunMero Flask",
        "version": "2.5.0",
        "author": "mero",
        "country": "فلسطين الحبيبة",
        "timestamp": time.time()
    }})

@app.route('/health')
def health():
    return jsonify({{"status": "healthy", "timestamp": time.time()}})

@app.route('/system')
def system_info():
    return jsonify({{
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "pid": os.getpid(),
        "timestamp": time.time()
    }})

@app.route('/process', methods=['POST'])
def create_process():
    data = request.get_json()
    
    def run_background_task():
        # تنفيذ المهمة في الخلفية
        time.sleep(5)
        print(f"تم تنفيذ العملية: {{data.get('name', 'unknown')}}")
    
    thread = threading.Thread(target=run_background_task, daemon=True)
    thread.start()
    
    return jsonify({{
        "message": f"تم إنشاء العملية: {{data.get('name', 'unknown')}}",
        "status": "created"
    }})

@app.route('/dashboard')
def dashboard():
    html_template = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>لوحة تحكم RunMero Flask</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #007bff; color: white; padding: 20px; border-radius: 5px; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; flex: 1; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>لوحة تحكم RunMero Flask</h1>
            <p>خادم Flask مدعوم بمكتبة RunMero - صنع في فلسطين</p>
        </div>
        <div class="stats">
            <div class="stat-card">
                <h3>حالة الخادم</h3>
                <p id="status">جاري التحميل...</p>
            </div>
            <div class="stat-card">
                <h3>معلومات النظام</h3>
                <p id="system">جاري التحميل...</p>
            </div>
        </div>
        <script>
            setInterval(function() {{
                fetch('/health').then(r => r.json()).then(data => {{
                    document.getElementById('status').textContent = 'نشط - ' + new Date().toLocaleString('ar');
                }});
                
                fetch('/system').then(r => r.json()).then(data => {{
                    document.getElementById('system').innerHTML = 
                        'CPU: ' + data.cpu_percent.toFixed(1) + '%<br>' +
                        'Memory: ' + data.memory_percent.toFixed(1) + '%<br>' +
                        'PID: ' + data.pid;
                }});
            }}, 5000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    },
    
    'django': {
        'basic_project': '''
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'runmero-django-secret-key-palestine-2025'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'runmero_project.urls'

TEMPLATES = [{{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {{
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    }},
}}]

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {{
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}}

# urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
import time
import os
import psutil

def api_root(request):
    return JsonResponse({{
        "message": "مرحباً بك في تطبيق RunMero Django",
        "version": "2.5.0",
        "author": "mero",
        "country": "فلسطين الحبيبة",
        "timestamp": time.time()
    }})

def health_check(request):
    return JsonResponse({{"status": "healthy", "timestamp": time.time()}})

def system_info(request):
    return JsonResponse({{
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "pid": os.getpid(),
        "timestamp": time.time()
    }})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health'),
    path('system/', system_info, name='system'),
    path('api/', include('rest_framework.urls')),
]
''',
        
        'models': '''
# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Process(models.Model):
    STATUS_CHOICES = [
        ('created', 'تم الإنشاء'),
        ('running', 'يعمل'),
        ('stopped', 'متوقف'),
        ('failed', 'فشل'),
        ('completed', 'مكتمل'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='اسم العملية')
    command = models.TextField(verbose_name='الأمر')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'عملية'
        verbose_name_plural = 'العمليات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{{self.name}} ({{self.status}})"

class ProcessLog(models.Model):
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'سجل العملية'
        verbose_name_plural = 'سجلات العمليات'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{{self.process.name}} - {{self.level}} - {{self.timestamp}}"

class SystemMetric(models.Model):
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    disk_percent = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مقياس النظام'
        verbose_name_plural = 'مقاييس النظام'
        ordering = ['-timestamp']
'''
    },
    
    'tornado': {
        'basic_app': '''
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import time
import os
import psutil
from typing import List

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("X-Powered-By", "RunMero Tornado - فلسطين")

    def options(self, *args):
        self.set_status(200)
        self.finish()

    def write_json(self, data):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(data, ensure_ascii=False, indent=2))

class MainHandler(BaseHandler):
    def get(self):
        self.write_json({{
            "message": "مرحباً بك في تطبيق RunMero Tornado",
            "version": "2.5.0",
            "author": "mero",
            "country": "فلسطين الحبيبة",
            "timestamp": time.time(),
            "features": ["websockets", "async_processing", "high_performance"]
        }})

class HealthHandler(BaseHandler):
    def get(self):
        self.write_json({{
            "status": "healthy",
            "timestamp": time.time(),
            "pid": os.getpid(),
            "tornado_version": tornado.version
        }})

class SystemHandler(BaseHandler):
    async def get(self):
        system_info = {{
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            "timestamp": time.time()
        }}
        self.write_json(system_info)

class ProcessHandler(BaseHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            process_name = data.get('name', 'unknown')
            
            # هنا يمكن إضافة منطق إنشاء العملية
            response = {{
                "message": f"تم إنشاء العملية: {{process_name}}",
                "process_id": f"proc_{{int(time.time())}}",
                "status": "created",
                "timestamp": time.time()
            }}
            
            self.write_json(response)
        except json.JSONDecodeError:
            self.set_status(400)
            self.write_json({{"error": "بيانات JSON غير صالحة"}})
        except Exception as e:
            self.set_status(500)
            self.write_json({{"error": str(e)}})

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    connections: List['WebSocketHandler'] = []
    
    def check_origin(self, origin):
        return True
    
    def open(self):
        self.connections.append(self)
        self.write_message(json.dumps({{
            "type": "connection",
            "message": "مرحباً بك في WebSocket الخاص بـ RunMero",
            "timestamp": time.time()
        }}))
    
    def on_message(self, message):
        try:
            data = json.loads(message)
            response = {{
                "type": "echo",
                "message": f"تم استلام الرسالة: {{data.get('message', message)}}",
                "timestamp": time.time()
            }}
            self.write_message(json.dumps(response))
            
            # إرسال للجميع
            for connection in self.connections:
                if connection != self:
                    try:
                        connection.write_message(json.dumps({{
                            "type": "broadcast",
                            "message": f"رسالة من مستخدم آخر: {{data.get('message', message)}}",
                            "timestamp": time.time()
                        }}))
                    except:
                        pass
                        
        except json.JSONDecodeError:
            self.write_message(json.dumps({{
                "type": "error",
                "message": "رسالة JSON غير صالحة",
                "timestamp": time.time()
            }}))
    
    def on_close(self):
        if self in self.connections:
            self.connections.remove(self)

class DashboardHandler(BaseHandler):
    def get(self):
        dashboard_html = """
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>لوحة تحكم RunMero Tornado</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                         gap: 20px; margin-bottom: 20px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; 
                             box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .websocket-section {{ background: white; padding: 20px; border-radius: 10px; }}
                #messages {{ height: 200px; overflow-y: auto; border: 1px solid #ddd; 
                            padding: 10px; margin: 10px 0; background: #f8f9fa; }}
                button {{ background: #667eea; color: white; border: none; padding: 10px 20px; 
                         border-radius: 5px; cursor: pointer; margin: 5px; }}
                input {{ padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>لوحة تحكم RunMero Tornado Server</h1>
                    <p>خادم Tornado عالي الأداء مدعوم بمكتبة RunMero - صنع في فلسطين 🇵🇸</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>حالة الخادم</h3>
                        <p id="server-status">جاري التحميل...</p>
                    </div>
                    <div class="stat-card">
                        <h3>معلومات النظام</h3>
                        <p id="system-info">جاري التحميل...</p>
                    </div>
                    <div class="stat-card">
                        <h3>اتصالات WebSocket</h3>
                        <p id="ws-status">غير متصل</p>
                    </div>
                </div>
                
                <div class="websocket-section">
                    <h3>WebSocket Testing</h3>
                    <button onclick="connectWS()">اتصال</button>
                    <button onclick="disconnectWS()">قطع الاتصال</button>
                    <br>
                    <input type="text" id="messageInput" placeholder="اكتب رسالة...">
                    <button onclick="sendMessage()">إرسال</button>
                    <div id="messages"></div>
                </div>
            </div>
            
            <script>
                let ws = null;
                
                function updateStats() {{
                    fetch('/health').then(r => r.json()).then(data => {{
                        document.getElementById('server-status').innerHTML = 
                            `✅ نشط<br>PID: ${{data.pid}}<br>Tornado: ${{data.tornado_version}}`;
                    }});
                    
                    fetch('/system').then(r => r.json()).then(data => {{
                        document.getElementById('system-info').innerHTML = 
                            `CPU: ${{data.cpu_percent.toFixed(1)}}%<br>` +
                            `Memory: ${{data.memory_percent.toFixed(1)}}%<br>` +
                            `Disk: ${{data.disk_percent.toFixed(1)}}%`;
                    }});
                }}
                
                function connectWS() {{
                    ws = new WebSocket('ws://localhost:8888/ws');
                    
                    ws.onopen = function() {{
                        document.getElementById('ws-status').textContent = '🟢 متصل';
                        addMessage('تم الاتصال بـ WebSocket');
                    }};
                    
                    ws.onmessage = function(event) {{
                        const data = JSON.parse(event.data);
                        addMessage(`${{data.type}}: ${{data.message}}`);
                    }};
                    
                    ws.onclose = function() {{
                        document.getElementById('ws-status').textContent = '🔴 منقطع';
                        addMessage('تم قطع الاتصال');
                    }};
                }}
                
                function disconnectWS() {{
                    if (ws) {{
                        ws.close();
                    }}
                }}
                
                function sendMessage() {{
                    const input = document.getElementById('messageInput');
                    if (ws && input.value) {{
                        ws.send(JSON.stringify({{message: input.value}}));
                        input.value = '';
                    }}
                }}
                
                function addMessage(message) {{
                    const messages = document.getElementById('messages');
                    const time = new Date().toLocaleTimeString('ar');
                    messages.innerHTML += `<div>[${{time}}] ${{message}}</div>`;
                    messages.scrollTop = messages.scrollHeight;
                }}
                
                updateStats();
                setInterval(updateStats, 5000);
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        sendMessage();
                    }}
                }});
            </script>
        </body>
        </html>
        """
        self.write(dashboard_html)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/health", HealthHandler),
        (r"/system", SystemHandler),
        (r"/process", ProcessHandler),
        (r"/ws", WebSocketHandler),
        (r"/dashboard", DashboardHandler),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888, address="0.0.0.0")
    print("Tornado server بدأ العمل على http://0.0.0.0:8888")
    tornado.ioloop.IOLoop.current().start()
'''
    }
}

MIDDLEWARE_TEMPLATES = {
    'cors_middleware': '''
class CORSMiddleware:
    def __init__(self, app, allow_origins=None, allow_methods=None, allow_headers=None):
        self.app = app
        self.allow_origins = allow_origins or ['*']
        self.allow_methods = allow_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allow_headers = allow_headers or ['Content-Type', 'Authorization']
    
    def __call__(self, environ, start_response):
        def new_start_response(status, response_headers):
            response_headers.extend([
                ('Access-Control-Allow-Origin', ', '.join(self.allow_origins)),
                ('Access-Control-Allow-Methods', ', '.join(self.allow_methods)),
                ('Access-Control-Allow-Headers', ', '.join(self.allow_headers)),
                ('Access-Control-Allow-Credentials', 'true'),
            ])
            return start_response(status, response_headers)
        
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', ', '.join(self.allow_origins)),
                ('Access-Control-Allow-Methods', ', '.join(self.allow_methods)),
                ('Access-Control-Allow-Headers', ', '.join(self.allow_headers)),
            ])
            return [b'']
        
        return self.app(environ, new_start_response)
''',
    
    'auth_middleware': '''
import jwt
from functools import wraps

class AuthMiddleware:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({{'error': 'Invalid token format'}}), 401
            
            if not token:
                return jsonify({{'error': 'Token missing'}}), 401
            
            payload = self.verify_token(token)
            if payload is None:
                return jsonify({{'error': 'Invalid or expired token'}}), 401
            
            return f(payload, *args, **kwargs)
        
        return decorated_function
''',
    
    'logging_middleware': '''
import logging
import time
from datetime import datetime

class LoggingMiddleware:
    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger or logging.getLogger('runmero.middleware')
        
        handler = logging.FileHandler('/tmp/runmero_middleware.log')
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        method = environ.get('REQUEST_METHOD', '')
        path = environ.get('PATH_INFO', '')
        remote_addr = environ.get('REMOTE_ADDR', '')
        user_agent = environ.get('HTTP_USER_AGENT', '')
        
        self.logger.info(f"Request started: {{method}} {{path}} from {{remote_addr}}")
        
        def logged_start_response(status, response_headers):
            duration = (time.time() - start_time) * 1000
            self.logger.info(f"Request completed: {{method}} {{path}} - {{status}} - {{duration:.2f}}ms")
            return start_response(status, response_headers)
        
        try:
            return self.app(environ, logged_start_response)
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(f"Request failed: {{method}} {{path}} - {{str(e)}} - {{duration:.2f}}ms")
            raise
''',
    
    'rate_limit_middleware': '''
import time
from collections import defaultdict

class RateLimitMiddleware:
    def __init__(self, app, max_requests=100, window_seconds=3600):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, client_ip):
        now = time.time()
        window_start = now - self.window_seconds
        
        # تنظيف الطلبات القديمة
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        # فحص الحد الأقصى
        if len(self.requests[client_ip]) >= self.max_requests:
            return True
        
        # تسجيل الطلب الحالي
        self.requests[client_ip].append(now)
        return False
    
    def __call__(self, environ, start_response):
        client_ip = environ.get('REMOTE_ADDR', '127.0.0.1')
        
        if self.is_rate_limited(client_ip):
            start_response('429 Too Many Requests', [
                ('Content-Type', 'application/json'),
                ('Retry-After', str(self.window_seconds))
            ])
            return [b'{"error": "Rate limit exceeded"}']
        
        return self.app(environ, start_response)
'''
}

ROUTING_TEMPLATES = {
    'fastapi_routes': '''
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import time

router = APIRouter(prefix="/api/v1", tags=["runmero"])

class ProcessRequest(BaseModel):
    name: str
    command: str
    args: List[str] = []
    environment: dict = {}

class ProcessResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: float

@router.get("/processes", response_model=List[ProcessResponse])
async def list_processes():
    # هنا يتم جلب قائمة العمليات
    return []

@router.post("/processes", response_model=ProcessResponse)
async def create_process(request: ProcessRequest, background_tasks: BackgroundTasks):
    process_id = f"proc_{{int(time.time())}}"
    
    def run_process():
        # تنفيذ العملية في الخلفية
        time.sleep(2)
        print(f"Process {{request.name}} executed")
    
    background_tasks.add_task(run_process)
    
    return ProcessResponse(
        id=process_id,
        name=request.name,
        status="created",
        created_at=time.time()
    )

@router.get("/processes/{{process_id}}", response_model=ProcessResponse)
async def get_process(process_id: str):
    # هنا يتم جلب تفاصيل العملية
    return ProcessResponse(
        id=process_id,
        name="Sample Process",
        status="running",
        created_at=time.time()
    )

@router.delete("/processes/{{process_id}}")
async def delete_process(process_id: str):
    # هنا يتم حذف العملية
    return {{"message": f"Process {{process_id}} deleted"}}
''',
    
    'flask_blueprints': '''
from flask import Blueprint, request, jsonify
import time

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/processes', methods=['GET'])
def list_processes():
    # هنا يتم جلب قائمة العمليات
    return jsonify([])

@api_bp.route('/processes', methods=['POST'])
def create_process():
    data = request.get_json()
    process_id = f"proc_{{int(time.time())}}"
    
    # هنا يتم إنشاء العملية
    
    return jsonify({{
        "id": process_id,
        "name": data.get('name'),
        "status": "created",
        "created_at": time.time()
    }})

@api_bp.route('/processes/<process_id>', methods=['GET'])
def get_process(process_id):
    # هنا يتم جلب تفاصيل العملية
    return jsonify({{
        "id": process_id,
        "name": "Sample Process",
        "status": "running",
        "created_at": time.time()
    }})

@api_bp.route('/processes/<process_id>', methods=['DELETE'])
def delete_process(process_id):
    # هنا يتم حذف العملية
    return jsonify({{"message": f"Process {{process_id}} deleted"}})

# Blueprint للمراقبة
monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')

@monitor_bp.route('/health')
def health_check():
    return jsonify({{"status": "healthy", "timestamp": time.time()}})

@monitor_bp.route('/metrics')
def metrics():
    # هنا يتم جمع المقاييس
    return jsonify({{
        "requests_total": 100,
        "response_time_avg": 150.5,
        "memory_usage": 64.2,
        "timestamp": time.time()
    }})
'''
}

def get_framework_template(framework: str, template_type: str = 'basic_app') -> str:
    if framework not in FRAMEWORK_TEMPLATES:
        raise ValueError(f"Framework '{framework}' not supported")
    
    if template_type not in FRAMEWORK_TEMPLATES[framework]:
        available_templates = list(FRAMEWORK_TEMPLATES[framework].keys())
        raise ValueError(f"Template '{template_type}' not found. Available templates: {available_templates}")
    
    return FRAMEWORK_TEMPLATES[framework][template_type]

def get_middleware_template(middleware_name: str) -> str:
    if middleware_name not in MIDDLEWARE_TEMPLATES:
        available_middleware = list(MIDDLEWARE_TEMPLATES.keys())
        raise ValueError(f"Middleware '{middleware_name}' not found. Available middleware: {available_middleware}")
    
    return MIDDLEWARE_TEMPLATES[middleware_name]

def get_routing_template(framework: str) -> str:
    template_name = f"{framework}_routes" if f"{framework}_routes" in ROUTING_TEMPLATES else f"{framework}_blueprints"
    
    if template_name not in ROUTING_TEMPLATES:
        available_templates = list(ROUTING_TEMPLATES.keys())
        raise ValueError(f"Routing template for '{framework}' not found. Available templates: {available_templates}")
    
    return ROUTING_TEMPLATES[template_name]

