from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
from typing_extensions import TypedDict
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
import re
import hashlib
from datetime import datetime
from .prompts import (
    ORCHESTRATOR_PROMPT,
    PATTERN_DETECTION_PROMPT,
    CONTEXT_ANALYSIS_PROMPT,
    COMPLIANCE_AGENT_PROMPT,
    GENERATION_PROMPT
)

# Global LLM instance - will be initialized with user's API key
llm = None

class AgentState(TypedDict):
    """Simple state for security analysis workflow"""
    
    # Current file being processed
    file_path: str
    file_content: str
    language: str
    framework: str
    
    # All files to process
    all_files: List[Dict[str, str]]  # [{"path": "...", "content": "..."}]
    current_file_index: int
    
    # Results (accumulated across all files)
    vulnerabilities: List[Dict[str, Any]]
    
    # Workflow control
    current_agent: str  # "pattern", "context", "compliance", "generation"
    pattern_complete: bool
    context_complete: bool  # Track if context analysis done for current file
    compliance_complete: bool  # Track if compliance analysis done for current file
    file_complete: bool  # Current file analysis complete
    all_files_complete: bool  # All files processed
    complete: bool  # Entire analysis complete



def parse_orchestrator_output(llm_output: str, current_state: AgentState) -> AgentState:
    import json
    
    try:
        
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in orchestrator output")
        
        json_str = llm_output[json_start:json_end]
        parsed = json.loads(json_str)
        
        
        # Don't trust LLM to return all_files correctly - keep original
        updated_state = AgentState(
            file_path=parsed.get('file_path', current_state['file_path']),
            file_content=parsed.get('file_content', current_state['file_content']),
            language=parsed.get('language', current_state.get('language', 'Unknown')),
            framework=parsed.get('framework', current_state.get('framework', 'unknown')),
            all_files=current_state.get('all_files', []),  # Always use current state for file list
            current_file_index=parsed.get('current_file_index', current_state.get('current_file_index', 0)),
            vulnerabilities=parsed.get('vulnerabilities', current_state.get('vulnerabilities', [])),
            current_agent=parsed.get('current_agent', 'patterndetectionagent'),
            pattern_complete=parsed.get('pattern_complete', current_state.get('pattern_complete', False)),
            context_complete=parsed.get('context_complete', current_state.get('context_complete', False)),
            compliance_complete=parsed.get('compliance_complete', current_state.get('compliance_complete', False)),
            file_complete=parsed.get('file_complete', False),
            all_files_complete=parsed.get('all_files_complete', False),
            complete=parsed.get('complete', False)
        )
        
        return updated_state
        
    except json.JSONDecodeError as e:
        return AgentState(
            file_path=current_state['file_path'],
            file_content=current_state['file_content'],
            language=current_state.get('language', 'Unknown'),
            framework=current_state.get('framework', 'unknown'),
            all_files=current_state.get('all_files', []),
            current_file_index=current_state.get('current_file_index', 0),
            vulnerabilities=current_state.get('vulnerabilities', []),
            current_agent='patterndetectionagent',  
            pattern_complete=False,
            file_complete=False,
            all_files_complete=False,
            complete=False
        )
    except Exception as e:
        return current_state


