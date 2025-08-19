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
        # Also ensure current_agent is never None
        next_agent = parsed.get('current_agent')
        if not next_agent or next_agent == 'None':
            # Default to pattern detection if not specified
            next_agent = 'patterndetectionagent'
        
        updated_state = AgentState(
            file_path=parsed.get('file_path', current_state['file_path']),
            file_content=parsed.get('file_content', current_state['file_content']),
            language=parsed.get('language', current_state.get('language', 'Unknown')),
            framework=parsed.get('framework', current_state.get('framework', 'unknown')),
            all_files=current_state.get('all_files', []),  # Always use current state for file list
            current_file_index=parsed.get('current_file_index', current_state.get('current_file_index', 0)),
            vulnerabilities=parsed.get('vulnerabilities', current_state.get('vulnerabilities', [])),
            current_agent=next_agent,
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
            context_complete=False,
            compliance_complete=False,
            file_complete=False,
            all_files_complete=False,
            complete=False
        )
    except Exception as e:
        # Ensure we always have a valid agent to avoid None errors
        if not current_state.get('current_agent'):
            current_state['current_agent'] = 'patterndetectionagent'
        return current_state


def orchestrator(state):
    from .ui import console
    import time
    
    current_file = state['current_file_index'] + 1
    total_files = len(state['all_files'])
    current_path = state.get('file_path', 'Unknown')
    filename = current_path.split('/')[-1]
    
    console.print(f"Orchestrator analyzing file {current_file}/{total_files}: {filename}")
    
    state_str = json.dumps(state, indent=2)
    # Fix: Use format() method properly
    if ORCHESTRATOR_PROMPT and hasattr(ORCHESTRATOR_PROMPT, 'template'):
        formatted_prompt = ORCHESTRATOR_PROMPT.template.format(state=state_str)
    else:
        # Fallback prompt if template is missing
        formatted_prompt = f"Analyze this state and decide the next agent to run: {state_str}"
    
    original_file_index = state['current_file_index']
    
    try:
        if not formatted_prompt:
            raise ValueError("Empty prompt")
        response = llm.invoke(formatted_prompt)
        content = response.content if response and response.content else ""
        parsed = parse_orchestrator_output(content.strip(), state)
    except Exception as e:
        console.print(f"Error in orchestrator: {str(e)}")
        # Fallback: move to pattern detection with full state
        parsed = dict(state)
        parsed['current_agent'] = 'patterndetectionagent'
        parsed['pattern_complete'] = False
        parsed['context_complete'] = False
        parsed['compliance_complete'] = False
        parsed['file_complete'] = False
        parsed['all_files_complete'] = False
        parsed['complete'] = False

    state['file_path'] = parsed['file_path']
    state['file_content'] = parsed['file_content']
    state['language'] = parsed['language']
    state['framework'] = parsed['framework']
    state['all_files'] = parsed['all_files']
    state['current_file_index'] = parsed['current_file_index']
    state['vulnerabilities'] = parsed['vulnerabilities']
    state['current_agent'] = parsed['current_agent']
    state['pattern_complete'] = parsed['pattern_complete']
    state['file_complete'] = parsed['file_complete']
    state['all_files_complete'] = parsed['all_files_complete']
    state['complete'] = parsed['complete']
    state['context_complete'] = parsed['context_complete']
    state['compliance_complete'] = parsed['compliance_complete']

    if state['current_file_index'] != original_file_index:
        # Moving to next file - load its content
        if state['current_file_index'] < len(state['all_files']):
            next_file = state['all_files'][state['current_file_index']]
            state['file_path'] = next_file['path']
            state['file_content'] = next_file['content']
            next_filename = next_file['path'].split('/')[-1]
            console.print(f"[bold #00FF00]✅ Moving to: {next_filename}[/bold #00FF00]")
        else:
            next_filename = 'Report'
            console.print(f"[bold #00FF00]✅ Moving to: {next_filename}[/bold #00FF00]")
        
        # Reset all completion flags for new file
        state['pattern_complete'] = False
        state['context_complete'] = False
        state['compliance_complete'] = False
        state['file_complete'] = False
    
    # Show next agent decision
    next_agent = state.get('current_agent')
    if not next_agent:
        console.print("[bold red]⚠️ Warning: No agent selected, defaulting to pattern detection[/bold red]")
        state['current_agent'] = 'patterndetectionagent'
        next_agent = 'patterndetectionagent'
    
    agent_colors = {
        'patterndetectionagent': '#FFD700',
        'contextanalysisagent': '#00FFFF', 
        'complianceagent': '#FF00FF',
        'generation': '#00FF00'
    }
    agent_color = agent_colors.get(next_agent, '#FFFFFF')
    next_agent_display = next_agent.replace('agent', ' agent').title() if next_agent else 'Unknown'
    console.print(f"[bold {agent_color}]🚀 Next: {next_agent_display}[/bold {agent_color}]")
    
    return state





