from typing import Dict, Any, List

def build_diagnostic_prompt(summary: Dict[str, Any], context: Dict[str, Any]) -> str:
    """Build a diagnostic prompt for the AI assistant"""
    
    alert = summary.get("alert", "unknown incident")
    severity = summary.get("severity", "unknown")
    environment = summary.get("environment", "unknown")
    os_info = context.get("system_info", {}).get("os", "unknown")
    
    recent_commands = context.get("commands_executed", [])[-3:] if context.get("commands_executed") else []
    
    # Get recent conversation context
    recent_responses = []
    for key, value in context.items():
        if key.startswith("response_") and isinstance(value, str):
            recent_responses.append(value)
    recent_responses = recent_responses[-3:]  # Last 3 responses
    
    # Detect cloud/service context from incident description
    cloud_context = ""
    alert_lower = alert.lower()
    if any(term in alert_lower for term in ["aws", "amazon", "ec2", "elb", "elastic", "beanstalk"]):
        cloud_context = "AWS_CLOUD"
    elif any(term in alert_lower for term in ["gcp", "google cloud", "gke"]):
        cloud_context = "GCP_CLOUD"
    elif any(term in alert_lower for term in ["azure", "microsoft"]):
        cloud_context = "AZURE_CLOUD"
    elif any(term in alert_lower for term in ["kubernetes", "k8s", "pod", "container"]):
        cloud_context = "KUBERNETES"
    
    prompt = f"""You are an expert SRE assistant helping debug a {severity} severity incident in {environment}.

INCIDENT: {alert}
SYSTEM: {os_info}
DURATION: {summary.get("duration", "unknown")}
CLOUD_CONTEXT: {cloud_context}

RECENT CONVERSATION:"""
    
    if recent_responses:
        prompt += "\nUser's recent responses:\n"
        for i, response in enumerate(recent_responses, 1):
            prompt += f"{i}. {response}\n"
    
    if recent_commands:
        prompt += "\nRecent commands executed:\n"
        for cmd in recent_commands:
            prompt += f"- {cmd['command']}: {'✅' if cmd['success'] else '❌'}\n"
    
    prompt += f"""
INSTRUCTIONS:
1. REMEMBER the conversation context - the user just asked: "{recent_responses[-1] if recent_responses else 'initial question'}"
2. If cloud context detected, provide cloud-specific guidance (AWS CLI, console, CloudWatch, etc.)
3. For Elastic Beanstalk: mention eb logs, CloudWatch logs, application logs in /var/log/
4. Suggest the MOST relevant next diagnostic step based on the user's LATEST question
5. Provide specific commands or console steps (wrap in backticks)
6. Explain why this step helps with their specific question

Be contextually aware and directly address what the user just asked about.
For AWS/cloud issues, prioritize cloud-native tools and services.
"""
    
    return prompt

def build_analysis_prompt(data: Dict[str, Any], command_output: str) -> str:
    """Build a prompt for analyzing command output"""
    
    return f"""You are an expert SRE analyzing command output for incident response.

INCIDENT CONTEXT: {data.get('alert', 'unknown')}
COMMAND OUTPUT:
{command_output}

ANALYSIS TASKS:
1. Identify any errors, warnings, or anomalies
2. Explain what the output indicates about the system state
3. Suggest immediate next steps based on findings
4. Rate the urgency (Low/Medium/High/Critical)

Provide a clear, actionable analysis focusing on incident resolution.
"""

def build_log_analysis_prompt(log_entries: List[str], incident_context: str) -> str:
    """Build a prompt for analyzing log entries"""
    
    log_sample = "\n".join(log_entries[:20])  # First 20 lines
    
    return f"""You are analyzing logs for incident: {incident_context}

LOG ENTRIES:
{log_sample}

ANALYSIS REQUIRED:
1. Identify error patterns and anomalies
2. Correlate timestamps with incident timeline
3. Extract relevant error messages and stack traces
4. Suggest root cause hypotheses
5. Recommend specific log files or services to investigate further

Focus on actionable insights for incident resolution.
"""

def build_system_health_prompt(system_metrics: Dict[str, Any]) -> str:
    """Build a prompt for system health analysis"""
    
    return f"""Analyze these system metrics for potential issues:

SYSTEM METRICS:
{system_metrics}

HEALTH CHECK ANALYSIS:
1. Identify resource bottlenecks or anomalies
2. Check if metrics indicate system stress
3. Correlate with typical incident patterns
4. Suggest monitoring or mitigation steps
5. Rate overall system health (Good/Warning/Critical)

Provide specific recommendations based on the metrics.
"""

def build_network_diagnosis_prompt(network_results: Dict[str, Any]) -> str:
    """Build a prompt for network issue diagnosis"""
    
    return f"""Analyze network connectivity results:

NETWORK TEST RESULTS:
{network_results}

NETWORK DIAGNOSIS:
1. Identify connectivity issues or patterns
2. Determine if problems are local, network, or remote
3. Suggest specific network troubleshooting steps
4. Recommend tools or commands for deeper analysis
5. Assess impact on services and users

Focus on practical network troubleshooting guidance.
"""

def build_service_analysis_prompt(service_status: Dict[str, Any], service_logs: str = None) -> str:
    """Build a prompt for service analysis"""
    
    prompt = f"""Analyze service status and logs:

SERVICE STATUS:
{service_status}
"""
    
    if service_logs:
        prompt += f"""
SERVICE LOGS:
{service_logs[:1000]}...  # Truncated
"""
    
    prompt += """
SERVICE ANALYSIS:
1. Determine service health and operational status
2. Identify configuration or runtime issues
3. Check for dependency problems
4. Suggest service management actions (restart, reload, etc.)
5. Recommend log files or metrics to monitor

Provide specific service troubleshooting steps.
"""
    
    return prompt
