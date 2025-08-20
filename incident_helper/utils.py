import re
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"

def extract_error_patterns(text: str) -> List[str]:
    """Extract common error patterns from text"""
    error_patterns = [
        r'ERROR:?\s+(.+)',
        r'FATAL:?\s+(.+)',
        r'CRITICAL:?\s+(.+)',
        r'Exception:?\s+(.+)',
        r'Traceback.*?(?=\n\n|\n[A-Z]|\Z)',
        r'failed:?\s+(.+)',
        r'timeout:?\s+(.+)',
        r'connection refused',
        r'out of memory',
        r'disk full',
        r'permission denied'
    ]
    
    errors = []
    for pattern in error_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        errors.extend(matches)
    
    return errors

def parse_log_timestamp(log_line: str) -> Optional[datetime]:
    """Parse timestamp from common log formats"""
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # 2023-12-08 14:30:45
        r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',  # 08/Dec/2023:14:30:45
        r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})',        # Dec 08 14:30:45
    ]
    
    for pattern in timestamp_patterns:
        match = re.search(pattern, log_line)
        if match:
            timestamp_str = match.group(1)
            try:
                # Try different datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%b/%Y:%H:%M:%S', '%b %d %H:%M:%S']:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            except:
                pass
    
    return None

def sanitize_command(command: str) -> str:
    """Sanitize command for safe execution"""
    if not command or not isinstance(command, str):
        raise ValueError("Invalid command: must be a non-empty string")
    
    command = command.strip()
    
    # Block dangerous characters
    dangerous_chars = [';', '&&', '||', '|', '>', '>>', '<', '`', '$', '(', ')']
    for char in dangerous_chars:
        if char in command:
            raise ValueError(f"Dangerous character '{char}' detected in command: {command}")
    
    # Block dangerous commands and patterns
    dangerous_patterns = [
        r'rm\s+-rf\s*/',
        r'rm\s+-rf\s+\*',
        r'dd\s+if=',
        r'mkfs\.',
        r'fdisk',
        r'format',
        r'>\s*/dev/',
        r'curl.*sh',
        r'wget.*sh',
        r'bash\s*-c',
        r'sh\s*-c',
        r'eval\s+',
        r'exec\s+',
        r'sudo\s+rm',
        r'chmod\s+777',
        r'chown\s+.*:.*\s+/',
        r'://',  # Block URLs
        r'\.\./',  # Block path traversal
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            raise ValueError(f"Potentially dangerous command pattern detected: {command}")
    
    # Whitelist of allowed commands (basic diagnostic commands only)
    allowed_commands = [
        'ls', 'cat', 'tail', 'head', 'grep', 'find', 'ps', 'top', 'htop',
        'df', 'du', 'free', 'uptime', 'whoami', 'id', 'date', 'uname',
        'systemctl', 'journalctl', 'service', 'netstat', 'ss', 'ping',
        'traceroute', 'nslookup', 'dig', 'curl', 'wget', 'ssh', 'scp',
        'awk', 'sed', 'sort', 'uniq', 'wc', 'which', 'whereis',
        'lsof', 'iostat', 'vmstat', 'sar', 'tcpdump', 'iptables'
    ]
    
    # Extract the base command (first word)
    base_command = command.split()[0] if command.split() else ""
    
    # Remove common prefixes
    if base_command.startswith('./'):
        base_command = base_command[2:]
    elif base_command.startswith('/'):
        base_command = os.path.basename(base_command)
    
    if base_command not in allowed_commands:
        raise ValueError(f"Command '{base_command}' is not in the allowed list for security reasons")
    
    return command

def parse_service_status(status_output: str) -> Dict[str, Any]:
    """Parse systemctl status output"""
    status_info = {
        "loaded": "unknown",
        "active": "unknown",
        "sub": "unknown",
        "main_pid": None,
        "memory": None,
        "cpu": None
    }
    
    lines = status_output.split('\n')
    for line in lines:
        line = line.strip()
        
        if "Loaded:" in line:
            status_info["loaded"] = line.split("Loaded:")[1].strip()
        elif "Active:" in line:
            status_info["active"] = line.split("Active:")[1].strip()
        elif "Main PID:" in line:
            try:
                pid_match = re.search(r'Main PID:\s*(\d+)', line)
                if pid_match:
                    status_info["main_pid"] = int(pid_match.group(1))
            except:
                pass
        elif "Memory:" in line:
            status_info["memory"] = line.split("Memory:")[1].strip()
        elif "CPU:" in line:
            status_info["cpu"] = line.split("CPU:")[1].strip()
    
    return status_info

def calculate_severity_score(metrics: Dict[str, Any]) -> int:
    """Calculate incident severity score based on system metrics"""
    score = 0
    
    # CPU usage
    cpu_percent = metrics.get("cpu_percent", 0)
    if cpu_percent > 90:
        score += 3
    elif cpu_percent > 70:
        score += 2
    elif cpu_percent > 50:
        score += 1
    
    # Memory usage
    memory_percent = metrics.get("memory_percent", 0)
    if memory_percent > 95:
        score += 3
    elif memory_percent > 80:
        score += 2
    elif memory_percent > 60:
        score += 1
    
    # Disk usage
    disk_percent = metrics.get("disk_usage", {}).get("percent", 0)
    if disk_percent > 95:
        score += 3
    elif disk_percent > 85:
        score += 2
    elif disk_percent > 70:
        score += 1
    
    # Load average (if available)
    load_avg = metrics.get("load_average")
    if load_avg and len(load_avg) > 0:
        cpu_count = metrics.get("cpu_count", 1)
        load_ratio = load_avg[0] / cpu_count
        if load_ratio > 2.0:
            score += 3
        elif load_ratio > 1.5:
            score += 2
        elif load_ratio > 1.0:
            score += 1
    
    return min(score, 10)  # Cap at 10

def generate_incident_id() -> str:
    """Generate a unique incident ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INC-{timestamp}"

def validate_log_path(path: str) -> bool:
    """Validate if a path looks like a valid log file"""
    import os
    
    if not path or not isinstance(path, str):
        return False
    
    # Prevent path traversal attacks
    if '..' in path or path.startswith('/'):
        # Only allow absolute paths in safe directories
        safe_dirs = ['/var/log/', '/tmp/', '/opt/']
        if not any(path.startswith(safe_dir) for safe_dir in safe_dirs):
            return False
    
    # Resolve path to prevent traversal
    try:
        resolved_path = os.path.realpath(path)
        # Ensure resolved path is still in safe directories
        safe_dirs = ['/var/log/', '/tmp/', '/opt/', os.getcwd()]
        if not any(resolved_path.startswith(safe_dir) for safe_dir in safe_dirs):
            return False
    except:
        return False
    
    if not os.path.exists(resolved_path):
        return False
    
    if not os.path.isfile(resolved_path):
        return False
    
    # Check if it's a common log file location or extension
    log_indicators = [
        '/var/log/',
        '/var/log/nginx/',
        '/var/log/apache2/',
        '/var/log/mysql/',
        '/var/log/postgresql/',
        '.log',
        '.out',
        '.err'
    ]
    
    return any(indicator in resolved_path.lower() for indicator in log_indicators)

def validate_file_path(path: str, allowed_dirs: List[str] = None) -> str:
    """Validate and sanitize file paths to prevent path traversal"""
    import os
    
    if not path or not isinstance(path, str):
        raise ValueError("Invalid path: must be a non-empty string")
    
    # Default allowed directories
    if allowed_dirs is None:
        allowed_dirs = ['/var/log/', '/tmp/', '/opt/', os.getcwd()]
    
    # Prevent path traversal
    if '..' in path:
        raise ValueError("Path traversal detected: '..' not allowed")
    
    # Resolve the path
    try:
        resolved_path = os.path.realpath(path)
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")
    
    # Check if resolved path is in allowed directories
    if not any(resolved_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
        raise ValueError(f"Path not in allowed directories: {resolved_path}")
    
    return resolved_path

def extract_ip_addresses(text: str) -> List[str]:
    """Extract IP addresses from text"""
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    return re.findall(ip_pattern, text)

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)

def colorize_severity(severity: str) -> str:
    """Return color code for severity level"""
    colors = {
        "low": "green",
        "medium": "yellow", 
        "high": "orange",
        "critical": "red"
    }
    return colors.get(severity.lower(), "white")

def truncate_output(text: str, max_lines: int = 50, max_chars: int = 2000) -> str:
    """Truncate command output for display"""
    lines = text.split('\n')
    
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f"... [truncated: {len(text.split(chr(10))) - max_lines} more lines]")
    
    result = '\n'.join(lines)
    
    if len(result) > max_chars:
        result = result[:max_chars] + "... [truncated: output too long]"
    
    return result