def orchestrator(state):
    try:
        from .ui import console
        import time
        
        current_file = state['current_file_index'] + 1
        total_files = len(state['all_files'])
        current_path = state.get('file_path', 'Unknown')
        
        console.print(f"[cyan]📁 Analyzing file {current_file}/{total_files}: [bold]{current_path.split('/')[-1]}[/bold][/cyan]")
        
        console.print("[dim]🤖 Orchestrator preparing analysis state...[/dim]")
        state_str = json.dumps(state, indent=2)
        prompt = ORCHESTRATOR_PROMPT.format(state=state_str)
        
        console.print("[dim]📡 Making API call to OpenAI...[/dim]")
        start_time = time.time()
        response = llm.invoke(prompt)
        api_time = time.time() - start_time
        console.print(f"[dim]✅ API response received ({api_time:.1f}s)[/dim]")
        
        console.print("[dim]🔄 Parsing orchestrator response and updating state...[/dim]")
        updated_state = parse_orchestrator_output(response.content, state)
        
        # Handle file transitions
        if updated_state['current_file_index'] != state['current_file_index']:
            next_index = updated_state['current_file_index']
            console.print(f"[dim]🔄 Transitioning to file {next_index + 1}...[/dim]")
            
            if next_index < len(state['all_files']):
                next_file = state['all_files'][next_index]
                
                if isinstance(next_file, dict) and 'path' in next_file and 'content' in next_file:
                    state['file_path'] = next_file['path']
                    state['file_content'] = next_file['content']
                    console.print(f"[green]✅ Completed analysis of {current_path.split('/')[-1]}[/green]")
                    console.print(f"[dim]📄 Loading next file: {next_file['path'].split('/')[-1]}[/dim]")
                else:
                    console.print("[yellow]⚠️  Invalid file structure, skipping...[/yellow]")
                    if next_index + 1 < len(state['all_files']):
                        state['current_file_index'] = next_index + 1
                        return state
                    else:
                        state['all_files_complete'] = True
                        return state
                        
                console.print("[dim]🔄 Resetting analysis state for new file...[/dim]")
                state['language'] = None
                state['framework'] = None
                state['pattern_complete'] = False
                state['context_complete'] = False
                state['compliance_complete'] = False
                state['file_complete'] = False
            else:
                state['all_files_complete'] = True
                console.print("[green]✅ All files analyzed! Preparing final report...[/green]")
        
        console.print("[dim]📝 Updating state with orchestrator decisions...[/dim]")
        # Update state fields
        state['language'] = updated_state.get('language') or state.get('language')
        state['framework'] = updated_state.get('framework') or state.get('framework')
        state['vulnerabilities'] = updated_state['vulnerabilities']
        state['current_agent'] = updated_state['current_agent']
        state['current_file_index'] = updated_state['current_file_index']
        state['pattern_complete'] = updated_state['pattern_complete']
        state['context_complete'] = updated_state['context_complete']
        state['compliance_complete'] = updated_state['compliance_complete']
        state['file_complete'] = updated_state['file_complete']
        state['all_files_complete'] = updated_state['all_files_complete']
        state['complete'] = updated_state['complete']
        
        next_agent = state['current_agent']
        reasoning = updated_state.get('decision_reasoning', 'No reasoning provided')
        
        console.print(f"[bold blue]🎯 Next agent: {next_agent}[/bold blue]")
        console.print(f"[dim]💭 Reasoning: {reasoning}[/dim]")
        
        return state
    except Exception as e:
        state['complete'] = True
        return state





def patterndetectionagent(state):
    """
    Fast pattern-based vulnerability detection
    """
    from .ui import console
    import time
    
    console.print("[yellow]🔍 Running pattern detection analysis...[/yellow]")
    
    console.print("[dim]📝 Preparing pattern detection prompt...[/dim]")
    state_str = json.dumps(state, indent=2)
    prompt = PATTERN_DETECTION_PROMPT.format(state=state_str)
    
    console.print("[dim]📡 Calling OpenAI for pattern analysis...[/dim]")
    start_time = time.time()
    response = llm.invoke(prompt)
    api_time = time.time() - start_time
    console.print(f"[dim]✅ Pattern analysis response received ({api_time:.1f}s)[/dim]")
    
    console.print("[dim]🔄 Parsing vulnerability findings...[/dim]")
    try:
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_str = response.content[json_start:json_end]
        result = json.loads(json_str)
        
        existing_vulns = state.get('vulnerabilities', [])
        new_vulns = result.get('vulnerabilities', [])
        
        console.print(f"[dim]📊 Processing {len(new_vulns)} new findings...[/dim]")
        
        # Add file path to each vulnerability
        for vuln in new_vulns:
            if 'file_path' not in vuln or vuln['file_path'] == 'unknown':
                vuln['file_path'] = state.get('file_path', 'unknown')
        
        state['vulnerabilities'] = existing_vulns + new_vulns
        state['pattern_complete'] = True
        
        if new_vulns:
            console.print(f"[red]⚠️  Found {len(new_vulns)} vulnerabilities in pattern analysis[/red]")
            for vuln in new_vulns[:3]:  # Show first 3
                console.print(f"[dim]  • {vuln.get('type', 'Unknown')} (Line {vuln.get('line', '?')})[/dim]")
            if len(new_vulns) > 3:
                console.print(f"[dim]  • ... and {len(new_vulns) - 3} more[/dim]")
        else:
            console.print("[green]✅ No vulnerabilities found in pattern analysis[/green]")
        
    except Exception as e:
        state['pattern_complete'] = True
        console.print("[yellow]⚠️  Pattern analysis completed with errors[/yellow]")
    
    return state


