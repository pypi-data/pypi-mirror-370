from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.box import HEAVY, ROUNDED, DOUBLE_EDGE
from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from colorama import init, Fore, Style
import time
import random

init(autoreset=True)
console = Console()

def show_banner():
    # ASCII art for "ANTI SHLOP AGENT" in big letters
    ascii_art = """
[bold magenta]╔═══════════════════════════════════════════════════════════════════════════════════════╗[/bold magenta]
[bold magenta]║[/bold magenta]                                                                                       [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]   [bold cyan]█████╗ ███╗   ██╗████████╗██╗    [bold magenta]███████╗██╗  ██╗██╗      ██████╗ ██████╗[/bold magenta]        [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]██╔══██╗████╗  ██║╚══██╔══╝██║    [bold magenta]██╔════╝██║  ██║██║     ██╔═══██╗██╔══██╗[/bold magenta]       [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]███████║██╔██╗ ██║   ██║   ██║    [bold magenta]███████╗███████║██║     ██║   ██║██████╔╝[/bold magenta]       [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]██╔══██║██║╚██╗██║   ██║   ██║    [bold magenta]╚════██║██╔══██║██║     ██║   ██║██╔═══╝[/bold magenta]        [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]██║  ██║██║ ╚████║   ██║   ██║    [bold magenta]███████║██║  ██║███████╗╚██████╔╝██║[/bold magenta]            [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝    [bold magenta]╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝[/bold magenta]            [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                                                                                       [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                 [bold yellow]█████╗  ██████╗ ███████╗███╗   ██╗████████╗[/bold yellow]                        [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                [bold yellow]██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/bold yellow]                        [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                [bold yellow]███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║[/bold yellow]                           [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                [bold yellow]██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║[/bold yellow]                           [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                [bold yellow]██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║[/bold yellow]                           [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                [bold yellow]╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝[/bold yellow]                           [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                                                                                       [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                    [dim white]AI-Powered Security Vulnerability Scanner[/dim white]                      [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                           [dim white]Version 1.0.0 | made by itscool2b                             [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]                                                                                       [bold magenta]║[/bold magenta]
[bold magenta]╚═══════════════════════════════════════════════════════════════════════════════════════╝[/bold magenta]
    """
    
    console.print(ascii_art)
    
    # Animated loading effect
    loading_text = "[bold cyan]Initializing bug detection engine[/bold cyan]"
    with console.status(loading_text, spinner="dots12"):
        time.sleep(0.5)

def show_no_api_key_message():
    error_panel = Panel(
        "[bold red]⚠️  NO API KEY DETECTED[/bold red]\n\n"
        "[dim]The Anti Shlop Security Agent requires an OpenAI API key to scan for vulnerabilities.[/dim]\n\n"
        "[bold yellow]Quick Setup:[/bold yellow]\n"
        "  [cyan]$[/cyan] python antishlop.py --set-key [green]YOUR_OPENAI_KEY[/green]\n\n"
        "[bold yellow]Alternative:[/bold yellow]\n"
        "  [cyan]$[/cyan] export OPENAI_API_KEY=[green]your_key_here[/green]\n\n"
        "[dim]Get your API key at: [link=https://platform.openai.com/api-keys]https://platform.openai.com/api-keys[/link][/dim]",
        title="[bold red]⚡ CONFIGURATION REQUIRED ⚡[/bold red]",
        border_style="red",
        box=DOUBLE_EDGE,
        padding=(1, 2)
    )
    console.print(error_panel)

