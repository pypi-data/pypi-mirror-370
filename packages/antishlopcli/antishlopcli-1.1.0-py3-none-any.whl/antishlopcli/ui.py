from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.box import HEAVY, ROUNDED, DOUBLE_EDGE, MINIMAL_HEAVY_HEAD, SQUARE
from rich.layout import Layout
from rich.live import Live
from rich.syntax import Syntax
from rich.columns import Columns
from rich.rule import Rule
from rich import print as rprint
from colorama import init, Fore, Style
import time
import random
import sys
from itertools import cycle

init(autoreset=True)
console = Console()

def animated_text(text, style="bold cyan", delay=0.03):
    """Animate text character by character"""
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(delay)
    console.print()

def show_banner():
    # Enhanced gradient banner with animation
    ascii_art = """
[bold #FF00FF]╔═══════════════════════════════════════════════════════════════════════════════════════╗[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                                                                                       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]   [bold #00FFFF]█████╗ ███╗   ██╗████████╗██╗    [bold #FF00FF]███████╗██╗  ██╗██╗      ██████╗ ██████╗[/bold #FF00FF]        [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]  [bold #00FFFF]██╔══██╗████╗  ██║╚══██╔══╝██║    [bold #FF00FF]██╔════╝██║  ██║██║     ██╔═══██╗██╔══██╗[/bold #FF00FF]       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]  [bold #00FFFF]███████║██╔██╗ ██║   ██║   ██║    [bold #FF00FF]███████╗███████║██║     ██║   ██║██████╔╝[/bold #FF00FF]       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]  [bold #00FFFF]██╔══██║██║╚██╗██║   ██║   ██║    [bold #FF00FF]╚════██║██╔══██║██║     ██║   ██║██╔═══╝[/bold #FF00FF]        [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]  [bold #00FFFF]██║  ██║██║ ╚████║   ██║   ██║    [bold #FF00FF]███████║██║  ██║███████╗╚██████╔╝██║[/bold #FF00FF]            [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]  [bold #00FFFF]╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝    [bold #FF00FF]╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝[/bold #FF00FF]            [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                                                                                       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                 [bold #FFD700]█████╗  ██████╗ ███████╗███╗   ██╗████████╗[/bold #FFD700]                        [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                [bold #FFD700]██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/bold #FFD700]                        [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                [bold #FFD700]███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║[/bold #FFD700]                           [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                [bold #FFD700]██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║[/bold #FFD700]                           [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                [bold #FFD700]██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║[/bold #FFD700]                           [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                [bold #FFD700]╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝[/bold #FFD700]                           [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                                                                                       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                    [dim #FFFFFF]🛡️  AI-Powered Security Vulnerability Scanner 🛡️[/dim #FFFFFF]                    [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                           [dim #888888]Version 1.0.0 | by itscool2b[/dim #888888]                             [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]║[/bold #FF00FF]                                                                                       [bold #FF00FF]║[/bold #FF00FF]
[bold #FF00FF]╚═══════════════════════════════════════════════════════════════════════════════════════╝[/bold #FF00FF]
    """
    
    console.print(ascii_art)
    
    # Enhanced animated loading with multiple phases
    loading_phases = [
        ("🔧 Initializing security engine", "dots12", "#00FFFF"),
        ("🔍 Loading vulnerability database", "dots8", "#FF00FF"),
        ("⚡ Optimizing detection algorithms", "arc", "#FFD700"),
        ("✨ Ready to protect your code", "star", "#00FF00")
    ]
    
    for text, spinner, color in loading_phases:
        with console.status(f"[bold {color}]{text}[/bold {color}]", spinner=spinner):
            time.sleep(0.3)

