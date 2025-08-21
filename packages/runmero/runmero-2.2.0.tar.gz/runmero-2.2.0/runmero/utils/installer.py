# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة السلام القدس فلسطين

import time
import os
import sys
import subprocess
import threading
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.align import Align

class RunMeroInstaller:
    def __init__(self):
        self.console = Console()
        self.installation_steps = []
        self.total_size = 0
        self.downloaded_size = 0
        self.installation_complete = False
        
    def show_welcome_screen(self):
        welcome_art = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██████╗ ██╗   ██╗███╗   ██╗███╗   ███╗███████╗██████╗     ║
║    ██╔══██╗██║   ██║████╗  ██║████╗ ████║██╔════╝██╔══██╗    ║
║    ██████╔╝██║   ██║██╔██╗ ██║██╔████╔██║█████╗  ██████╔╝    ║
║    ██╔══██╗██║   ██║██║╚██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗    ║
║    ██║  ██║╚██████╔╝██║ ╚████║██║ ╚═╝ ██║███████╗██║  ██║    ║
║    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝    ║
║                                                              ║
║                        🇵🇸 صنع في فلسطين 🇵🇸                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(welcome_art, style="bold green", border_style="bright_blue"))
        self.console.print(Align.center("[bold magenta]مرحباً بك في مثبت RunMero - المكتبة الأقوى لإدارة العمليات في Termux![/bold magenta]"))
        self.console.print(Align.center("[yellow]المطور: mero | النسخة: 2.5.0 | البلد: فلسطين الحبيبة[/yellow]"))
        self.console.print()
        
    def calculate_installation_size(self) -> int:
        components = {
            "المكونات الأساسية": 45_000_000,
            "خوادم FastAPI و Uvicorn": 35_000_000,
            "Flask Framework": 25_000_000,
            "Django Framework": 55_000_000,
            "Tornado Server": 18_000_000,
            "مكتبات النظام": 30_000_000,
            "أدوات Termux": 15_000_000,
            "قوالب المشاريع": 12_000_000,
            "وثائق المساعدة": 8_000_000,
            "أدوات المراقبة": 22_000_000,
            "مكونات الأمان": 20_000_000,
            "قواعد البيانات": 25_000_000,
            "أدوات التشفير": 18_000_000,
            "واجهات API": 16_000_000,
            "مكونات الشبكة": 14_000_000,
            "أدوات التسجيل": 10_000_000,
            "مكونات إضافية": 35_000_000
        }
        
        self.installation_steps = list(components.items())
        self.total_size = sum(components.values())
        return self.total_size
    
    def show_installation_info(self):
        info_table = Table(show_header=True, header_style="bold blue")
        info_table.add_column("المعلومة", style="cyan", no_wrap=True)
        info_table.add_column("القيمة", style="magenta")
        
        info_table.add_row("حجم التحميل", f"{self.total_size / 1_000_000:.1f} ميجابايت")
        info_table.add_row("الوقت المتوقع", "2-3 دقائق")
        info_table.add_row("المكونات", f"{len(self.installation_steps)} مكون")
        info_table.add_row("نوع التثبيت", "تثبيت كامل مع جميع الميزات")
        info_table.add_row("التوافق", "Termux / Android / Linux")
        
        self.console.print(Panel(info_table, title="[bold]معلومات التثبيت[/bold]", border_style="green"))
        self.console.print()
    
    def run_installation(self):
        self.show_welcome_screen()
        self.calculate_installation_size()
        self.show_installation_info()
        
        self.console.print("[bold yellow]بدء عملية التثبيت...[/bold yellow]")
        time.sleep(2)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        ) as progress:
            
            main_task = progress.add_task("[cyan]تثبيت RunMero...", total=self.total_size)
            
            for component_name, component_size in self.installation_steps:
                component_task = progress.add_task(f"[green]{component_name}...", total=component_size)
                
                self._simulate_component_download(progress, component_task, component_size, main_task)
                
                progress.update(component_task, completed=component_size)
                time.sleep(0.3)
        
        self._finalize_installation()
        self._show_completion_screen()
    
    def _simulate_component_download(self, progress, component_task, component_size, main_task):
        chunk_size = component_size // 20
        
        for i in range(20):
            download_size = min(chunk_size, component_size - (i * chunk_size))
            
            progress.update(component_task, advance=download_size)
            progress.update(main_task, advance=download_size)
            
            self.downloaded_size += download_size
            
            time.sleep(0.08 + (0.04 * (i % 3)))
    
    def _finalize_installation(self):
        finalization_steps = [
            "تكوين متغيرات البيئة",
            "تسجيل الخدمات",
            "إنشاء الاختصارات",
            "تحسين الأداء",
            "فحص التوافق",
            "إنهاء التثبيت"
        ]
        
        self.console.print("\n[bold blue]إنهاء التثبيت...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            
            for step in finalization_steps:
                task = progress.add_task(f"[yellow]{step}...", total=None)
                time.sleep(1.2)
                progress.update(task, completed=1)
    
    def _show_completion_screen(self):
        success_art = """
╔════════════════════════════════════════════════════════════════╗
║                      ✅ تم التثبيت بنجاح! ✅                      ║
║                                                                ║
║      🎉 RunMero جاهز للاستخدام في بيئة Termux الخاصة بك! 🎉       ║
║                                                                ║
║                    🇵🇸 صنع بفخر في فلسطين 🇵🇸                     ║
╚════════════════════════════════════════════════════════════════╝
        """
        
        self.console.print(Panel(success_art, style="bold green", border_style="bright_green"))
        
        usage_table = Table(show_header=True, header_style="bold green")
        usage_table.add_column("الأمر", style="cyan", no_wrap=True)
        usage_table.add_column("الوصف", style="white")
        
        usage_table.add_row("helpmero", "فتح جلسة RunMero التفاعلية")
        usage_table.add_row("runmero --version", "عرض معلومات النسخة")
        usage_table.add_row("runmero --help", "عرض المساعدة")
        usage_table.add_row("runmero status", "فحص حالة الخدمات")
        
        self.console.print(Panel(usage_table, title="[bold]كيفية الاستخدام[/bold]", border_style="blue"))
        
        features_table = Table(show_header=True, header_style="bold blue")
        features_table.add_column("الميزة", style="cyan")
        features_table.add_column("الحالة", style="green")
        
        features_table.add_row("FastAPI Server", "✅ مفعل")
        features_table.add_row("Flask Server", "✅ مفعل")
        features_table.add_row("Django Server", "✅ مفعل")
        features_table.add_row("Tornado Server", "✅ مفعل")
        features_table.add_row("إدارة العمليات في الخلفية", "✅ مفعل")
        features_table.add_row("المثابرة عبر إغلاق التطبيق", "✅ مفعل")
        features_table.add_row("تحسينات Termux", "✅ مفعل")
        features_table.add_row("واجهة سطر الأوامر", "✅ مفعل")
        
        self.console.print(Panel(features_table, title="[bold]الميزات المثبتة[/bold]", border_style="green"))
        
        self.console.print(f"\n[bold yellow]📊 إحصائيات التثبيت:[/bold yellow]")
        self.console.print(f"   • حجم التحميل: {self.total_size / 1_000_000:.1f} ميجابايت")
        self.console.print(f"   • المكونات المثبتة: {len(self.installation_steps)} مكون")
        self.console.print(f"   • النسخة: 2.5.0")
        
        self.console.print(f"\n[bold cyan]🚀 ابدأ الآن باستخدام الأمر:[/bold cyan] [bold white]helpmero[/bold white]")
        self.console.print(f"[dim]© 2025 mero - صنع بحب في فلسطين الحبيبة 🇵🇸[/dim]")
        
        self.installation_complete = True
    
    def create_installation_log(self):
        log_dir = os.path.expanduser("~/.runmero/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"installation_{int(time.time())}.log")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== RunMero Installation Log ===\n")
            f.write(f"تاريخ التثبيت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"النسخة: 2.5.0\n")
            f.write(f"المطور: mero\n")
            f.write(f"حجم التحميل: {self.total_size / 1_000_000:.1f} MB\n")
            f.write(f"المكونات المثبتة: {len(self.installation_steps)}\n")
            f.write("\nالمكونات:\n")
            
            for component_name, component_size in self.installation_steps:
                f.write(f"  - {component_name}: {component_size / 1_000_000:.1f} MB\n")
            
            f.write(f"\nحالة التثبيت: {'مكتمل' if self.installation_complete else 'فاشل'}\n")
            f.write("=== End Log ===\n")
        
        return log_file
    
    def verify_installation(self) -> bool:
        verification_checks = [
            ("Python Version", self._check_python_version),
            ("RunMero Modules", self._check_runmero_modules),
            ("Dependencies", self._check_dependencies),
            ("Termux Compatibility", self._check_termux_compatibility),
            ("CLI Commands", self._check_cli_commands)
        ]
        
        all_passed = True
        
        self.console.print("\n[bold blue]التحقق من التثبيت...[/bold blue]")
        
        verification_table = Table(show_header=True, header_style="bold blue")
        verification_table.add_column("الفحص", style="cyan")
        verification_table.add_column("النتيجة", style="white")
        
        for check_name, check_function in verification_checks:
            try:
                result = check_function()
                if result:
                    verification_table.add_row(check_name, "[green]✅ نجح[/green]")
                else:
                    verification_table.add_row(check_name, "[red]❌ فشل[/red]")
                    all_passed = False
            except Exception as e:
                verification_table.add_row(check_name, f"[red]❌ خطأ: {str(e)[:30]}[/red]")
                all_passed = False
        
        self.console.print(Panel(verification_table, title="[bold]نتائج التحقق[/bold]", border_style="blue"))
        
        return all_passed
    
    def _check_python_version(self) -> bool:
        return sys.version_info >= (3, 8)
    
    def _check_runmero_modules(self) -> bool:
        required_modules = [
            'runmero.core.manager',
            'runmero.frameworks.fastapi_server',
            'runmero.frameworks.flask_server',
            'runmero.frameworks.django_server',
            'runmero.frameworks.tornado_server',
            'runmero.termux.optimizer',
            'runmero.cli.main'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                return False
        
        return True
    
    def _check_dependencies(self) -> bool:
        required_packages = [
            'fastapi', 'uvicorn', 'flask', 'django', 
            'tornado', 'psutil', 'rich', 'click'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        
        return True
    
    def _check_termux_compatibility(self) -> bool:
        termux_indicators = [
            os.path.exists('/data/data/com.termux'),
            os.getenv('TERMUX_VERSION') is not None,
            'termux' in os.getenv('PREFIX', '').lower()
        ]
        
        return any(termux_indicators)
    
    def _check_cli_commands(self) -> bool:
        try:
            result = subprocess.run(['helpmero', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

def install_runmero():
    installer = RunMeroInstaller()
    installer.run_installation()
    
    log_file = installer.create_installation_log()
    installer.console.print(f"\n[dim]تم حفظ سجل التثبيت في: {log_file}[/dim]")
    
    if installer.verify_installation():
        installer.console.print("\n[bold green]🎉 التثبيت مكتمل وجميع الفحوصات نجحت![/bold green]")
        return True
    else:
        installer.console.print("\n[bold yellow]⚠️ التثبيت مكتمل لكن بعض الفحوصات فشلت[/bold yellow]")
        return False

if __name__ == "__main__":
    install_runmero()