def show_scanning_header(directory):
    scan_panel = Panel(
        f"[bold green]📡 TARGET DIRECTORY[/bold green]\n"
        f"[cyan]{directory}[/cyan]\n\n"
        f"[dim]Press [bold]Ctrl+C[/bold] to abort scan[/dim]",
        title="[bold cyan]🔍 INITIATING DEEP SCAN[/bold cyan]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(scan_panel)

def create_progress_bar():
    return Progress(
        SpinnerColumn(spinner_name="dots12", style="bold cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(
            style="cyan",
            complete_style="bold green",
            finished_style="bold green",
            pulse_style="cyan"
        ),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TextColumn("[bold magenta]→[/bold magenta] [yellow]{task.fields[current_file]}[/yellow]"),
        console=console,
        expand=True
    )

def show_vulnerability_found(filepath, line_num, severity, vuln_type, description):
    severity_styles = {
        'critical': ('bold red', '💀', 'CRITICAL'),
        'high': ('bold yellow', '⚠️ ', 'HIGH'),
        'medium': ('bold cyan', '⚡', 'MEDIUM'),
        'low': ('dim white', '💡', 'LOW')
    }
    
    style, icon, label = severity_styles.get(severity, ('white', '🐛', 'UNKNOWN'))
    
    vuln_text = Text()
    vuln_text.append(f"\n{icon} ", style)
    vuln_text.append(f"[{label}] ", style)
    vuln_text.append(f"{vuln_type}: ", "bold cyan")
    vuln_text.append(f"{filepath}:", "bold white")
    vuln_text.append(f"{line_num}\n", "yellow")
    vuln_text.append(f"   └─ {description}", "dim white")
    
    console.print(vuln_text)

def show_summary(total_files, total_vulnerabilities, scan_time):
    console.print("\n")
    
    # Create a fancy summary table
    summary_panel = Panel.fit(
        f"[bold cyan]FILES ANALYZED:[/bold cyan]  [bold white]{total_files}[/bold white]\n"
        f"[bold magenta]VULNERABILITIES:[/bold magenta]  [bold white]{total_vulnerabilities}[/bold white]\n"
        f"[bold yellow]SCAN DURATION:[/bold yellow]   [bold white]{scan_time:.2f}s[/bold white]\n"
        f"[bold green]SCAN SPEED:[/bold green]      [bold white]{total_files/scan_time:.1f} files/sec[/bold white]",
        title="[bold cyan]═══ SCAN COMPLETE ═══[/bold cyan]",
        border_style="cyan",
        box=HEAVY,
        padding=(1, 3)
    )
    
    console.print(Align.center(summary_panel))
    
    if total_vulnerabilities == 0:
        success_text = Text()
        success_text.append("\n🛡️ ", "bold green")
        success_text.append("SECURE CODE DETECTED", "bold green blink")
        success_text.append(" 🛡️\n", "bold green")
        success_text.append("No security vulnerabilities found!", "green")
        console.print(Align.center(success_text))
    else:
        warning_text = Text()
        warning_text.append("\n🚨 ", "bold red")
        warning_text.append(f"FOUND {total_vulnerabilities} SECURITY VULNERABILITIES", "bold red")
        warning_text.append(" 🚨\n", "bold red")
        warning_text.append("Immediate action required - review the vulnerabilities above", "red")
        console.print(Align.center(warning_text))

def show_analyzing_file(filename):
    console.print(f"[dim cyan]🔬 Analyzing:[/dim cyan] [white]{filename}[/white]", end="\r")

def show_error(message):
    error_panel = Panel(
        f"[bold red]{message}[/bold red]",
        title="[bold red]❌ ERROR[/bold red]",
        border_style="red",
        box=ROUNDED,
        padding=(0, 2)
    )
    console.print(error_panel)

def show_success(message):
    success_text = Text()
    success_text.append("✅ ", "bold green")
    success_text.append(message, "green")
    console.print(success_text)

def show_api_key_set():
    key_panel = Panel(
        "[bold green]✅ API KEY CONFIGURED SUCCESSFULLY![/bold green]\n\n"
        "[cyan]The Anti Shlop Security Agent is now ready to detect vulnerabilities.[/cyan]\n"
        "[dim]Run [bold]python antishlop.py[/bold] to start scanning[/dim]",
        title="[bold green]⚡ READY TO SCAN ⚡[/bold green]",
        border_style="green",
        box=DOUBLE_EDGE,
        padding=(1, 2)
    )
    console.print(key_panel)

def clear_line():
    console.print(" " * 100, end="\r")

def show_file_stats(stats):
    """Display file statistics in a modern way"""
    stats_table = Table(
        title="[bold cyan]📊 PROJECT STATISTICS[/bold cyan]",
        box=ROUNDED,
        border_style="cyan",
        title_style="bold cyan"
    )
    
    stats_table.add_column("Metric", style="cyan", justify="left")
    stats_table.add_column("Value", style="bold white", justify="right")
    
    stats_table.add_row("Total Files", f"{stats['total_files']:,}")
    stats_table.add_row("Total Size", f"{stats['total_size'] / 1024 / 1024:.2f} MB")
    stats_table.add_row("Largest File", f"{stats.get('largest_file', 'N/A')}")
    
    console.print(stats_table)
    
    if stats.get('by_extension'):
        ext_table = Table(
            title="[bold magenta]FILE TYPES[/bold magenta]",
            box=ROUNDED,
            border_style="magenta",
            show_header=False
        )
        ext_table.add_column("Extension", style="yellow")
        ext_table.add_column("Count", style="white", justify="right")
        
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:5]:
            ext_table.add_row(ext or "no extension", str(count))
        
        console.print(ext_table)