def show_no_api_key_message():
    # Animated warning
    console.print()
    console.rule("[bold red]⚠️  CONFIGURATION REQUIRED ⚠️[/bold red]", style="red")
    console.print()
    
    error_panel = Panel(
        "[bold #FF0000]🔐 NO API KEY DETECTED[/bold #FF0000]\n\n"
        "[#FFAAAA]The Anti Shlop Security Agent requires an OpenAI API key to scan for vulnerabilities.[/#FFAAAA]\n\n"
        "[bold #FFD700]Quick Setup:[/bold #FFD700]\n"
        "  [#00FFFF]$[/#00FFFF] python antishlop.py --set-key [#00FF00]YOUR_OPENAI_KEY[/#00FF00]\n\n"
        "[bold #FFD700]Alternative:[/bold #FFD700]\n"
        "  [#00FFFF]$[/#00FFFF] export OPENAI_API_KEY=[#00FF00]your_key_here[/#00FF00]\n\n"
        "[dim #888888]Get your API key at: [link=https://platform.openai.com/api-keys]https://platform.openai.com/api-keys[/link][/dim #888888]",
        title="[bold #FF0000]⚡ API KEY MISSING ⚡[/bold #FF0000]",
        border_style="#FF0000",
        box=DOUBLE_EDGE,
        padding=(1, 2),
        expand=False
    )
    console.print(Align.center(error_panel))

def show_scanning_header(directory):
    # Animated scan initiation
    console.print()
    console.rule("[bold #00FFFF]🔍 SECURITY SCAN INITIATED[/bold #00FFFF]", style="#00FFFF")
    console.print()
    
    # Create animated scanning effect
    with console.status("[bold #FF00FF]Preparing scan environment...[/bold #FF00FF]", spinner="bouncingBall"):
        time.sleep(0.5)
    
    scan_panel = Panel(
        f"[bold #00FF00]📡 TARGET DIRECTORY[/bold #00FF00]\n"
        f"[#00FFFF]{directory}[/#00FFFF]\n\n"
        f"[bold #FFD700]🎯 SCAN MODE:[/bold #FFD700] [#FF00FF]Deep Analysis[/#FF00FF]\n"
        f"[bold #FFD700]⚡ ENGINE:[/bold #FFD700] [#00FF00]GPT-4 Turbo[/#00FF00]\n\n"
        f"[dim #888888]Press [bold]Ctrl+C[/bold] to abort scan[/dim #888888]",
        title="[bold #00FFFF]🚀 SCANNING IN PROGRESS 🚀[/bold #00FFFF]",
        border_style="#00FFFF",
        box=ROUNDED,
        padding=(1, 2),
        expand=False
    )
    console.print(Align.center(scan_panel))
    console.print()

def create_progress_bar():
    return Progress(
        SpinnerColumn(spinner_name="arc", style="bold #FF00FF"),
        TextColumn("[bold #00FFFF]{task.description}[/bold #00FFFF]"),
        BarColumn(
            style="#00FFFF",
            complete_style="bold #00FF00",
            finished_style="bold #00FF00",
            pulse_style="#FF00FF"
        ),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TextColumn("[bold #FFD700]→[/bold #FFD700] [#FFFFFF]{task.fields[current_file]}[/#FFFFFF]"),
        console=console,
        expand=True,
        refresh_per_second=10
    )

def show_vulnerability_found(filepath, line_num, severity, vuln_type, description):
    severity_styles = {
        'critical': ('#FF0000', '💀', 'CRITICAL', 'blink'),
        'high': ('#FF8800', '🔥', 'HIGH', 'bold'),
        'medium': ('#FFD700', '⚡', 'MEDIUM', 'bold'),
        'low': ('#00FFFF', '💡', 'LOW', '')
    }
    
    color, icon, label, extra_style = severity_styles.get(severity, ('#FFFFFF', '🐛', 'UNKNOWN', ''))
    
    # Animated vulnerability notification
    vuln_panel = Panel(
        f"[bold {color}]{icon} {label} VULNERABILITY DETECTED[/bold {color}]\n\n"
        f"[bold #00FFFF]Type:[/bold #00FFFF] [{color}]{vuln_type}[/{color}]\n"
        f"[bold #00FFFF]File:[/bold #00FFFF] [#FFFFFF]{filepath}[/#FFFFFF]\n"
        f"[bold #00FFFF]Line:[/bold #00FFFF] [#FFD700]{line_num}[/#FFD700]\n\n"
        f"[bold #FF00FF]Description:[/bold #FF00FF]\n[#FFAAAA]{description}[/#FFAAAA]",
        border_style=color,
        box=ROUNDED if severity != 'critical' else DOUBLE_EDGE,
        padding=(0, 1),
        expand=False
    )
    
    if severity == 'critical':
        # Extra emphasis for critical vulnerabilities
        console.print()
        console.rule(f"[{color} {extra_style}]⚠️  CRITICAL SECURITY ISSUE ⚠️[/{color}]", style=color)
    
    console.print(vuln_panel)
    console.print()