def patterndetectionagent(state):
    from .ui import console
    import time
    
    filename = state.get('file_path', 'unknown').split('/')[-1]
    console.print(f"[bold #FFD700]🔍 Pattern Detection: [bold #FFFFFF]{filename}[/bold #FFFFFF][/bold #FFD700]")
    
    state_str = json.dumps(state, indent=2)
    formatted_prompt = PATTERN_DETECTION_PROMPT.format(state=state_str) if PATTERN_DETECTION_PROMPT else ""
    
    with console.status("[bold #FFD700]⚡ Scanning for vulnerability patterns...[/bold #FFD700]", spinner="arc"):
        response = llm2.invoke(formatted_prompt)
    
    state['pattern_complete'] = True
    
    content = response.content if response and response.content else ""
    parsed = parse_orchestrator_output(content.strip(), state)
    new_vulns = parsed.get('vulnerabilities', [])
    
    if new_vulns:
        console.print(f"[bold #FF8800]⚠️  Found {len(new_vulns)} pattern-based vulnerabilities[/bold #FF8800]")
    else:
        console.print("[bold #00FF00]✅ No pattern vulnerabilities detected[/bold #00FF00]")
    
    state['vulnerabilities'].extend(new_vulns)
    return state


def contextanalysisagent(state):
    from .ui import console
    import time
    
    filename = state.get('file_path', 'unknown').split('/')[-1]
    console.print(f"[bold #00FFFF]🧠 Deep Context Analysis: [bold #FFFFFF]{filename}[/bold #FFFFFF][/bold #00FFFF]")
    
    state_str = json.dumps(state, indent=2)
    formatted_prompt = CONTEXT_ANALYSIS_PROMPT.format(state=state_str) if CONTEXT_ANALYSIS_PROMPT else ""
    
    with console.status("[bold #00FFFF]🔬 Analyzing data flows and business logic...[/bold #00FFFF]", spinner="bouncingBall"):
        response = llm.invoke(formatted_prompt)
    
    content = response.content if response and response.content else ""
    parsed = parse_orchestrator_output(content.strip(), state)
    state['context_complete'] = True
    
    new_vulns = parsed.get('vulnerabilities', [])
    
    if new_vulns:
        console.print(f"[bold #FF8800]🎯 Found {len(new_vulns)} context-aware vulnerabilities[/bold #FF8800]")
    else:
        console.print("[bold #00FF00]✅ No context vulnerabilities found[/bold #00FF00]")
    
    state['vulnerabilities'].extend(new_vulns)
    return state



