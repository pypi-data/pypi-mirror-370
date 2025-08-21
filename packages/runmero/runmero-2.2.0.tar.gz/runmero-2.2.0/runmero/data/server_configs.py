# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة الخليل الخليل فلسطين

from typing import Dict, Any, List

DEFAULT_PORTS = {
    'fastapi': 8000,
    'flask': 5000,
    'django': 8000,
    'tornado': 8888,
    'websocket': 8080,
    'monitoring': 9090,
    'health_check': 9000,
    'metrics': 9100
}

SERVER_CONFIGS = {
    'fastapi': {
        'server_class': 'FastAPIServer',
        'default_config': {
            'host': '0.0.0.0',
            'port': 8000,
            'debug': False,
            'auto_reload': False,
            'workers': 1,
            'log_level': 'info',
            'access_log': True,
            'keep_alive': 2,
            'max_requests': 1000,
            'max_requests_jitter': 50,
            'preload_app': True,
            'timeout': 30,
            'graceful_timeout': 30,
            'client_timeout': 30,
            'body_timeout': 30,
            'header_timeout': 30
        },
        'production_config': {
            'workers': 4,
            'worker_class': 'uvicorn.workers.UvicornWorker',
            'worker_connections': 1000,
            'max_requests': 10000,
            'max_requests_jitter': 1000,
            'preload_app': True,
            'keepalive': 5,
            'timeout': 120,
            'graceful_timeout': 120,
            'log_level': 'warning',
            'access_log': False
        },
        'termux_optimized': {
            'workers': 2,
            'max_requests': 500,
            'timeout': 60,
            'keepalive': 2,
            'worker_tmp_dir': '/data/data/com.termux/files/usr/tmp',
            'bind_unix_socket': '/tmp/runmero_fastapi.sock',
            'enable_memory_optimization': True,
            'cpu_affinity': [0, 1],
            'process_priority': -5
        },
        'middleware_stack': [
            'fastapi.middleware.cors.CORSMiddleware',
            'fastapi.middleware.gzip.GZipMiddleware',
            'fastapi.middleware.trustedhost.TrustedHostMiddleware'
        ],
        'extensions': [
            'fastapi.security',
            'fastapi.background',
            'fastapi.websockets',
            'fastapi.staticfiles'
        ]
    },
    
    'flask': {
        'server_class': 'FlaskServer',
        'default_config': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False,
            'threaded': True,
            'processes': 1,
            'passthrough_errors': False,
            'use_reloader': False,
            'use_debugger': False,
            'use_evalex': True,
            'extra_files': None,
            'reloader_interval': 1,
            'reloader_type': 'auto',
            'threaded_requests': True
        },
        'production_config': {
            'processes': 4,
            'threaded': True,
            'use_reloader': False,
            'use_debugger': False,
            'passthrough_errors': True,
            'request_handler': 'werkzeug.serving.WSGIRequestHandler'
        },
        'termux_optimized': {
            'processes': 2,
            'threaded': True,
            'request_timeout': 60,
            'max_content_length': 16 * 1024 * 1024,
            'tmp_dir': '/data/data/com.termux/files/usr/tmp',
            'instance_path': '/data/data/com.termux/files/usr/var/flask',
            'static_folder': 'static',
            'template_folder': 'templates'
        },
        'flask_extensions': [
            'Flask-CORS',
            'Flask-Compress',
            'Flask-Session',
            'Flask-Caching',
            'Flask-Limiter'
        ],
        'wsgi_config': {
            'application': 'app:app',
            'bind': '0.0.0.0:5000',
            'workers': 2,
            'worker_class': 'sync',
            'timeout': 30,
            'max_requests': 1000,
            'preload_app': True
        }
    },
    
    'django': {
        'server_class': 'DjangoServer',
        'default_config': {
            'host': '0.0.0.0',
            'port': 8000,
            'debug': False,
            'auto_reload': False,
            'verbosity': 1,
            'use_threading': True,
            'use_static_handler': True,
            'insecure_serving': False,
            'ipv6': False,
            'shutdown_message': 'Server stopped'
        },
        'production_config': {
            'debug': False,
            'allowed_hosts': ['*'],
            'secure_ssl_redirect': True,
            'secure_proxy_ssl_header': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'session_cookie_secure': True,
            'csrf_cookie_secure': True,
            'secure_browser_xss_filter': True,
            'secure_content_type_nosniff': True,
            'x_frame_options': 'DENY'
        },
        'termux_optimized': {
            'database': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/data/data/com.termux/files/usr/var/lib/runmero/db.sqlite3',
                'OPTIONS': {
                    'timeout': 30,
                }
            },
            'static_root': '/data/data/com.termux/files/usr/var/lib/runmero/static',
            'media_root': '/data/data/com.termux/files/usr/var/lib/runmero/media',
            'file_upload_temp_dir': '/data/data/com.termux/files/usr/tmp',
            'cache': {
                'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
                'LOCATION': '/data/data/com.termux/files/usr/var/cache/django',
            }
        },
        'installed_apps': [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'corsheaders',
            'rest_framework'
        ],
        'middleware': [
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware'
        ]
    },
    
    'tornado': {
        'server_class': 'TornadoServer',
        'default_config': {
            'host': '0.0.0.0',
            'port': 8888,
            'debug': False,
            'auto_reload': False,
            'max_workers': 4,
            'compress_response': True,
            'cookie_secret': None,
            'login_url': None,
            'xsrf_cookies': True,
            'xsrf_cookie_kwargs': {},
            'static_path': None,
            'static_url_prefix': '/static/',
            'static_handler_class': 'tornado.web.StaticFileHandler'
        },
        'production_config': {
            'max_workers': 8,
            'compress_response': True,
            'xsrf_cookies': True,
            'cookie_secret': 'generate_random_secret',
            'serve_traceback': False,
            'log_function': 'custom_log_function',
            'default_handler_class': 'tornado.web.ErrorHandler'
        },
        'termux_optimized': {
            'max_workers': 2,
            'max_buffer_size': 1048576,
            'max_body_size': 1048576,
            'chunk_size': 65536,
            'decompress_request': True,
            'tcp_nodelay': True,
            'keep_alive_timeout': 30,
            'body_timeout': 30,
            'header_timeout': 30
        },
        'websocket_config': {
            'websocket_ping_interval': 30,
            'websocket_ping_timeout': 10,
            'websocket_max_message_size': 10 * 1024 * 1024,
            'websocket_compression_options': {
                'compression_level': 6,
                'mem_level': 5
            }
        },
        'handlers': [
            ('/', 'MainHandler'),
            ('/api/.*', 'APIHandler'),
            ('/ws', 'WebSocketHandler'),
            ('/static/(.*)', 'tornado.web.StaticFileHandler')
        ]
    }
}