def show_summary(total_files, total_vulnerabilities, scan_time):
    console.print("\n")
    console.rule("[bold #00FFFF]📊 SCAN RESULTS 📊[/bold #00FFFF]", style="#00FFFF")
    console.print("\n")
    
    # Animated summary statistics
    stats_table = Table(box=MINIMAL_HEAVY_HEAD, border_style="#00FFFF", expand=False)
    stats_table.add_column("Metric", style="bold #FFD700", justify="left")
    stats_table.add_column("Value", style="bold #FFFFFF", justify="right")
    
    stats_table.add_row("📁 Files Analyzed", f"{total_files:,}")
    stats_table.add_row("🐛 Vulnerabilities Found", f"{total_vulnerabilities:,}")
    stats_table.add_row("⏱️  Scan Duration", f"{scan_time:.2f}s")
    stats_table.add_row("⚡ Scan Speed", f"{total_files/scan_time:.1f} files/sec")
    
    console.print(Align.center(stats_table))
    console.print("\n")
    
    if total_vulnerabilities == 0:
        # Success animation
        success_panel = Panel(
            "[bold #00FF00]🛡️  SECURE CODE DETECTED 🛡️[/bold #00FF00]\n\n"
            "[#00FF00]✨ No security vulnerabilities found![/#00FF00]\n"
            "[#00FF00]Your code has passed all security checks.[/#00FF00]",
            border_style="#00FF00",
            box=DOUBLE_EDGE,
            padding=(1, 3),
            expand=False
        )
        console.print(Align.center(success_panel))
        
        # Victory animation
        with console.status("[bold #00FF00]🎉 Celebrating secure code...[/bold #00FF00]", spinner="star"):
            time.sleep(1)
    else:
        # Warning animation
        severity_color = "#FF0000" if total_vulnerabilities > 10 else "#FF8800" if total_vulnerabilities > 5 else "#FFD700"
        
        warning_panel = Panel(
            f"[bold {severity_color}]🚨 {total_vulnerabilities} VULNERABILITIES DETECTED 🚨[/bold {severity_color}]\n\n"
            f"[{severity_color}]⚠️  Immediate action required![/{severity_color}]\n"
            f"[#FFAAAA]Review the vulnerabilities above and fix them.[/#FFAAAA]",
            border_style=severity_color,
            box=DOUBLE_EDGE,
            padding=(1, 3),
            expand=False
        )
        console.print(Align.center(warning_panel))
        
        # Alert animation
        for _ in range(3):
            console.print(f"[{severity_color}]⚠️[/{severity_color}]", end="\r")
            time.sleep(0.2)
            console.print("  ", end="\r")
            time.sleep(0.2)

def show_analyzing_file(filename):
    # Animated file analysis indicator
    console.print(f"[bold #00FFFF]🔬[/bold #00FFFF] [#FF00FF]Analyzing:[/#FF00FF] [#FFFFFF]{filename}[/#FFFFFF]", end="\r")

def show_error(message):
    console.print()
    console.rule("[bold #FF0000]❌ ERROR OCCURRED ❌[/bold #FF0000]", style="#FF0000")
    
    error_panel = Panel(
        f"[bold #FF0000]{message}[/bold #FF0000]",
        border_style="#FF0000",
        box=DOUBLE_EDGE,
        padding=(1, 2),
        expand=False
    )
    console.print(Align.center(error_panel))
    console.print()