def complianceagent(state):
    from .ui import console
    import time
    
    total_vulns = len(state.get('vulnerabilities', []))
    console.print(f"[bold #FF00FF]📋 Compliance Mapping: [bold #FFFFFF]{total_vulns} vulnerabilities[/bold #FFFFFF][/bold #FF00FF]")
    
    state_str = json.dumps(state, indent=2)
    formatted_prompt = COMPLIANCE_AGENT_PROMPT.format(state=state_str) if COMPLIANCE_AGENT_PROMPT else ""
    
    with console.status("[bold #FF00FF]📊 Adding OWASP/CWE mappings and CVSS scores...[/bold #FF00FF]", spinner="dots12"):
        response = llm.invoke(formatted_prompt)
    
    content = response.content if response and response.content else ""
    parsed = parse_orchestrator_output(content.strip(), state)
    state['compliance_complete'] = True
    
    # For compliance, we update existing vulnerabilities rather than add new ones
    enriched_vulns = parsed.get('vulnerabilities', state['vulnerabilities'])
    state['vulnerabilities'] = enriched_vulns
    
    console.print(f"[bold #00FF00]✅ Compliance data added to {total_vulns} vulnerabilities[/bold #00FF00]")
    
    return state



def generation(state):
    from .ui import console
    import time
    
    total_vulns = len(state.get('vulnerabilities', []))
    total_files = len(state.get('all_files', []))
    
    console.print(f"[bold #00FF00]📝 Final Report Generation[/bold #00FF00]")
    console.print(f"[dim]📊 Consolidating {total_vulns} vulnerabilities across {total_files} files...[/dim]")
    
    state_str = json.dumps(state, indent=2)
    prompt = GENERATION_PROMPT.format(state=state_str) if GENERATION_PROMPT else ""
    
    with console.status("[bold #00FF00]📄 Creating comprehensive security report...[/bold #00FF00]", spinner="star"):
        response = llm.invoke(prompt)
    
    content = response.content if response and response.content else ""
    parsed = parse_orchestrator_output(content.strip(), state)
    state['final_report'] = parsed
    state['complete'] = True
    
    console.print(f"[bold #00FF00]🎉 Security analysis complete![/bold #00FF00]")
    console.print(f"[bold #FFFFFF]📋 Report generated with {total_vulns} total findings[/bold #FFFFFF]")
    
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
    import time
    import signal
    import sys
    from .ui import console, show_agent_pipeline_start, show_vulnerability_summary_live, show_final_celebration
    
    start_time = time.time()
    
    # Graceful Ctrl+C handling
    def signal_handler(sig, frame):
        console.print()
        console.print("Analysis interrupted by user. Exiting gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    global llm
    global llm2
    llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0, top_p=0)
    llm2 = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0, top_p=0)
    
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
            'current_agent': 'patterndetectionagent',  # Start with pattern detection
            'pattern_complete': False,
            'context_complete': False,
            'compliance_complete': False,
            'file_complete': False,
            'all_files_complete': False,
            'complete': False
        }
    except Exception as e:
        console.print(f"Failed to initialize analysis: {str(e)}")
        return {'vulnerabilities': []}
    
    # Show startup
    show_agent_pipeline_start()
    
    iteration_count = 0
    max_iterations = 100  # Safety net to prevent infinite loops
    last_vuln_count = 0
    
    console.print("Initializing security analysis...")
    
    try:
        while not state['complete'] and iteration_count < max_iterations:
            iteration_count += 1
            
            # Let the orchestrator make intelligent decisions
            state = orchestrator(state)
            
            # Show live vulnerability count if it changed
            current_vuln_count = len(state.get('vulnerabilities', []))
            if current_vuln_count != last_vuln_count and current_vuln_count > 0:
                show_vulnerability_summary_live(state['vulnerabilities'])
                last_vuln_count = current_vuln_count
            
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
                console.print(f"Unknown agent '{state['current_agent']}', completing analysis")
                break
        
        if iteration_count >= max_iterations:
            console.print("Max iterations reached, completing analysis")
            state['complete'] = True
        
        # Show final celebration with timing
        scan_time = time.time() - start_time
        total_vulns = len(state.get('vulnerabilities', []))
        show_final_celebration(total_vulns, scan_time)
        
    except KeyboardInterrupt:
        console.print()
        console.print("Analysis interrupted by user. Exiting gracefully...")
        return {'vulnerabilities': state.get('vulnerabilities', [])}
    
    return state