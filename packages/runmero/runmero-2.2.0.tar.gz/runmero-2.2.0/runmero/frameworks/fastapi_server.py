# حقوق الطبع والنشر محفوظة © 2025 mero - من أرض البرتقال يافا فلسطين

import asyncio
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import threading
import time
import os

class FastAPIServer:
    def __init__(self, 
                 app_name: str = "RunMero FastAPI Server",
                 host: str = "0.0.0.0", 
                 port: int = 8000,
                 debug: bool = False,
                 auto_reload: bool = False):
        
        self.app_name = app_name
        self.host = host
        self.port = port
        self.debug = debug
        self.auto_reload = auto_reload
        
        self.app = FastAPI(
            title=app_name,
            description="خادم FastAPI قوي مدعوم بمكتبة RunMero - صنع في فلسطين",
            version="2.5.0",
            docs_url="/docs" if debug else None,
            redoc_url="/redoc" if debug else None
        )
        
        self._setup_middleware()
        self._setup_routes()
        self._background_tasks = []
        self._running = False
        self._server_thread = None
        
    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        @self.app.middleware("http")
        async def process_time_header(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Powered-By"] = "RunMero FastAPI - فلسطين"
            return response

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return {
                "message": "مرحباً بك في خادم FastAPI المدعوم بـ RunMero",
                "version": "2.5.0",
                "author": "mero",
                "country": "فلسطين الحبيبة",
                "status": "running",
                "uptime": time.time() - getattr(self, '_start_time', time.time())
            }

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "server": self.app_name,
                "process_id": os.getpid()
            }

        @self.app.get("/status")
        async def server_status():
            import psutil
            process = psutil.Process()
            
            return {
                "server_info": {
                    "name": self.app_name,
                    "host": self.host,
                    "port": self.port,
                    "running": self._running
                },
                "system_info": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_info": process.memory_info()._asdict(),
                    "connections": len(process.connections()) if hasattr(process, 'connections') else 0,
                    "threads": process.num_threads()
                },
                "background_tasks": len(self._background_tasks)
            }

        @self.app.post("/background-task")
        async def create_background_task(background_tasks: BackgroundTasks):
            task_id = f"task_{int(time.time())}"
            
            def long_running_task(task_id: str):
                time.sleep(10)
                print(f"انتهت المهمة في الخلفية: {task_id}")
            
            background_tasks.add_task(long_running_task, task_id)
            self._background_tasks.append(task_id)
            
            return {"message": f"تم إنشاء مهمة في الخلفية: {task_id}"}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"تم استلام الرسالة: {data}")
            except Exception as e:
                print(f"خطأ في WebSocket: {e}")

    def add_route(self, path: str, endpoint, methods: List[str] = ["GET"]):
        for method in methods:
            if method.upper() == "GET":
                self.app.get(path)(endpoint)
            elif method.upper() == "POST":
                self.app.post(path)(endpoint)
            elif method.upper() == "PUT":
                self.app.put(path)(endpoint)
            elif method.upper() == "DELETE":
                self.app.delete(path)(endpoint)
            elif method.upper() == "PATCH":
                self.app.patch(path)(endpoint)

    def add_middleware(self, middleware_class, **kwargs):
        self.app.add_middleware(middleware_class, **kwargs)

    def include_router(self, router, prefix: str = "", tags: List[str] = None):
        self.app.include_router(router, prefix=prefix, tags=tags or [])

    def run_in_background(self):
        if self._running:
            return False
        
        def server_worker():
            self._running = True
            self._start_time = time.time()
            
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                reload=self.auto_reload,
                log_level="info" if self.debug else "warning",
                access_log=self.debug
            )
            
            server = uvicorn.Server(config)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(server.serve())
            except Exception as e:
                print(f"خطأ في تشغيل الخادم: {e}")
            finally:
                self._running = False
                loop.close()
        
        self._server_thread = threading.Thread(target=server_worker, daemon=True)
        self._server_thread.start()
        
        time.sleep(2)
        return self._running

    def run_sync(self):
        self._running = True
        self._start_time = time.time()
        
        try:
            uvicorn.run(
                app=self.app,
                host=self.host,
                port=self.port,
                reload=self.auto_reload,
                log_level="info" if self.debug else "warning",
                access_log=self.debug
            )
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

    def get_app(self):
        return self.app

    def add_startup_event(self, func):
        self.app.add_event_handler("startup", func)

    def add_shutdown_event(self, func):
        self.app.add_event_handler("shutdown", func)

    def create_advanced_endpoints(self):
        class ProcessModel(BaseModel):
            name: str
            command: str
            args: Optional[List[str]] = []
            env: Optional[Dict[str, str]] = {}

        @self.app.post("/processes")
        async def create_process(process: ProcessModel):
            return {
                "message": f"تم إنشاء العملية: {process.name}",
                "process": process.dict(),
                "timestamp": time.time()
            }

        @self.app.get("/processes")
        async def list_processes():
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "processes": processes[:20],
                "total": len(processes),
                "timestamp": time.time()
            }

        @self.app.get("/system")
        async def system_info():
            import psutil
            return {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage('/')._asdict(),
                "network": {name: stats._asdict() for name, stats in psutil.net_io_counters(pernic=True).items()},
                "uptime": time.time() - psutil.boot_time()
            }

    def setup_file_server(self, static_path: str = "static"):
        from fastapi.staticfiles import StaticFiles
        
        if os.path.exists(static_path):
            self.app.mount("/static", StaticFiles(directory=static_path), name="static")

    def setup_websocket_manager(self):
        from fastapi import WebSocket, WebSocketDisconnect
        
        class ConnectionManager:
            def __init__(self):
                self.active_connections: List[WebSocket] = []

            async def connect(self, websocket: WebSocket):
                await websocket.accept()
                self.active_connections.append(websocket)

            def disconnect(self, websocket: WebSocket):
                self.active_connections.remove(websocket)

            async def send_personal_message(self, message: str, websocket: WebSocket):
                await websocket.send_text(message)

            async def broadcast(self, message: str):
                for connection in self.active_connections:
                    try:
                        await connection.send_text(message)
                    except:
                        self.disconnect(connection)

        manager = ConnectionManager()

        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: int):
            await manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await manager.send_personal_message(f"رسالة من العميل #{client_id}: {data}", websocket)
                    await manager.broadcast(f"العميل #{client_id} قال: {data}")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                await manager.broadcast(f"العميل #{client_id} قطع الاتصال")

        return manager