def contextanalysisagent(state):
    from .ui import console
    import time
    
    console.print("[blue]🧠 Running deep context analysis...[/blue]")
    
    console.print("[dim]📝 Building context analysis prompt with data flows...[/dim]")
    state_str = json.dumps(state, indent=2)
    prompt = CONTEXT_ANALYSIS_PROMPT.format(state=state_str)
    
    console.print("[dim]📡 Calling OpenAI for deep context analysis...[/dim]")
    start_time = time.time()
    response = llm.invoke(prompt)
    api_time = time.time() - start_time
    console.print(f"[dim]✅ Context analysis response received ({api_time:.1f}s)[/dim]")
    
    console.print("[dim]🔄 Processing complex vulnerability patterns...[/dim]")
    try:
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_str = response.content[json_start:json_end]
        result = json.loads(json_str)
        
        existing_vulns = state.get('vulnerabilities', [])
        new_vulns = result.get('vulnerabilities', [])
        
        context_vulns = [
            v for v in new_vulns 
            if v not in existing_vulns and v.get('requires_context', False)
        ]
        
        console.print(f"[dim]📊 Filtering {len(new_vulns)} findings for context-specific issues...[/dim]")
        state['vulnerabilities'] = existing_vulns + context_vulns
        state['context_complete'] = True  # Mark context analysis as done
        
        if context_vulns:
            console.print(f"[red]⚠️  Found {len(context_vulns)} additional vulnerabilities in context analysis[/red]")
            for vuln in context_vulns[:2]:  # Show first 2
                console.print(f"[dim]  • {vuln.get('type', 'Unknown')} - {vuln.get('description', '')[:50]}...[/dim]")
        else:
            console.print("[green]✅ No additional vulnerabilities found in context analysis[/green]")
        
    except Exception as e:
        console.print("[yellow]⚠️  Context analysis completed with errors[/yellow]")
        state['context_complete'] = True  # Mark as done even with errors
    
    return state



def complianceagent(state):
    """
    Enrich vulnerabilities with compliance and standards mappings
    """
    from .ui import console
    import time
    
    console.print("[magenta]📋 Adding compliance mappings...[/magenta]")
    
    console.print("[dim]📝 Mapping vulnerabilities to OWASP/CWE standards...[/dim]")
    state_str = json.dumps(state, indent=2)
    prompt = COMPLIANCE_AGENT_PROMPT.format(state=state_str)
    
    console.print("[dim]📡 Calling OpenAI for compliance enrichment...[/dim]")
    start_time = time.time()
    response = llm.invoke(prompt)
    api_time = time.time() - start_time
    console.print(f"[dim]✅ Compliance mapping response received ({api_time:.1f}s)[/dim]")
    
    console.print("[dim]🔄 Adding CVSS scores and compliance tags...[/dim]")
    try:
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_str = response.content[json_start:json_end]
        result = json.loads(json_str)
        
        state['vulnerabilities'] = result.get('vulnerabilities', state['vulnerabilities'])
        state['compliance_complete'] = True  # Mark compliance analysis as done
        console.print(f"[green]✅ Enriched {len(state['vulnerabilities'])} vulnerabilities with compliance data[/green]")
        
        # Show compliance summary
        severities = {}
        for vuln in state['vulnerabilities']:
            sev = vuln.get('severity', 'unknown')
            severities[sev] = severities.get(sev, 0) + 1
        
        if severities:
            severity_str = ", ".join([f"{count} {sev}" for sev, count in severities.items()])
            console.print(f"[dim]📊 Severity breakdown: {severity_str}[/dim]")
        
    except Exception as e:
        console.print("[yellow]⚠️  Compliance analysis completed with errors[/yellow]")
        state['compliance_complete'] = True  # Mark as done even with errors
    
    return state


