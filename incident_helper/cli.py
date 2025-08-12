import typer
import json
import os
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from incident_helper.context import IncidentContext, IncidentSeverity, IncidentStatus
from incident_helper.agents import LLMEngine
from incident_helper.resolvers.system import SystemResolver
from incident_helper.resolvers.services import ServiceResolver
from incident_helper.resolvers.logs import LogResolver
from incident_helper.resolvers.network import NetworkResolver
from incident_helper.resolvers.ssh import SSHResolver
from incident_helper.resolvers.aws import AWSResolver
from incident_helper.prompts import build_diagnostic_prompt, build_analysis_prompt

app = typer.Typer(help="🛠️ AI-powered incident response tool for SREs and DevOps")
console = Console()

# Global instances
ctx = IncidentContext()
llm = None  # Will be initialized when needed
system_resolver = SystemResolver()
service_resolver = ServiceResolver()
log_resolver = LogResolver()
network_resolver = NetworkResolver()
ssh_resolver = SSHResolver()
aws_resolver = AWSResolver()

def get_llm(provider: str = "ollama", model: str = "mistral"):
    """Get or create LLM instance"""
    global llm
    try:
        if llm is None:
            llm = LLMEngine(provider=provider, model=model)
        return llm
    except Exception as e:
        console.print(f"❌ Failed to initialize LLM: {e}", style="red")
        return None

@app.command()
def start(
    provider: str = typer.Option("ollama", help="LLM provider (ollama, openai)"),
    model: str = typer.Option(None, help="Model name"),
    auto_execute: bool = typer.Option(False, help="Auto-execute suggested commands")
):
    """Start an interactive incident response session"""
    global llm
    
    # Initialize LLM with specified provider
    try:
        llm = LLMEngine(provider=provider, model=model)
        console.print(f"✅ {llm.get_provider_info()}", style="green")
    except Exception as e:
        console.print(f"❌ Failed to initialize LLM: {e}", style="red")
        return
    
    console.print(Panel.fit("🛠️ Incident Helper - AI-powered SRE Assistant", style="bold blue"))
    
    # Initial incident report
    alert = Prompt.ask("👋 Describe your incident")
    ctx.set("alert", alert)
    
    # Gather initial context
    _gather_initial_context()
    
    # Main interaction loop
    console.print("\n💬 Starting diagnostic conversation...")
    console.print("Type 'help' for commands, 'exit' to quit\n")
    
    while True:
        try:
            # Get AI suggestion
            if llm:
                prompt = build_diagnostic_prompt(ctx.get_summary(), ctx.data)
                ai_response = llm.ask(prompt)
                console.print(Panel(ai_response, title="🤖 AI Assistant", style="cyan"))
            else:
                console.print(Panel("LLM not available. You can still use manual commands with '!' prefix.", title="⚠️ Manual Mode", style="yellow"))
            
            # Parse AI response for commands
            suggested_commands = _extract_commands(ai_response)
            
            if suggested_commands and auto_execute:
                for cmd in suggested_commands:
                    if Confirm.ask(f"Execute: {cmd}?"):
                        _execute_command(cmd)
            
            # Get user input
            user_input = Prompt.ask("> ")
            
            if user_input.lower() in ["exit", "quit"]:
                _end_session()
                break
            elif user_input.lower() == "help":
                _show_help()
                continue
            elif user_input.lower() == "status":
                _show_status()
                continue
            elif user_input.lower() == "report":
                _generate_report()
                continue
            elif user_input.startswith("!"):
                # Execute command
                command = user_input[1:].strip()
                _execute_command(command)
                continue
            
            # Store user response
            ctx.set(f"response_{len(ctx.data)}", user_input)
            
        except KeyboardInterrupt:
            console.print("\n👋 Session interrupted. Use 'exit' to quit properly.")
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")

@app.command()
def quick_check(
    service: Optional[str] = typer.Option(None, help="Service to check"),
    log_file: Optional[str] = typer.Option(None, help="Log file to analyze"),
    host: Optional[str] = typer.Option(None, help="Host to ping")
):
    """Quick system health check"""
    console.print("🔍 Running quick health check...\n")
    
    # System resources
    console.print("📊 System Resources:")
    resources = system_resolver.get_resource_usage()
    if "error" not in resources:
        table = Table()
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("CPU Usage", f"{resources['cpu_percent']}%")
        table.add_row("Memory Usage", f"{resources['memory_percent']}%")
        table.add_row("Active Processes", str(resources['processes']))
        console.print(table)
    
    # Service check
    if service:
        console.print(f"\n🔧 Service Status: {service}")
        status = service_resolver.get_service_status(service)
        console.print(json.dumps(status, indent=2))
    
    # Log analysis
    if log_file:
        console.print(f"\n📋 Log Analysis: {log_file}")
        analysis = log_resolver.analyze_error_patterns(log_file)
        console.print(json.dumps(analysis, indent=2))
    
    # Network check
    if host:
        console.print(f"\n🌐 Network Test: {host}")
        ping_result = network_resolver.ping_host(host)
        console.print(json.dumps(ping_result, indent=2))

@app.command()
def analyze_logs(
    path: str = typer.Argument(..., help="Log file path"),
    pattern: Optional[str] = typer.Option(None, help="Search pattern"),
    lines: int = typer.Option(50, help="Number of lines to analyze")
):
    """Analyze log files for issues"""
    console.print(f"📋 Analyzing log file: {path}")
    
    if pattern:
        result = log_resolver.search_logs(path, pattern, lines)
    else:
        result = log_resolver.analyze_error_patterns(path)
    
    console.print(json.dumps(result, indent=2))

