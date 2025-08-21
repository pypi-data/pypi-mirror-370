# حقوق الطبع والنشر محفوظة © 2025 mero - من مدينة نابلس جبل النار فلسطين

import sys
import os
import time
import signal
import subprocess
import json
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout

from ..core.manager import ProcessManager
from ..frameworks.fastapi_server import FastAPIServer
from ..frameworks.flask_server import FlaskServer
from ..frameworks.django_server import DjangoServer
from ..frameworks.tornado_server import TornadoServer
from ..termux.optimizer import TermuxOptimizer
from ..termux.persistence import PersistenceManager
from ..utils.console import Console as RunMeroConsole

class RunMeroCLI:
    def __init__(self):
        self.console = Console()
        self.runmero_console = RunMeroConsole()
        self.process_manager = ProcessManager()
        self.termux_optimizer = TermuxOptimizer()
        self.persistence_manager = PersistenceManager()
        self.interactive_mode = False
        
    def show_welcome_banner(self):
        banner_art = """
██████╗ ██╗   ██╗███╗   ██╗███╗   ███╗███████╗██████╗  ██████╗ 
██╔══██╗██║   ██║████╗  ██║████╗ ████║██╔════╝██╔══██╗██╔═══██╗
██████╔╝██║   ██║██╔██╗ ██║██╔████╔██║█████╗  ██████╔╝██║   ██║
██╔══██╗██║   ██║██║╚██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║
██║  ██║╚██████╔╝██║ ╚████║██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ 
        """
        
        welcome_panel = Panel(
            f"[bold green]{banner_art}[/bold green]\n\n"
            f"[bold blue]مرحباً بك في RunMero - أقوى مكتبة لإدارة العمليات في Termux[/bold blue]\n"
            f"[yellow]المطور: mero | النسخة: 2.5.0 | صنع في: فلسطين الحبيبة 🇵🇸[/yellow]\n\n"
            f"[dim]للمساعدة اكتب: help | للخروج اكتب: exit[/dim]",
            title="[bold]RunMero CLI[/bold]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
    
    def start_interactive_mode(self):
        self.interactive_mode = True
        self.show_welcome_banner()
        
        try:
            self.termux_optimizer.optimize_for_android()
            self.console.print("[green]✅ تم تحسين الإعدادات لبيئة Termux[/green]")
        except Exception as e:
            self.console.print(f"[yellow]⚠️ تحذير: {e}[/yellow]")
        
        while self.interactive_mode:
            try:
                command = Prompt.ask(
                    "[bold blue]RunMero[/bold blue]",
                    default=""
                ).strip()
                
                if not command:
                    continue
                
                self.execute_command(command)
                
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]هل تريد الخروج من RunMero؟[/yellow]"):
                    break
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]خطأ: {e}[/red]")
        
        self.cleanup_and_exit()
    
    def execute_command(self, command: str):
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        command_map = {
            'help': self.show_help,
            'status': self.show_status,
            'ps': self.list_processes,
            'start': self.start_server,
            'stop': self.stop_process,
            'restart': self.restart_process,
            'logs': self.show_logs,
            'system': self.show_system_info,
            'optimize': self.run_optimization,
            'backup': self.create_backup,
            'restore': self.restore_backup,
            'config': self.manage_config,
            'monitor': self.start_monitoring,
            'dashboard': self.open_dashboard,
            'clear': self.console.clear,
            'exit': self.exit_interactive,
            'quit': self.exit_interactive,
        }
        
        if cmd in command_map:
            try:
                if args:
                    command_map[cmd](*args)
                else:
                    command_map[cmd]()
            except TypeError:
                command_map[cmd]()
        else:
            self.console.print(f"[red]أمر غير معروف: {cmd}[/red]")
            self.console.print("[dim]اكتب 'help' لعرض الأوامر المتاحة[/dim]")
    
    def show_help(self):
        help_table = Table(title="أوامر RunMero المتاحة", show_header=True, header_style="bold blue")
        help_table.add_column("الأمر", style="cyan", no_wrap=True)
        help_table.add_column("الوصف", style="white")
        help_table.add_column("مثال", style="dim")
        
        commands = [
            ("help", "عرض هذه المساعدة", "help"),
            ("status", "عرض حالة جميع العمليات", "status"),
            ("ps", "قائمة العمليات النشطة", "ps"),
            ("start <server>", "تشغيل خادم", "start fastapi"),
            ("stop <process_id>", "إيقاف عملية", "stop server_1"),
            ("restart <process_id>", "إعادة تشغيل عملية", "restart server_1"),
            ("logs <process_id>", "عرض سجلات عملية", "logs server_1"),
            ("system", "معلومات النظام", "system"),
            ("optimize", "تحسين الأداء", "optimize"),
            ("backup", "إنشاء نسخة احتياطية", "backup"),
            ("restore <name>", "استعادة نسخة احتياطية", "restore backup_1"),
            ("config", "إدارة التكوين", "config"),
            ("monitor", "مراقبة الموارد", "monitor"),
            ("dashboard", "فتح لوحة التحكم", "dashboard"),
            ("clear", "مسح الشاشة", "clear"),
            ("exit/quit", "الخروج من RunMero", "exit")
        ]
        
        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)
        
        self.console.print(Panel(help_table, border_style="green"))
        
        self.console.print("\n[bold blue]الخوادم المدعومة:[/bold blue]")
        servers_table = Table(show_header=False, box=None)
        servers_table.add_column("", style="cyan")
        servers_table.add_column("", style="white")
        
        servers = [
            ("fastapi", "خادم FastAPI مع Uvicorn"),
            ("flask", "خادم Flask"),
            ("django", "خادم Django"),
            ("tornado", "خادم Tornado")
        ]
        
        for server, desc in servers:
            servers_table.add_row(f"• {server}", desc)
        
        self.console.print(servers_table)
    
    def show_status(self):
        processes = self.process_manager.list_processes()
        
        if not processes:
            self.console.print("[yellow]لا توجد عمليات نشطة[/yellow]")
            return
        
        status_table = Table(title="حالة العمليات", show_header=True, header_style="bold green")
        status_table.add_column("ID", style="cyan")
        status_table.add_column("الحالة", style="white")
        status_table.add_column("PID", style="yellow")
        status_table.add_column("وقت التشغيل", style="blue")
        status_table.add_column("استخدام المعالج", style="red")
        status_table.add_column("الذاكرة", style="magenta")
        
        for process in processes:
            status_color = "green" if process['status'] == 'running' else "red" if process['status'] == 'failed' else "yellow"
            running_time = f"{process.get('running_time', 0):.1f}s" if process.get('running_time') else "N/A"
            cpu_percent = f"{process.get('cpu_percent', 0):.1f}%" if process.get('cpu_percent') else "N/A"
            memory_mb = f"{process.get('memory_info', {}).get('rss', 0) / 1024 / 1024:.1f}MB" if process.get('memory_info') else "N/A"
            
            status_table.add_row(
                process['id'],
                f"[{status_color}]{process['status']}[/{status_color}]",
                str(process.get('pid', 'N/A')),
                running_time,
                cpu_percent,
                memory_mb
            )
        
        self.console.print(Panel(status_table, border_style="blue"))
    
    def list_processes(self):
        self.show_status()
        
        system_stats = self.process_manager.get_system_stats()
        
        system_table = Table(title="إحصائيات النظام", show_header=True, header_style="bold blue")
        system_table.add_column("المعيار", style="cyan")
        system_table.add_column("القيمة", style="white")
        
        system_table.add_row("استخدام المعالج", f"{system_stats.get('cpu_percent', 0):.1f}%")
        system_table.add_row("استخدام الذاكرة", f"{system_stats.get('memory', {}).get('percent', 0):.1f}%")
        system_table.add_row("استخدام القرص", f"{system_stats.get('disk', {}).get('percent', 0):.1f}%")
        system_table.add_row("العمليات النشطة", str(system_stats.get('active_processes', 0)))
        system_table.add_row("إجمالي العمليات", str(system_stats.get('total_processes', 0)))
        
        self.console.print(Panel(system_table, border_style="green"))
    
    def start_server(self, server_type: str = None, *args):
        if not server_type:
            server_type = Prompt.ask(
                "اختر نوع الخادم",
                choices=["fastapi", "flask", "django", "tornado"],
                default="fastapi"
            )
        
        server_type = server_type.lower()
        
        try:
            if server_type == "fastapi":
                server = FastAPIServer(debug=True)
                process_id = f"fastapi_{int(time.time())}"
            elif server_type == "flask":
                server = FlaskServer(debug=True)
                process_id = f"flask_{int(time.time())}"
            elif server_type == "django":
                server = DjangoServer(debug=True)
                process_id = f"django_{int(time.time())}"
            elif server_type == "tornado":
                server = TornadoServer(debug=True)
                process_id = f"tornado_{int(time.time())}"
            else:
                self.console.print(f"[red]نوع خادم غير مدعوم: {server_type}[/red]")
                return
            
            process = self.process_manager.create_process(
                process_id=process_id,
                target=server.run_in_background,
                persistent=True
            )
            
            if self.process_manager.start_process(process_id):
                self.console.print(f"[green]✅ تم تشغيل خادم {server_type} بنجاح[/green]")
                self.console.print(f"[blue]معرف العملية: {process_id}[/blue]")
                
                if hasattr(server, 'port'):
                    self.console.print(f"[yellow]الخادم يعمل على: http://0.0.0.0:{server.port}[/yellow]")
            else:
                self.console.print(f"[red]❌ فشل في تشغيل خادم {server_type}[/red]")
        
        except Exception as e:
            self.console.print(f"[red]خطأ في تشغيل الخادم: {e}[/red]")
    
    def stop_process(self, process_id: str = None):
        if not process_id:
            processes = self.process_manager.list_processes()
            if not processes:
                self.console.print("[yellow]لا توجد عمليات للإيقاف[/yellow]")
                return
            
            choices = [p['id'] for p in processes if p['status'] == 'running']
            if not choices:
                self.console.print("[yellow]لا توجد عمليات نشطة للإيقاف[/yellow]")
                return
            
            process_id = Prompt.ask(
                "اختر العملية للإيقاف",
                choices=choices
            )
        
        if self.process_manager.stop_process(process_id):
            self.console.print(f"[green]✅ تم إيقاف العملية {process_id}[/green]")
        else:
            self.console.print(f"[red]❌ فشل في إيقاف العملية {process_id}[/red]")
    
    def restart_process(self, process_id: str = None):
        if not process_id:
            processes = self.process_manager.list_processes()
            if not processes:
                self.console.print("[yellow]لا توجد عمليات لإعادة التشغيل[/yellow]")
                return
            
            choices = [p['id'] for p in processes]
            process_id = Prompt.ask(
                "اختر العملية لإعادة التشغيل",
                choices=choices
            )
        
        if self.process_manager.restart_process(process_id):
            self.console.print(f"[green]✅ تم إعادة تشغيل العملية {process_id}[/green]")
        else:
            self.console.print(f"[red]❌ فشل في إعادة تشغيل العملية {process_id}[/red]")
    
    def show_logs(self, process_id: str = None, lines: int = 50):
        if not process_id:
            processes = self.process_manager.list_processes()
            if not processes:
                self.console.print("[yellow]لا توجد عمليات لعرض سجلاتها[/yellow]")
                return
            
            choices = [p['id'] for p in processes]
            process_id = Prompt.ask("اختر العملية لعرض سجلاتها", choices=choices)
        
        logs = self.persistence_manager.get_process_logs(process_id, lines)
        
        if not logs:
            self.console.print(f"[yellow]لا توجد سجلات للعملية {process_id}[/yellow]")
            return
        
        logs_table = Table(title=f"سجلات العملية: {process_id}", show_header=True, header_style="bold blue")
        logs_table.add_column("الوقت", style="cyan")
        logs_table.add_column("المستوى", style="white")
        logs_table.add_column("الرسالة", style="white")
        
        for log in logs:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log['timestamp']))
            level_color = "green" if log['level'] == 'INFO' else "yellow" if log['level'] == 'WARNING' else "red"
            
            logs_table.add_row(
                timestamp,
                f"[{level_color}]{log['level']}[/{level_color}]",
                log['message'][:80] + "..." if len(log['message']) > 80 else log['message']
            )
        
        self.console.print(Panel(logs_table, border_style="blue"))
    
    def show_system_info(self):
        system_info = self.termux_optimizer.get_system_info()
        
        info_table = Table(title="معلومات النظام", show_header=True, header_style="bold green")
        info_table.add_column("المعلومة", style="cyan")
        info_table.add_column("القيمة", style="white")
        
        info_table.add_row("نوع النظام", "Termux" if system_info['is_termux'] else "Linux")
        info_table.add_row("منصة العمل", system_info['platform'])
        info_table.add_row("نسخة Python", system_info['python_version'])
        
        if system_info['is_termux']:
            info_table.add_row("نسخة Termux", system_info.get('termux_version', 'غير معروف'))
            info_table.add_row("نسخة Android", system_info.get('android_version', 'غير معروف'))
            info_table.add_row("موديل الجهاز", system_info.get('device_model', 'غير معروف'))
        
        optimizations = system_info.get('optimizations_applied', {})
        if optimizations:
            for opt_type, opts in optimizations.items():
                info_table.add_row(f"تحسينات {opt_type}", ", ".join(opts) if opts else "لا توجد")
        
        self.console.print(Panel(info_table, border_style="green"))
        
        system_stats = self.process_manager.get_system_stats()
        
        stats_table = Table(title="إحصائيات الأداء", show_header=True, header_style="bold blue")
        stats_table.add_column("المعيار", style="cyan")
        stats_table.add_column("القيمة", style="white")
        stats_table.add_column("الحالة", style="green")
        
        cpu_status = "جيد" if system_stats.get('cpu_percent', 0) < 70 else "مرتفع"
        memory_status = "جيد" if system_stats.get('memory', {}).get('percent', 0) < 80 else "مرتفع"
        disk_status = "جيد" if system_stats.get('disk', {}).get('percent', 0) < 90 else "ممتلئ"
        
        stats_table.add_row("استخدام المعالج", f"{system_stats.get('cpu_percent', 0):.1f}%", cpu_status)
        stats_table.add_row("استخدام الذاكرة", f"{system_stats.get('memory', {}).get('percent', 0):.1f}%", memory_status)
        stats_table.add_row("استخدام القرص", f"{system_stats.get('disk', {}).get('percent', 0):.1f}%", disk_status)
        
        self.console.print(Panel(stats_table, border_style="blue"))
    
    def run_optimization(self):
        self.console.print("[blue]🚀 بدء تحسين النظام...[/blue]")
        
        with self.console.status("[bold green]تطبيق التحسينات...") as status:
            optimizations = []
            
            if self.termux_optimizer.optimize_for_android():
                optimizations.append("تحسينات Android")
            
            termux_opts = self.termux_optimizer.apply_termux_specific_optimizations()
            if termux_opts:
                optimizations.extend(termux_opts)
            
            prevention_strategies = self.termux_optimizer.prevent_android_killing()
            if prevention_strategies:
                optimizations.extend(prevention_strategies)
        
        if optimizations:
            self.console.print("[green]✅ تم تطبيق التحسينات التالية:[/green]")
            for opt in optimizations:
                self.console.print(f"  • {opt}")
        else:
            self.console.print("[yellow]⚠️ لم يتم تطبيق أي تحسينات[/yellow]")
    
    def create_backup(self, name: str = None):
        if not name:
            name = f"backup_{int(time.time())}"
        
        with self.console.status("[bold blue]إنشاء نسخة احتياطية..."):
            backup_path = self.persistence_manager.backup_data(name)
        
        if backup_path:
            self.console.print(f"[green]✅ تم إنشاء النسخة الاحتياطية: {backup_path}[/green]")
        else:
            self.console.print("[red]❌ فشل في إنشاء النسخة الاحتياطية[/red]")
    
    def restore_backup(self, name: str = None):
        if not name:
            self.console.print("[red]يجب تحديد اسم النسخة الاحتياطية[/red]")
            return
        
        if Confirm.ask(f"[yellow]هل أنت متأكد من استعادة النسخة الاحتياطية '{name}'؟[/yellow]"):
            with self.console.status("[bold blue]استعادة النسخة الاحتياطية..."):
                success = self.persistence_manager.restore_from_backup(name)
            
            if success:
                self.console.print("[green]✅ تم استعادة النسخة الاحتياطية بنجاح[/green]")
            else:
                self.console.print("[red]❌ فشل في استعادة النسخة الاحتياطية[/red]")
    
    def manage_config(self, key: str = None, value: str = None):
        if key and value:
            self.persistence_manager.save_configuration(key, value)
            self.console.print(f"[green]✅ تم حفظ التكوين: {key} = {value}[/green]")
        elif key:
            config_value = self.persistence_manager.load_configuration(key)
            self.console.print(f"[blue]{key}: {config_value}[/blue]")
        else:
            self.console.print("[blue]أوامر التكوين:[/blue]")
            self.console.print("  config <key> <value> - حفظ قيمة")
            self.console.print("  config <key> - عرض قيمة")
    
    def start_monitoring(self):
        self.console.print("[blue]🔍 بدء مراقبة الموارد...[/blue]")
        
        monitor = self.termux_optimizer.monitor_system_resources(interval=5)
        
        try:
            with Live(console=self.console, refresh_per_second=1) as live:
                for i in range(60):
                    system_stats = self.process_manager.get_system_stats()
                    
                    layout = Layout()
                    
                    stats_table = Table(title="مراقبة الموارد المباشرة", show_header=True, header_style="bold green")
                    stats_table.add_column("المورد", style="cyan")
                    stats_table.add_column("القيمة", style="white")
                    stats_table.add_column("الحالة", style="green")
                    
                    cpu = system_stats.get('cpu_percent', 0)
                    memory = system_stats.get('memory', {}).get('percent', 0)
                    
                    cpu_status = "🟢 جيد" if cpu < 70 else "🟡 متوسط" if cpu < 90 else "🔴 مرتفع"
                    memory_status = "🟢 جيد" if memory < 70 else "🟡 متوسط" if memory < 90 else "🔴 مرتفع"
                    
                    stats_table.add_row("المعالج", f"{cpu:.1f}%", cpu_status)
                    stats_table.add_row("الذاكرة", f"{memory:.1f}%", memory_status)
                    stats_table.add_row("العمليات النشطة", str(system_stats.get('active_processes', 0)), "🔵 نشط")
                    
                    layout.update(stats_table)
                    live.update(layout)
                    
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]تم إيقاف المراقبة[/yellow]")
    
    def open_dashboard(self):
        self.console.print("[blue]🌐 فتح لوحة التحكم...[/blue]")
        
        servers = [
            ("FastAPI", "http://localhost:8000/docs"),
            ("Flask", "http://localhost:5000/dashboard"),
            ("Django", "http://localhost:8000/dashboard"),
            ("Tornado", "http://localhost:8888/dashboard")
        ]
        
        dashboard_table = Table(title="لوحات التحكم المتاحة", show_header=True, header_style="bold blue")
        dashboard_table.add_column("الخادم", style="cyan")
        dashboard_table.add_column("الرابط", style="yellow")
        
        for server, url in servers:
            dashboard_table.add_row(server, url)
        
        self.console.print(Panel(dashboard_table, border_style="green"))
        
        if Confirm.ask("هل تريد فتح لوحة تحكم في المتصفح؟"):
            url = Prompt.ask("أدخل الرابط", default="http://localhost:8000")
            try:
                subprocess.run(['termux-open-url', url], check=True)
                self.console.print(f"[green]✅ تم فتح {url}[/green]")
            except subprocess.CalledProcessError:
                self.console.print(f"[yellow]لم يتمكن من فتح الرابط تلقائياً: {url}[/yellow]")
    
    def exit_interactive(self):
        self.console.print("[yellow]👋 شكراً لاستخدام RunMero![/yellow]")
        self.interactive_mode = False
    
    def cleanup_and_exit(self):
        self.console.print("[blue]🧹 تنظيف الموارد...[/blue]")
        
        try:
            self.process_manager.stop_all_processes()
            self.persistence_manager.force_save_all()
        except Exception as e:
            self.console.print(f"[yellow]تحذير أثناء التنظيف: {e}[/yellow]")
        
        self.console.print("[green]✅ تم الخروج من RunMero بأمان[/green]")
        sys.exit(0)

@click.group()
@click.version_option("2.5.0", prog_name="RunMero")
def cli():
    pass

@cli.command()
def interactive():
    cli_instance = RunMeroCLI()
    cli_instance.start_interactive_mode()

@cli.command()
@click.argument('server_type', type=click.Choice(['fastapi', 'flask', 'django', 'tornado']))
@click.option('--port', default=None, type=int, help='منفذ الخادم')
@click.option('--host', default='0.0.0.0', help='عنوان الخادم')
def start(server_type, port, host):
    cli_instance = RunMeroCLI()
    cli_instance.start_server(server_type)

@cli.command()
def status():
    cli_instance = RunMeroCLI()
    cli_instance.show_status()

@cli.command()
def optimize():
    cli_instance = RunMeroCLI()
    cli_instance.run_optimization()

def main():
    try:
        cli_instance = RunMeroCLI()
        cli_instance.start_interactive_mode()
    except KeyboardInterrupt:
        print("\nتم الخروج من RunMero")
        sys.exit(0)
    except Exception as e:
        print(f"خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