def generation(state):
    """
    Generate comprehensive final report with all findings
    """
    from .ui import console
    import time
    
    console.print("[cyan]📝 Generating comprehensive security report...[/cyan]")
    
    console.print("[dim]📝 Consolidating all vulnerability findings...[/dim]")
    total_vulns = len(state.get('vulnerabilities', []))
    console.print(f"[dim]📊 Preparing report for {total_vulns} total vulnerabilities...[/dim]")
    
    state_str = json.dumps(state, indent=2)
    prompt = GENERATION_PROMPT.format(state=state_str)
    
    console.print("[dim]📡 Calling OpenAI for final report generation...[/dim]")
    start_time = time.time()
    response = llm.invoke(prompt)
    api_time = time.time() - start_time
    console.print(f"[dim]✅ Report generation response received ({api_time:.1f}s)[/dim]")
    
    console.print("[dim]🔄 Formatting comprehensive security report...[/dim]")
    try:
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_str = response.content[json_start:json_end]
        report = json.loads(json_str)
        
        # Store both the final report AND keep vulnerabilities accessible
        state['final_report'] = report
        # Ensure vulnerabilities remain at top level for main script access
        if 'vulnerabilities' not in state:
            state['vulnerabilities'] = []
        state['complete'] = True
        
        console.print("[bold green]✅ Security analysis complete![/bold green]")
        console.print(f"[bold green]📄 Final report generated with {total_vulns} vulnerability findings[/bold green]")
        
        # Also add the report summary to state for easy access
        if report and 'executive_summary' in report:
            console.print(f"[dim]📋 Report includes executive summary and detailed findings[/dim]")
        
    except Exception as e:
        state['complete'] = True
        console.print("[yellow]⚠️  Report generation completed with errors[/yellow]")
        console.print(f"[dim]🔧 Keeping {total_vulns} vulnerabilities accessible for display[/dim]")
    
    return state

def antishlopper(all_files, api_key):
    """
    Analyze multiple files for security vulnerabilities using agent pipeline
    
    Args:
        all_files: List of {"path": str, "content": str} dictionaries
        api_key: OpenAI API key
    
    Returns:
        Final state with all vulnerabilities found across all files
    """
    global llm
    llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0)
    
    # Start with first file
    first_file = all_files[0] if all_files else {"path": "", "content": ""}
    
    try:
        state = {
            'file_path': first_file['path'],
            'file_content': first_file['content'],
            'language': None,
            'framework': None,
            'all_files': all_files,
            'current_file_index': 0,
            'vulnerabilities': [],
            'current_agent': None,
            'pattern_complete': False,
            'context_complete': False,
            'compliance_complete': False,
            'file_complete': False,
            'all_files_complete': False,
            'complete': False
        }
    except Exception as e:
        return {'vulnerabilities': []}
    
    from .ui import console
    
    console.print("[bold cyan]🚀 Starting multi-agent security analysis...[/bold cyan]\n")
    
    iteration_count = 0
    max_iterations = 100  # Safety net to prevent infinite loops
    
    while not state['complete'] and iteration_count < max_iterations:
        iteration_count += 1
        
        # Let the orchestrator make intelligent decisions
        state = orchestrator(state)
        
        # Execute the agent chosen by the orchestrator
        if state['current_agent'] == 'patterndetectionagent':
            state = patterndetectionagent(state)
        elif state['current_agent'] == 'contextanalysisagent':
            state = contextanalysisagent(state)
        elif state['current_agent'] == 'complianceagent':
            state = complianceagent(state)
        elif state['current_agent'] == 'generation':
            state = generation(state)
            state['complete'] = True  
        else:
            console.print(f"[yellow]⚠️  Unknown agent '{state['current_agent']}', completing analysis[/yellow]")
            break
    
    if iteration_count >= max_iterations:
        console.print("[red]⚠️  Max iterations reached, completing analysis[/red]")
        state['complete'] = True
    
    return state