SECURITY_CONFIGS = {
    'ssl_config': {
        'enabled': False,
        'cert_file': '/etc/ssl/certs/server.crt',
        'key_file': '/etc/ssl/private/server.key',
        'ca_file': '/etc/ssl/certs/ca.crt',
        'ssl_options': {
            'ssl_version': 'PROTOCOL_TLSv1_2',
            'ciphers': 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS',
            'cert_reqs': 'CERT_NONE',
            'check_hostname': False
        }
    },
    
    'authentication': {
        'jwt_secret': 'runmero_jwt_secret_palestine_2025',
        'jwt_algorithm': 'HS256',
        'jwt_expiration': 3600,
        'refresh_token_expiration': 86400,
        'password_hash_algorithm': 'bcrypt',
        'password_rounds': 12,
        'session_timeout': 1800,
        'max_login_attempts': 5,
        'lockout_duration': 300
    },
    
    'cors_config': {
        'allow_origins': ['*'],
        'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'allow_credentials': True,
        'max_age': 86400,
        'expose_headers': ['X-Total-Count', 'X-Page-Count']
    },
    
    'rate_limiting': {
        'enabled': True,
        'default_rate': '1000/hour',
        'per_endpoint_rates': {
            '/api/auth/login': '5/minute',
            '/api/auth/register': '3/minute',
            '/api/upload': '10/minute',
            '/api/search': '100/minute'
        },
        'storage_uri': 'memory://',
        'strategy': 'moving-window',
        'headers_enabled': True,
        'header_retry_after': 'Retry-After',
        'header_limit': 'X-RateLimit-Limit',
        'header_remaining': 'X-RateLimit-Remaining',
        'header_reset': 'X-RateLimit-Reset'
    },
    
    'security_headers': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'X-Permitted-Cross-Domain-Policies': 'none'
    }
}

