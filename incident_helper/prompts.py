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
    
    # Detect cloud/service context from incident description (be more specific)
    cloud_context = ""
    alert_lower = alert.lower()
    
    # AWS - be more specific to avoid false positives
    aws_terms = ["aws", "amazon web services", "ec2", "elb", "elastic beanstalk", "beanstalk", "cloudwatch", "s3", "rds", "lambda"]
    if any(term in alert_lower for term in aws_terms):
        cloud_context = "AWS_CLOUD"
    # GCP
    elif any(term in alert_lower for term in ["gcp", "google cloud", "gke", "compute engine"]):
        cloud_context = "GCP_CLOUD"
    # Azure
    elif any(term in alert_lower for term in ["azure", "microsoft azure", "app service"]):
        cloud_context = "AZURE_CLOUD"
    # Kubernetes
    elif any(term in alert_lower for term in ["kubernetes", "k8s", "pod", "container", "kubectl", "helm"]):
        cloud_context = "KUBERNETES"
    # Docker
    elif any(term in alert_lower for term in ["docker", "dockerfile", "docker-compose"]):
        cloud_context = "DOCKER"
    
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
    
    # Add specific guidance based on context
    if cloud_context == "NONE":
        context_guidance = """
DIAGNOSTIC APPROACH:
- For web errors (404, 500): Check web server logs, service status, configuration
- For system issues: Check system resources, processes, logs
- For network issues: Test connectivity, DNS, routing
- Use standard Linux/system tools unless cloud services are explicitly mentioned
"""
    else:
        context_guidance = f"""
CLOUD CONTEXT DETECTED: {cloud_context}
- Provide cloud-specific diagnostic steps and tools
- Mention relevant cloud services and consoles
- Include both cloud-native and traditional diagnostic approaches
"""

    prompt += context_guidance + f"""
INSTRUCTIONS:
1. REMEMBER the conversation context - the user just asked: "{recent_responses[-1] if recent_responses else 'initial question'}"
2. ONLY mention cloud services if they were explicitly mentioned in the incident description
3. For generic web issues (404, 500 errors), focus on standard web server diagnostics first
4. Suggest the MOST relevant next diagnostic step based on the user's LATEST question
5. Provide specific commands or console steps (wrap in backticks)
6. Explain why this step helps with their specific question

Be contextually aware and directly address what the user just asked about.
Do NOT assume cloud platforms unless explicitly mentioned by the user.
"""
    
    return prompt

def build_web_server_prompt(incident_type: str, context: Dict[str, Any]) -> str:
    """Build a prompt for common web server issues"""
    
    return f"""You are diagnosing a {incident_type} web server issue.

CONTEXT: {context.get('alert', 'web server issue')}

For common web server issues like 404/500 errors:
1. Check web server logs (nginx: /var/log/nginx/, apache: /var/log/apache2/)
2. Verify web server status (systemctl status nginx/apache2)
3. Check application logs if applicable
4. Verify file permissions and document root
5. Test configuration syntax (nginx -t, apache2ctl configtest)

Provide specific diagnostic steps for standard web servers, not cloud platforms.
Focus on: logs → service status → configuration → file system
"""

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