def show_success(message):
    success_text = Text()
    success_text.append("✅ ", "bold #00FF00")
    success_text.append(message, "#00FF00")
    console.print(success_text)
    
    # Quick success animation
    with console.status("[bold #00FF00]✨[/bold #00FF00]", spinner="point"):
        time.sleep(0.3)

def show_api_key_set():
    console.print()
    console.rule("[bold #00FF00]✅ CONFIGURATION COMPLETE ✅[/bold #00FF00]", style="#00FF00")
    console.print()
    
    # Animated success message
    with console.status("[bold #00FF00]Validating API key...[/bold #00FF00]", spinner="dots"):
        time.sleep(0.5)
    
    key_panel = Panel(
        "[bold #00FF00]✅ API KEY CONFIGURED SUCCESSFULLY![/bold #00FF00]\n\n"
        "[#00FFFF]The Anti Shlop Security Agent is now ready to protect your code.[/#00FFFF]\n\n"
        "[bold #FFD700]Next Step:[/bold #FFD700]\n"
        "[#FFFFFF]Run [bold #00FFFF]python antishlop.py[/bold #00FFFF] to start scanning[/#FFFFFF]",
        title="[bold #00FF00]🚀 READY TO PROTECT 🚀[/bold #00FF00]",
        border_style="#00FF00",
        box=DOUBLE_EDGE,
        padding=(1, 2),
        expand=False
    )
    console.print(Align.center(key_panel))
    console.print()

def clear_line():
    console.print(" " * 100, end="\r")

def show_file_stats(stats):
    """Display file statistics with animations"""
    console.print()
    console.rule("[bold #00FFFF]📊 PROJECT ANALYSIS 📊[/bold #00FFFF]", style="#00FFFF")
    console.print()
    
    # Animated stats loading
    with console.status("[bold #FF00FF]Analyzing project structure...[/bold #FF00FF]", spinner="dots"):
        time.sleep(0.3)
    
    # Main statistics table with gradient colors
    stats_table = Table(
        title="[bold #00FFFF]📁 PROJECT METRICS[/bold #00FFFF]",
        box=MINIMAL_HEAVY_HEAD,
        border_style="#00FFFF",
        title_style="bold #00FFFF",
        expand=False
    )
    
    stats_table.add_column("Metric", style="#FFD700", justify="left")
    stats_table.add_column("Value", style="bold #FFFFFF", justify="right")
    
    stats_table.add_row("📁 Total Files", f"{stats['total_files']:,}")
    stats_table.add_row("💾 Total Size", f"{stats['total_size'] / 1024 / 1024:.2f} MB")
    stats_table.add_row("📄 Largest File", f"{stats.get('largest_file', 'N/A')}")
    
    console.print(Align.center(stats_table))
    console.print()
    
    if stats.get('by_extension'):
        # File types breakdown with visual bars
        ext_panel = Panel(
            title="[bold #FF00FF]🎯 FILE TYPE DISTRIBUTION[/bold #FF00FF]",
            border_style="#FF00FF",
            box=ROUNDED,
            padding=(0, 1)
        )
        
        content = ""
        max_count = max(stats['by_extension'].values())
        
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:5]:
            ext_name = ext or "no extension"
            bar_length = int((count / max_count) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            content += f"[#FFD700]{ext_name:12}[/#FFD700] [{get_extension_color(ext)}]{bar}[/] [#FFFFFF]{count:4}[/#FFFFFF]\n"
        
        ext_panel.renderable = content.strip()
        console.print(Align.center(ext_panel))

def get_extension_color(ext):
    """Get color for file extension"""
    colors = {
        '.py': '#00FF00',
        '.js': '#FFD700',
        '.ts': '#00FFFF',
        '.jsx': '#FF00FF',
        '.tsx': '#FF00FF',
        '.html': '#FF8800',
        '.css': '#00AAFF',
        '.json': '#AAFFAA',
        '.yml': '#FFAAAA',
        '.yaml': '#FFAAAA',
    }
    return colors.get(ext, '#FFFFFF')