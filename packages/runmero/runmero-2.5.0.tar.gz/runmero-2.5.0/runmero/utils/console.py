# حقوق الطبع والنشر محفوظة © 2025 mero - من مخيم جباليا فلسطين

import sys
import time
from datetime import datetime
from typing import Any, Optional
from rich.console import Console as RichConsole
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

class Console:
    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich
        if self.use_rich:
            self.rich_console = RichConsole()
        self.log_file = None
        self.enable_logging = False
        
    def setup_logging(self, log_file_path: str):
        self.log_file = log_file_path
        self.enable_logging = True
    
    def _log_to_file(self, message: str, level: str = "INFO"):
        if self.enable_logging and self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            except Exception:
                pass
    
    def print(self, *args, style: Optional[str] = None, **kwargs):
        message = " ".join(str(arg) for arg in args)
        
        if self.use_rich:
            if style:
                self.rich_console.print(message, style=style, **kwargs)
            else:
                self.rich_console.print(message, **kwargs)
        else:
            print(message, **kwargs)
        
        self._log_to_file(message)
    
    def info(self, message: str):
        formatted_msg = f"ℹ️  {message}"
        if self.use_rich:
            self.rich_console.print(formatted_msg, style="bright_blue")
        else:
            print(f"[INFO] {message}")
        self._log_to_file(message, "INFO")
    
    def success(self, message: str):
        formatted_msg = f"✅ {message}"
        if self.use_rich:
            self.rich_console.print(formatted_msg, style="bold green")
        else:
            print(f"[SUCCESS] {message}")
        self._log_to_file(message, "SUCCESS")
    
    def warning(self, message: str):
        formatted_msg = f"⚠️  {message}"
        if self.use_rich:
            self.rich_console.print(formatted_msg, style="bold yellow")
        else:
            print(f"[WARNING] {message}")
        self._log_to_file(message, "WARNING")
    
    def error(self, message: str):
        formatted_msg = f"❌ {message}"
        if self.use_rich:
            self.rich_console.print(formatted_msg, style="bold red")
        else:
            print(f"[ERROR] {message}", file=sys.stderr)
        self._log_to_file(message, "ERROR")
    
    def debug(self, message: str):
        formatted_msg = f"🐛 {message}"
        if self.use_rich:
            self.rich_console.print(formatted_msg, style="dim cyan")
        else:
            print(f"[DEBUG] {message}")
        self._log_to_file(message, "DEBUG")
    
    def header(self, title: str, subtitle: str = ""):
        if self.use_rich:
            if subtitle:
                content = f"[bold white]{title}[/bold white]\n[dim]{subtitle}[/dim]"
            else:
                content = f"[bold white]{title}[/bold white]"
            
            panel = Panel(
                Align.center(content),
                style="bold blue",
                border_style="bright_blue",
                padding=(1, 2)
            )
            self.rich_console.print(panel)
        else:
            print(f"\n{'='*50}")
            print(f" {title}")
            if subtitle:
                print(f" {subtitle}")
            print(f"{'='*50}\n")
        
        self._log_to_file(f"HEADER: {title} - {subtitle}")
    
    def separator(self, char: str = "-", length: int = 50):
        separator_line = char * length
        if self.use_rich:
            self.rich_console.print(separator_line, style="dim")
        else:
            print(separator_line)
    
    def table(self, data: list, headers: list, title: str = ""):
        if self.use_rich:
            table = Table(show_header=True, header_style="bold blue")
            
            for header in headers:
                table.add_column(header, style="cyan")
            
            for row in data:
                table.add_row(*[str(cell) for cell in row])
            
            if title:
                panel = Panel(table, title=f"[bold]{title}[/bold]", border_style="green")
                self.rich_console.print(panel)
            else:
                self.rich_console.print(table)
        else:
            if title:
                print(f"\n{title}")
                print("-" * len(title))
            
            header_line = " | ".join(headers)
            print(header_line)
            print("-" * len(header_line))
            
            for row in data:
                row_line = " | ".join(str(cell) for cell in row)
                print(row_line)
    
    def progress_bar(self, items: list, description: str = "معالجة..."):
        if self.use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.rich_console
            ) as progress:
                task = progress.add_task(description, total=len(items))
                
                for item in items:
                    yield item
                    progress.advance(task, 1)
        else:
            total = len(items)
            for i, item in enumerate(items, 1):
                print(f"\r{description} {i}/{total} ({i/total*100:.1f}%)", end="", flush=True)
                yield item
            print()
    
    def input(self, prompt: str, password: bool = False) -> str:
        if self.use_rich:
            if password:
                import getpass
                return getpass.getpass(f"{prompt}: ")
            else:
                return self.rich_console.input(f"[cyan]{prompt}:[/cyan] ")
        else:
            if password:
                import getpass
                return getpass.getpass(f"{prompt}: ")
            else:
                return input(f"{prompt}: ")
    
    def confirm(self, message: str, default: bool = True) -> bool:
        default_char = "Y/n" if default else "y/N"
        prompt = f"{message} ({default_char})"
        
        response = self.input(prompt).strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'نعم', 'ن']
    
    def select(self, message: str, choices: list) -> Any:
        if self.use_rich:
            self.rich_console.print(f"[cyan]{message}[/cyan]")
            
            table = Table(show_header=False, show_lines=False, pad_edge=False, box=None)
            table.add_column("رقم", style="bright_blue", width=4)
            table.add_column("الخيار", style="white")
            
            for i, choice in enumerate(choices, 1):
                table.add_row(f"{i}.", str(choice))
            
            self.rich_console.print(table)
        else:
            print(f"\n{message}")
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice}")
        
        while True:
            try:
                response = self.input("اختر رقم الخيار")
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                else:
                    self.error("رقم غير صالح، حاول مرة أخرى")
            except ValueError:
                self.error("يرجى إدخال رقم صالح")
    
    def status_display(self, status_data: dict):
        if self.use_rich:
            layout = Layout()
            
            status_table = Table(title="حالة النظام", show_header=True, header_style="bold green")
            status_table.add_column("المعيار", style="cyan", no_wrap=True)
            status_table.add_column("القيمة", style="white")
            status_table.add_column("الحالة", style="green")
            
            for key, value in status_data.items():
                if isinstance(value, dict) and 'value' in value and 'status' in value:
                    status_icon = "✅" if value['status'] == 'good' else "⚠️" if value['status'] == 'warning' else "❌"
                    status_table.add_row(key, str(value['value']), f"{status_icon} {value['status']}")
                else:
                    status_table.add_row(key, str(value), "✅ نشط")
            
            self.rich_console.print(Panel(status_table, border_style="green"))
        else:
            print("\n=== حالة النظام ===")
            for key, value in status_data.items():
                print(f"{key}: {value}")
    
    def live_update(self, update_function, interval: int = 1, duration: int = 10):
        if self.use_rich:
            with Live(console=self.rich_console, refresh_per_second=1) as live:
                start_time = time.time()
                while time.time() - start_time < duration:
                    content = update_function()
                    live.update(content)
                    time.sleep(interval)
        else:
            start_time = time.time()
            while time.time() - start_time < duration:
                content = update_function()
                print(f"\r{content}", end="", flush=True)
                time.sleep(interval)
            print()
    
    def code_block(self, code: str, language: str = "python"):
        if self.use_rich:
            from rich.syntax import Syntax
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            self.rich_console.print(Panel(syntax, border_style="blue"))
        else:
            print(f"\n--- {language.upper()} CODE ---")
            print(code)
            print("--- END CODE ---\n")
    
    def json_display(self, data: dict):
        if self.use_rich:
            from rich.json import JSON
            json_obj = JSON.from_data(data)
            self.rich_console.print(Panel(json_obj, title="JSON Data", border_style="blue"))
        else:
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def clear_screen(self):
        if self.use_rich:
            self.rich_console.clear()
        else:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
    
    def pause(self, message: str = "اضغط Enter للمتابعة..."):
        self.input(message)
    
    def countdown(self, seconds: int, message: str = "انتظار"):
        for i in range(seconds, 0, -1):
            if self.use_rich:
                self.rich_console.print(f"\r[yellow]{message} {i} ثانية...[/yellow]", end="")
            else:
                print(f"\r{message} {i} ثانية...", end="", flush=True)
            time.sleep(1)
        
        if self.use_rich:
            self.rich_console.print(f"\r[green]{message} انتهى![/green]")
        else:
            print(f"\r{message} انتهى!")
    
    def banner(self, text: str, style: str = "ascii"):
        if style == "ascii" and self.use_rich:
            ascii_art = f"""
╔{'═' * (len(text) + 4)}╗
║  {text}  ║
╚{'═' * (len(text) + 4)}╝
            """
            self.rich_console.print(ascii_art, style="bold blue")
        else:
            border = "=" * (len(text) + 4)
            print(f"\n{border}")
            print(f"  {text}  ")
            print(f"{border}\n")
