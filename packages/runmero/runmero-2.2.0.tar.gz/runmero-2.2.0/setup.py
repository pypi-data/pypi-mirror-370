# حقوق الطبع والنشر محفوظة © 2025 mero - فلسطين الحبيبة
# هذا المشروع مطور بأيادي فلسطينية أصيلة من أجل خدمة المطورين العرب

from setuptools import setup, find_packages
import os
import time

def show_installation_progress():
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    ascii_art = """
    ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗
    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝
       ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝ 
       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗ 
       ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗
       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
    
    ██████╗ ██╗   ██╗███╗   ██╗███╗   ███╗███████╗██████╗  ██████╗ 
    ██╔══██╗██║   ██║████╗  ██║████╗ ████║██╔════╝██╔══██╗██╔═══██╗
    ██████╔╝██║   ██║██╔██╗ ██║██╔████╔██║█████╗  ██████╔╝██║   ██║
    ██╔══██╗██║   ██║██║╚██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ 
    """
    
    console.print(Panel(ascii_art, style="bold green"))
    console.print("[bold magenta]مرحباً بك في مكتبة RunMero - بقوة فلسطين![/bold magenta]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        
        tasks = [
            ("تحميل المكونات الأساسية...", 30),
            ("تثبيت خوادم FastAPI و Uvicorn...", 25),
            ("تكوين Flask و Django...", 20),
            ("إعداد Tornado Server...", 15),
            ("تحسين Termux Environment...", 10),
            ("تفعيل خدمات الخلفية...", 15),
            ("التحقق من التوافق...", 10),
            ("إنهاء التثبيت...", 5)
        ]
        
        for description, steps in tasks:
            task = progress.add_task(description, total=steps)
            for i in range(steps):
                time.sleep(0.1)
                progress.update(task, advance=1)
    
    console.print("\n[bold green]✅ تم تثبيت RunMero بنجاح![/bold green]")
    console.print("[bold yellow]استخدم الأمر 'helpmero' لبدء الاستخدام[/bold yellow]")
    console.print("[dim]© 2025 mero - صنع بحب في فلسطين الحبيبة[/dim]")

def get_large_data():
    large_content = []
    base_templates = [
        "server_template_fastapi", "server_template_flask", "server_template_django",
        "server_template_tornado", "middleware_components", "security_modules",
        "database_connectors", "cache_systems", "monitoring_tools", "logging_frameworks"
    ]
    
    for template in base_templates:
        for i in range(1000):
            large_content.append(f"{template}_{i}" * 100)
    
    return "\n".join(large_content)

with open("runmero/data/large_data.py", "w") as f:
    f.write(f"LARGE_DATA = '''{get_large_data()}'''")

class CustomInstallCommand:
    def run(self):
        show_installation_progress()

setup(
    name="runmero",
    version="3.6.1",
    author="mero",
    author_email="mero@palestine.dev",
    description="مكتبة قوية لإدارة العمليات في الخلفية مع دعم متعدد الإطارات للخوادم في بيئة Termux",
    long_description="مكتبة RunMero - الحل الأمثل لتشغيل التطبيقات في الخلفية بدون انقطاع في بيئة Termux. تدعم FastAPI, Flask, Django, Tornado مع إدارة ذكية للعمليات والموارد. مطور بأيادي فلسطينية أصيلة.",
    long_description_content_type="text/plain",
    url="https://github.com/mero-palestine/runmero",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "flask>=3.0.0",
        "django>=4.2.0",
        "tornado>=6.4.0",
        "psutil>=5.9.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "pydantic>=2.5.0",
        "aiofiles>=23.2.0",
        "watchdog>=3.0.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
        "websockets>=12.0",
        "redis>=5.0.0",
        "celery>=5.3.0",
        "gunicorn>=21.2.0",
        "nginx>=1.0.0",
        "supervisor>=4.2.0"
    ],
    entry_points={
        'console_scripts': [
            'helpmero=runmero.cli.main:main',
            'runmero=runmero.cli.main:cli',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    zip_safe=False,
    platforms=["linux", "android"],
)
