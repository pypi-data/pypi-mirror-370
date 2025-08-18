#!/usr/bin/env python3

import argparse
import os
import sys
import time
import glob
from pathlib import Path

from .config import get_api_key, set_api_key, validate_api_key
from .agent import antishlopper
from .ui import (
    show_banner,
    show_no_api_key_message,
    show_scanning_header,
    create_progress_bar,
    show_vulnerability_found,
    show_summary,
    show_analyzing_file,
    show_error,
    show_success,
    show_api_key_set,
    clear_line,
    console
)

def get_code_files(directory):
    """Recursively find all code files in directory"""
    code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.php', '.go', '.sql', '.rb', '.cs', '.cpp', '.c', '.h'}
    files = []
    
    for ext in code_extensions:
        pattern = os.path.join(directory, f"**/*{ext}")
        files.extend(glob.glob(pattern, recursive=True))
    
    return sorted(files)

def read_file_safely(filepath):
    """Read file content safely, handling encoding issues"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return ""
    except:
        return ""

def collect_all_files(directory):
    """Collect all code files with their content"""
    file_paths = get_code_files(directory)
    all_files = []
    
    for filepath in file_paths:
        content = read_file_safely(filepath)
        if content.strip():  # Only include non-empty files
            all_files.append({
                'path': filepath,
                'content': content
            })
    
    return all_files

def main():
    parser = argparse.ArgumentParser(
        description='Anti-Shlop Security Agent - AI-powered security vulnerability scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to directory to scan (default: current directory)'
    )
    
    parser.add_argument(
        '--set-key',
        dest='api_key',
        help='Set your OpenAI API key'
    )
    
    parser.add_argument(
        '--show-stats',
        action='store_true',
        help='Show file statistics before scanning'
    )
    
    parser.add_argument(
        '--output',
        choices=['terminal', 'json', 'html'],
        default='terminal',
        help='Output format (default: terminal)'
    )
    
    args = parser.parse_args()
    
    # Always show banner
    show_banner()
    
    # Handle API key setting
    if args.api_key:
        if validate_api_key(args.api_key):
            set_api_key(args.api_key)
            show_api_key_set()
            show_success("You can now run 'python antishlop.py' to scan your code!")
        else:
            show_error("Invalid API key format. Keys should start with 'sk-'")
        return
    
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        show_no_api_key_message()
        sys.exit(1)
    
    # Validate the path
    scan_path = os.path.abspath(args.path)
    if not os.path.exists(scan_path):
        show_error(f"Path does not exist: {scan_path}")
        sys.exit(1)
    
    if not os.path.isdir(scan_path):
        show_error(f"Path is not a directory: {scan_path}")
        sys.exit(1)
    
    # Show what we're scanning
    show_scanning_header(scan_path)
    
    # Collect all files to analyze
    console.print("[dim]Collecting code files...[/dim]")
    all_files = collect_all_files(scan_path)
    
    
    if not all_files:
        show_error("No code files found to analyze!")
        sys.exit(1)
    
    console.print(f"[bold green]Found {len(all_files)} files to scan for security vulnerabilities[/bold green]\n")
    
    # Run complete security analysis on all files
    console.print("[bold cyan]🔍 Starting comprehensive security analysis...[/bold cyan]")
    console.print(f"[dim]Files to analyze: {', '.join([f['path'].split('/')[-1] for f in all_files[:3]])}{' and ' + str(len(all_files)-3) + ' more...' if len(all_files) > 3 else ''}[/dim]\n")
    start_time = time.time()
    
    try:
        # Run the agent pipeline on all files
        result = antishlopper(all_files, api_key)
        
        console.print(f"\n[bold cyan]📊 Analysis Results Summary[/bold cyan]")
        
        # Extract all vulnerabilities found
        all_vulnerabilities_list = result.get('vulnerabilities', [])
        
        # Also check if there's a final report with more details
        final_report = result.get('final_report', {})
        if final_report:
            console.print("[dim]📋 Comprehensive report generated successfully[/dim]")
            exec_summary = final_report.get('executive_summary', {})
            if exec_summary:
                console.print(f"[dim]📈 Total vulnerabilities: {exec_summary.get('total_vulnerabilities', len(all_vulnerabilities_list))}[/dim]")
        
        console.print(f"[bold]🔍 Found {len(all_vulnerabilities_list)} total vulnerabilities across all files[/bold]\n")
        
        # Group vulnerabilities by file for display
        all_vulnerabilities = {}
        for vuln in all_vulnerabilities_list:
            filepath = vuln.get('file_path', 'unknown')
            if filepath not in all_vulnerabilities:
                all_vulnerabilities[filepath] = []
            all_vulnerabilities[filepath].append(vuln)
        
        # Display vulnerabilities as they're found
        for filepath, vulnerabilities in all_vulnerabilities.items():
            for vuln in vulnerabilities:
                show_vulnerability_found(
                    filepath,
                    vuln.get('line', 0),
                    vuln.get('severity', 'medium'),
                    vuln.get('type', 'Security Issue'),
                    vuln.get('description', 'Unknown vulnerability')
                )
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        all_vulnerabilities = {}
        all_vulnerabilities_list = []
    except Exception as e:
        show_error(f"Error during analysis: {str(e)}")
        sys.exit(1)
    
    # Calculate scan time
    scan_time = time.time() - start_time
    
    # Show summary
    total_vulnerabilities = sum(len(vulns) for vulns in all_vulnerabilities.values())
    show_summary(len(all_files), total_vulnerabilities, scan_time)
    
    # Output in different formats if requested
    if args.output == 'json':
        import json
        output = {
            'scan_path': scan_path,
            'files_scanned': len(all_files),
            'vulnerabilities': all_vulnerabilities,
            'final_report': final_report,
            'scan_time': scan_time
        }
        console.print("\n[bold cyan]JSON Output:[/bold cyan]")
        console.print(json.dumps(output, indent=2))
    
    elif args.output == 'html':
        # TODO: Implement HTML report generation
        console.print("[yellow]HTML output not yet implemented[/yellow]")
    
    # Display final report summary if available
    if final_report and args.output == 'terminal':
        console.print(f"\n[bold cyan]📋 Final Security Report Summary[/bold cyan]")
        exec_summary = final_report.get('executive_summary', {})
        if exec_summary:
            console.print(f"[green]📈 Risk Level: {exec_summary.get('overall_risk_level', 'Unknown')}[/green]")
            
            # Show key findings if available
            key_findings = exec_summary.get('key_findings', [])
            if key_findings:
                console.print(f"[yellow]🔍 Top Issues:[/yellow]")
                for i, finding in enumerate(key_findings[:3], 1):
                    console.print(f"  {i}. {finding}")
        
        # Show remediation info if available
        remediation = final_report.get('remediation_roadmap', {})
        if remediation and remediation.get('critical_fixes'):
            console.print(f"[red]🚨 Critical Fixes Needed: {len(remediation.get('critical_fixes', []))}[/red]")

if __name__ == '__main__':
    main()