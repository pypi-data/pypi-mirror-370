# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة رام الله فلسطين

import os
import sys
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponse
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.core.management import execute_from_command_line
from django.core.servers.basehttp import get_internal_wsgi_application
import threading
import time
import json
import psutil
from typing import Dict, Any, List, Optional

class DjangoServer:
    def __init__(self, 
                 app_name: str = "RunMero Django Server",
                 host: str = "0.0.0.0",
                 port: int = 8000,
                 debug: bool = False,
                 auto_reload: bool = False):
        
        self.app_name = app_name
        self.host = host
        self.port = port
        self.debug = debug
        self.auto_reload = auto_reload
        
        self._running = False
        self._server_thread = None
        self._start_time = None
        self._request_count = 0
        
        self._setup_django()
        self._setup_urls()

    def _setup_django(self):
        if not settings.configured:
            settings.configure(
                DEBUG=self.debug,
                SECRET_KEY='runmero-django-server-palestine-mero-2025',
                ALLOWED_HOSTS=['*'],
                ROOT_URLCONF=__name__,
                INSTALLED_APPS=[
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.messages',
                    'django.contrib.staticfiles',
                ],
                MIDDLEWARE=[
                    'django.middleware.security.SecurityMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.middleware.common.CommonMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                    'django.middleware.clickjacking.XFrameOptionsMiddleware',
                ],
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                USE_TZ=True,
                USE_I18N=True,
                LANGUAGE_CODE='ar',
                TIME_ZONE='Asia/Jerusalem',
                STATIC_URL='/static/',
                TEMPLATES=[
                    {
                        'BACKEND': 'django.template.backends.django.DjangoTemplates',
                        'DIRS': [],
                        'APP_DIRS': True,
                        'OPTIONS': {
                            'context_processors': [
                                'django.template.context_processors.debug',
                                'django.template.context_processors.request',
                                'django.contrib.messages.context_processors.messages',
                            ],
                        },
                    },
                ],
            )
            
            django.setup()

    def _setup_urls(self):
        def home_view(request):
            self._request_count += 1
            return JsonResponse({
                "message": "مرحباً بك في خادم Django المدعوم بـ RunMero",
                "version": "2.5.0", 
                "author": "mero",
                "country": "فلسطين الحبيبة",
                "status": "running",
                "uptime": time.time() - (self._start_time or time.time()),
                "requests_served": self._request_count,
                "framework": "Django",
                "server": self.app_name
            }, json_dumps_params={'ensure_ascii': False})

        def health_view(request):
            return JsonResponse({
                "status": "healthy",
                "timestamp": time.time(),
                "server": self.app_name,
                "process_id": os.getpid(),
                "django_version": django.get_version()
            }, json_dumps_params={'ensure_ascii': False})

        def status_view(request):
            process = psutil.Process()
            
            return JsonResponse({
                "server_info": {
                    "name": self.app_name,
                    "host": self.host,
                    "port": self.port,
                    "running": self._running,
                    "uptime": time.time() - (self._start_time or time.time()) if self._start_time else 0,
                    "requests": self._request_count,
                    "django_version": django.get_version()
                },
                "system_info": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_info": process.memory_info()._asdict(),
                    "threads": process.num_threads(),
                    "connections": len(process.connections()) if hasattr(process, 'connections') else 0
                },
                "environment": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "platform": os.name,
                    "pid": os.getpid()
                }
            }, json_dumps_params={'ensure_ascii': False})

        @csrf_exempt
        def processes_view(request):
            if request.method == 'GET':
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                        try:
                            processes.append(proc.info)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    return JsonResponse({
                        "processes": processes[:30],
                        "total": len(processes),
                        "timestamp": time.time()
                    }, json_dumps_params={'ensure_ascii': False})
                    
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500, json_dumps_params={'ensure_ascii': False})
            
            elif request.method == 'POST':
                try:
                    data = json.loads(request.body)
                    return JsonResponse({
                        "message": f"تم إنشاء العملية: {data.get('name', 'unknown')}",
                        "process": data,
                        "timestamp": time.time()
                    }, json_dumps_params={'ensure_ascii': False})
                except json.JSONDecodeError:
                    return JsonResponse({"error": "بيانات JSON غير صالحة"}, status=400, json_dumps_params={'ensure_ascii': False})

        def system_view(request):
            try:
                return JsonResponse({
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
                }, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500, json_dumps_params={'ensure_ascii': False})

        def dashboard_view(request):
            dashboard_html = """
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>لوحة تحكم RunMero Django</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        margin: 0; padding: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { 
                        background: rgba(255,255,255,0.95); 
                        color: #333; padding: 30px; 
                        border-radius: 15px; 
                        margin-bottom: 30px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        backdrop-filter: blur(10px);
                    }
                    .stats { 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                        gap: 20px; margin-bottom: 30px; 
                    }
                    .stat-card { 
                        background: rgba(255,255,255,0.95); 
                        padding: 25px; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        backdrop-filter: blur(10px);
                        transition: transform 0.3s ease;
                    }
                    .stat-card:hover { transform: translateY(-5px); }
                    .stat-value { 
                        font-size: 2.5em; font-weight: bold; 
                        color: #667eea; margin: 10px 0;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    }
                    .stat-label { color: #666; font-size: 0.9em; }
                    .info-section { 
                        background: rgba(255,255,255,0.95); 
                        padding: 25px; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        backdrop-filter: blur(10px);
                    }
                    .refresh-btn { 
                        background: linear-gradient(45deg, #667eea, #764ba2); 
                        color: white; border: none; 
                        padding: 12px 24px; border-radius: 25px; 
                        cursor: pointer; font-weight: bold;
                        transition: all 0.3s ease;
                    }
                    .refresh-btn:hover { 
                        transform: scale(1.05); 
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    }
                    h1 { margin: 0; font-size: 2.5em; }
                    h2 { color: #667eea; }
                    pre { 
                        background: #f8f9fa; padding: 15px; 
                        border-radius: 10px; overflow-x: auto;
                        border-left: 4px solid #667eea;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 لوحة تحكم RunMero Django Server</h1>
                        <p>خادم Django قوي مدعوم بمكتبة RunMero - صنع بحب في فلسطين الحبيبة 🇵🇸</p>
                        <small>Django Version: """ + django.get_version() + """</small>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-label">الطلبات المخدومة</div>
                            <div class="stat-value" id="requests">""" + str(self._request_count) + """</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">وقت التشغيل (ثانية)</div>
                            <div class="stat-value" id="uptime">""" + str(int(time.time() - (self._start_time or time.time()))) + """</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">معرف العملية</div>
                            <div class="stat-value">""" + str(os.getpid()) + """</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">حالة الخادم</div>
                            <div class="stat-value" style="color: #28a745;">✅ نشط</div>
                        </div>
                    </div>
                    
                    <div class="info-section">
                        <h2>معلومات النظام</h2>
                        <button class="refresh-btn" onclick="location.reload()">🔄 تحديث</button>
                        <pre id="system-info">معلومات النظام جاري التحميل...</pre>
                    </div>
                </div>
                
                <script>
                    function updateStats() {
                        fetch('/status')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('requests').textContent = data.server_info.requests;
                                document.getElementById('uptime').textContent = Math.round(data.server_info.uptime);
                            })
                            .catch(error => console.error('خطأ في جلب البيانات:', error));
                    }
                    
                    function loadSystemInfo() {
                        fetch('/api/system')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('system-info').textContent = JSON.stringify(data, null, 2);
                            })
                            .catch(error => {
                                document.getElementById('system-info').textContent = 'خطأ في تحميل معلومات النظام: ' + error.message;
                            });
                    }
                    
                    updateStats();
                    loadSystemInfo();
                    setInterval(updateStats, 5000);
                </script>
            </body>
            </html>
            """
            return HttpResponse(dashboard_html, content_type='text/html; charset=utf-8')

        self.urlpatterns = [
            path('', home_view, name='home'),
            path('health', health_view, name='health'),
            path('status', status_view, name='status'),
            path('api/processes', processes_view, name='processes'),
            path('api/system', system_view, name='system'),
            path('dashboard', dashboard_view, name='dashboard'),
        ]

    def add_url(self, pattern: str, view_func, name: str = None):
        self.urlpatterns.append(path(pattern, view_func, name=name))

    def run_in_background(self):
        if self._running:
            return False
        
        def server_worker():
            self._running = True
            self._start_time = time.time()
            
            try:
                from django.core.management.commands.runserver import Command as RunServerCommand
                from django.core.management.base import BaseCommand
                
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
                
                cmd = RunServerCommand()
                cmd.stdout = open(os.devnull, 'w') if not self.debug else sys.stdout
                cmd.stderr = open(os.devnull, 'w') if not self.debug else sys.stderr
                
                options = {
                    'addrport': f'{self.host}:{self.port}',
                    'verbosity': 1 if self.debug else 0,
                    'use_reloader': self.auto_reload,
                    'use_threading': True,
                    'use_static_handler': True,
                    'insecure_serving': True
                }
                
                print(f"Django server بدأ العمل على {self.host}:{self.port}")
                cmd.handle(**options)
                
            except Exception as e:
                print(f"خطأ في تشغيل خادم Django: {e}")
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
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
            
            from django.core.management import execute_from_command_line
            
            argv = [
                'manage.py',
                'runserver',
                f'{self.host}:{self.port}',
            ]
            
            if not self.debug:
                argv.append('--noreload')
            
            print(f"Django server بدأ العمل على {self.host}:{self.port}")
            execute_from_command_line(argv)
            
        except KeyboardInterrupt:
            print("تم إيقاف الخادم بواسطة المستخدم")
        except Exception as e:
            print(f"خطأ في تشغيل الخادم: {e}")
        finally:
            self._running = False

    def stop(self):
        self._running = False
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=10)

    def is_running(self) -> bool:
        return self._running

    def get_stats(self) -> Dict[str, Any]:
        return {
            "requests": self._request_count,
            "uptime": time.time() - (self._start_time or time.time()) if self._start_time else 0,
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "django_version": django.get_version()
        }

    def create_management_commands(self):
        from django.core.management.base import BaseCommand
        
        class RunMeroCommand(BaseCommand):
            help = 'أوامر إدارة خاصة بـ RunMero Django Server'
            
            def add_arguments(self, parser):
                parser.add_argument('--status', action='store_true', help='عرض حالة الخادم')
                parser.add_argument('--processes', action='store_true', help='عرض العمليات النشطة')
                parser.add_argument('--system', action='store_true', help='معلومات النظام')
            
            def handle(self, *args, **options):
                if options['status']:
                    self.stdout.write(f"خادم Django يعمل على {self.host}:{self.port}")
                    self.stdout.write(f"عدد الطلبات: {self._request_count}")
                    self.stdout.write(f"وقت التشغيل: {int(time.time() - (self._start_time or time.time()))} ثانية")
                
                elif options['processes']:
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            self.stdout.write(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                elif options['system']:
                    self.stdout.write(f"CPU: {psutil.cpu_percent()}%")
                    self.stdout.write(f"Memory: {psutil.virtual_memory().percent}%")
                    self.stdout.write(f"Disk: {psutil.disk_usage('/').percent}%")
        
        return RunMeroCommand

urlpatterns = []
