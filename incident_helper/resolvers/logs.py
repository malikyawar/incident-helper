import os
import re
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class LogResolver:
    """Handles log file analysis and searching"""
    
    def __init__(self):
        self.common_log_paths = [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/kern.log",
            "/var/log/auth.log",
            "/var/log/nginx/error.log",
            "/var/log/nginx/access.log",
            "/var/log/apache2/error.log",
            "/var/log/apache2/access.log",
            "/var/log/mysql/error.log",
            "/var/log/postgresql/postgresql.log",
            "/var/log/redis/redis-server.log"
        ]
    
    def find_log_files(self, pattern: str = None) -> List[Dict[str, Any]]:
        """Find available log files"""
        log_files = []
        
        for log_path in self.common_log_paths:
            if os.path.exists(log_path):
                try:
                    stat = os.stat(log_path)
                    log_files.append({
                        "path": log_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "readable": os.access(log_path, os.R_OK)
                    })
                except Exception as e:
                    log_files.append({
                        "path": log_path,
                        "error": str(e)
                    })
        
        # If pattern provided, filter results
        if pattern:
            log_files = [lf for lf in log_files if pattern.lower() in lf.get("path", "").lower()]
        
        return log_files
    
    def tail_log(self, log_path: str, lines: int = 50) -> Dict[str, Any]:
        """Get last N lines from a log file"""
        try:
            # Validate path for security
            from incident_helper.utils import validate_file_path
            try:
                validated_path = validate_file_path(log_path, ['/var/log/', '/tmp/', '/opt/'])
            except ValueError as e:
                return {"error": f"Invalid log path: {e}"}
            
            if not os.path.exists(validated_path):
                return {"error": f"Log file not found: {validated_path}"}
            
            if not os.access(validated_path, os.R_OK):
                return {"error": f"Cannot read log file: {validated_path}"}
            
            result = subprocess.run(
                ["tail", "-n", str(lines), validated_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "path": validated_path,
                "lines": result.stdout.split('\n'),
                "line_count": len(result.stdout.split('\n')),
                "success": result.returncode == 0
            }
            
        except Exception as e:
            return {"error": f"Failed to tail log: {e}", "path": log_path}
    
    def search_logs(self, log_path: str, pattern: str, lines: int = 100, 
                   case_sensitive: bool = False) -> Dict[str, Any]:
        """Search for pattern in log file"""
        try:
            if not os.path.exists(log_path):
                return {"error": f"Log file not found: {log_path}"}
            
            grep_args = ["grep"]
            if not case_sensitive:
                grep_args.append("-i")
            
            grep_args.extend(["-n", pattern, log_path])
            
            # Use safe subprocess without shell=True
            grep_cmd = ["grep"]
            if not case_sensitive:
                grep_cmd.append("-i")
            grep_cmd.extend(["-n", pattern, log_path])
            
            result = subprocess.run(
                grep_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # If we need to limit lines, process the output
            if lines > 0 and result.returncode == 0:
                output_lines = result.stdout.strip().split('\n')
                if len(output_lines) > lines:
                    result.stdout = '\n'.join(output_lines[:lines])
            
            matches = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "path": log_path,
                "pattern": pattern,
                "matches": matches,
                "match_count": len(matches),
                "success": result.returncode == 0
            }
            
        except Exception as e:
            return {"error": f"Failed to search logs: {e}", "path": log_path}
    
    def analyze_error_patterns(self, log_path: str, hours: int = 1) -> Dict[str, Any]:
        """Analyze common error patterns in logs"""
        try:
            # Get recent logs
            since_time = datetime.now() - timedelta(hours=hours)
            
            # Common error patterns
            error_patterns = [
                r"ERROR",
                r"FATAL",
                r"CRITICAL",
                r"Exception",
                r"Traceback",
                r"failed",
                r"timeout",
                r"connection refused",
                r"out of memory",
                r"disk full",
                r"permission denied"
            ]
            
            pattern_counts = {}
            total_errors = 0
            
            for pattern in error_patterns:
                search_result = self.search_logs(log_path, pattern, lines=1000, case_sensitive=False)
                if search_result.get("success"):
                    count = search_result.get("match_count", 0)
                    if count > 0:
                        pattern_counts[pattern] = count
                        total_errors += count
            
            return {
                "path": log_path,
                "analysis_period_hours": hours,
                "total_errors": total_errors,
                "error_patterns": pattern_counts,
                "top_errors": sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze error patterns: {e}", "path": log_path}
    
    def get_log_stats(self, log_path: str) -> Dict[str, Any]:
        """Get basic statistics about a log file"""
        try:
            if not os.path.exists(log_path):
                return {"error": f"Log file not found: {log_path}"}
            
            # Get file stats
            stat = os.stat(log_path)
            
            # Count lines
            line_count_result = subprocess.run(
                ["wc", "-l", log_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            line_count = 0
            if line_count_result.returncode == 0:
                line_count = int(line_count_result.stdout.split()[0])
            
            return {
                "path": log_path,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "line_count": line_count,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get log stats: {e}", "path": log_path}
    
    def monitor_log_realtime(self, log_path: str, pattern: str = None) -> Dict[str, Any]:
        """Monitor log file in real-time (returns command to run)"""
        if not os.path.exists(log_path):
            return {"error": f"Log file not found: {log_path}"}
        
        if pattern:
            command = f"tail -f {log_path} | grep --line-buffered '{pattern}'"
        else:
            command = f"tail -f {log_path}"
        
        return {
            "path": log_path,
            "command": command,
            "description": f"Monitor {log_path} in real-time" + (f" for pattern '{pattern}'" if pattern else ""),
            "note": "Run this command in a separate terminal to monitor logs in real-time"
        }