@app.command()
def test_connectivity(
    host: str = typer.Argument(..., help="Host to test"),
    port: Optional[int] = typer.Option(None, help="Port to test")
):
    """Test network connectivity"""
    console.print(f"🌐 Testing connectivity to {host}")
    
    if port:
        result = network_resolver.diagnose_connection_issue(host, port)
    else:
        result = network_resolver.check_connectivity([host])
    
    console.print(json.dumps(result, indent=2))

@app.command()
def aws_eb_logs(
    environment: Optional[str] = typer.Option(None, help="EB environment name"),
    lines: int = typer.Option(100, help="Number of log lines")
):
    """Get Elastic Beanstalk logs"""
    console.print("📋 Getting Elastic Beanstalk logs...")
    
    result = aws_resolver.get_eb_logs(environment, lines)
    if result.get("success"):
        console.print("✅ Logs retrieved successfully")
        console.print(result.get("logs", "No logs found"))
    else:
        console.print("❌ Failed to get logs")
        console.print(json.dumps(result, indent=2))

@app.command()
def aws_eb_health(
    environment: Optional[str] = typer.Option(None, help="EB environment name")
):
    """Get Elastic Beanstalk health status"""
    console.print("🏥 Checking Elastic Beanstalk health...")
    
    result = aws_resolver.get_eb_health(environment)
    if result.get("success"):
        console.print("✅ Health info retrieved")
        console.print(result.get("health_info", "No health info"))
    else:
        console.print("❌ Failed to get health info")
        console.print(json.dumps(result, indent=2))

def _gather_initial_context():
    """Gather initial system context"""
    console.print("🔍 Gathering system context...")
    
    # Get system info
    sys_info = system_resolver.get_system_info()
    ctx.set("system_info", sys_info)
    
    # Ask for environment
    env = Prompt.ask("Environment", choices=["production", "staging", "development", "other"], default="production")
    ctx.set("environment", env)
    
    # Ask for severity with flexible input
    while True:
        severity_input = Prompt.ask("Severity (1/low, 2/medium, 3/high, 4/critical)", default="2").lower().strip()
        
        # Map various inputs to severity levels
        severity_map = {
            "1": IncidentSeverity.LOW, "low": IncidentSeverity.LOW, "l": IncidentSeverity.LOW,
            "2": IncidentSeverity.MEDIUM, "medium": IncidentSeverity.MEDIUM, "med": IncidentSeverity.MEDIUM, "m": IncidentSeverity.MEDIUM,
            "3": IncidentSeverity.HIGH, "high": IncidentSeverity.HIGH, "h": IncidentSeverity.HIGH,
            "4": IncidentSeverity.CRITICAL, "critical": IncidentSeverity.CRITICAL, "crit": IncidentSeverity.CRITICAL, "c": IncidentSeverity.CRITICAL
        }
        
        if severity_input in severity_map:
            ctx.set_severity(severity_map[severity_input])
            break
        else:
            console.print("❌ Please enter: 1/low, 2/medium, 3/high, or 4/critical", style="red")

def _extract_commands(text: str) -> list:
    """Extract suggested commands from AI response"""
    commands = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('`') and line.endswith('`'):
            commands.append(line[1:-1])
        elif 'sudo ' in line or any(cmd in line for cmd in ['systemctl', 'journalctl', 'tail', 'grep', 'ps', 'top']):
            # Extract command-like text
            import re
            cmd_match = re.search(r'`([^`]+)`', line)
            if cmd_match:
                commands.append(cmd_match.group(1))
    
    return commands

def _execute_command(command: str):
    """Execute a system command and store results"""
    console.print(f"⚡ Executing: {command}")
    
    result = system_resolver.run_command(command)
    ctx.add_command(command, result.get("stdout", ""), result.get("success", False))
    
    if result.get("success"):
        console.print("✅ Command executed successfully")
        if result.get("stdout"):
            console.print(Syntax(result["stdout"], "bash", theme="monokai"))
    else:
        console.print("❌ Command failed")
        if result.get("stderr"):
            console.print(f"Error: {result['stderr']}", style="red")

def _show_help():
    """Show available commands"""
    help_text = """
Available commands:
• help - Show this help
• status - Show incident status
• report - Generate incident report
• exit/quit - End session
• !<command> - Execute system command
• Any other input will be sent to the AI assistant
"""
    console.print(Panel(help_text, title="Help", style="yellow"))

def _show_status():
    """Show current incident status"""
    summary = ctx.get_summary()
    
    table = Table(title="Incident Status")
    table.add_column("Field")
    table.add_column("Value")
    
    for key, value in summary.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)

def _generate_report():
    """Generate and save incident report"""
    report = ctx.export_report()
    
    filename = f"incident_report_{ctx.start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        f.write(report)
    
    console.print(f"📄 Report saved to: {filename}")

def _end_session():
    """End the incident session"""
    ctx.set_status(IncidentStatus.RESOLVED)
    console.print("👋 Session ended. Thank you for using Incident Helper!")
    
    if Confirm.ask("Generate final report?"):
        _generate_report()

if __name__ == "__main__":
    app()