MONITORING_CONFIGS = {
    'health_check': {
        'enabled': True,
        'endpoint': '/health',
        'interval': 30,
        'timeout': 10,
        'checks': [
            'database_connection',
            'memory_usage',
            'disk_space',
            'response_time'
        ],
        'thresholds': {
            'memory_usage': 80,
            'disk_space': 90,
            'response_time': 1000,
            'error_rate': 5
        }
    },
    
    'metrics': {
        'enabled': True,
        'endpoint': '/metrics',
        'format': 'prometheus',
        'collection_interval': 10,
        'metrics': [
            'requests_total',
            'requests_duration_seconds',
            'memory_usage_bytes',
            'cpu_usage_percent',
            'active_connections',
            'error_rate'
        ],
        'labels': ['method', 'endpoint', 'status_code']
    },
    
    'logging': {
        'level': 'INFO',
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        'file_path': '/tmp/runmero_server.log',
        'max_file_size': '10MB',
        'backup_count': 5,
        'rotation': 'time',
        'when': 'midnight',
        'interval': 1,
        'structured_logging': True,
        'json_format': False
    }
}

PERFORMANCE_CONFIGS = {
    'caching': {
        'enabled': True,
        'backend': 'memory',
        'redis_config': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'connection_pool_max_connections': 50
        },
        'memory_config': {
            'max_size': 128 * 1024 * 1024,
            'eviction_policy': 'lru',
            'ttl_default': 3600
        },
        'cache_keys': {
            'user_sessions': 1800,
            'api_responses': 300,
            'database_queries': 600,
            'static_content': 86400
        }
    },
    
    'compression': {
        'enabled': True,
        'algorithm': 'gzip',
        'level': 6,
        'minimum_size': 1024,
        'mime_types': [
            'text/plain',
            'text/html',
            'text/css',
            'text/javascript',
            'application/json',
            'application/xml',
            'application/javascript'
        ]
    },
    
    'connection_pooling': {
        'enabled': True,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'echo': False
    }
}

TERMUX_SPECIFIC_CONFIGS = {
    'paths': {
        'data_dir': '/data/data/com.termux/files/usr/var/lib/runmero',
        'log_dir': '/data/data/com.termux/files/usr/var/log/runmero',
        'cache_dir': '/data/data/com.termux/files/usr/var/cache/runmero',
        'tmp_dir': '/data/data/com.termux/files/usr/tmp',
        'socket_dir': '/data/data/com.termux/files/usr/tmp/sockets',
        'pid_dir': '/data/data/com.termux/files/usr/var/run'
    },
    
    'permissions': {
        'file_mode': 0o644,
        'dir_mode': 0o755,
        'executable_mode': 0o755,
        'socket_mode': 0o666
    },
    
    'resource_limits': {
        'max_memory': '512MB',
        'max_cpu_percent': 80,
        'max_file_descriptors': 1024,
        'max_processes': 10,
        'max_threads_per_process': 20,
        'max_open_files': 256,
        'max_network_connections': 100
    },
    
    'optimization': {
        'cpu_affinity': [0],
        'process_priority': -5,
        'io_priority': 4,
        'scheduler_policy': 'SCHED_OTHER',
        'memory_oom_score': -100,
        'swappiness': 10,
        'tcp_keepalive_time': 600,
        'tcp_keepalive_intvl': 60,
        'tcp_keepalive_probes': 9
    },
    
    'android_specific': {
        'wakelock_enabled': True,
        'wakelock_tag': 'runmero_server',
        'foreground_service': True,
        'notification_channel': 'runmero_background',
        'doze_whitelist': True,
        'battery_optimization_disabled': True,
        'background_restrictions_ignored': True
    }
}

def get_server_config(server_type: str, environment: str = 'default') -> Dict[str, Any]:
    if server_type not in SERVER_CONFIGS:
        raise ValueError(f"Unsupported server type: {server_type}")
    
    base_config = SERVER_CONFIGS[server_type]['default_config'].copy()
    
    if environment == 'production':
        base_config.update(SERVER_CONFIGS[server_type].get('production_config', {}))
    elif environment == 'termux':
        base_config.update(SERVER_CONFIGS[server_type].get('termux_optimized', {}))
        base_config.update(TERMUX_SPECIFIC_CONFIGS)
    
    base_config.update(SECURITY_CONFIGS)
    base_config.update(MONITORING_CONFIGS)
    base_config.update(PERFORMANCE_CONFIGS)
    
    return base_config

def validate_server_config(config: Dict[str, Any]) -> bool:
    required_keys = ['host', 'port']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    if not isinstance(config['port'], int) or config['port'] < 1 or config['port'] > 65535:
        raise ValueError("Invalid port number")
    
    return True

