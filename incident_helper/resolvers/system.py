import subprocess
import platform
import psutil
from typing import Dict, List, Any, Optional

class SystemResolver:
    """Handles system-level diagnostics and information gathering"""
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture()[0],
                "hostname": platform.node(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": self._get_disk_usage(),
                "load_average": self._get_load_average(),
                "uptime": self._get_uptime()
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {e}"}
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                "network_io": psutil.net_io_counters()._asdict(),
                "processes": len(psutil.pids())
            }
        except Exception as e:
            return {"error": f"Failed to get resource usage: {e}"}
    
    def get_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by CPU/memory usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            return processes[:limit]
        except Exception as e:
            return [{"error": f"Failed to get processes: {e}"}]
    
    def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute system command safely"""
        try:
            # Import and use sanitization
            from incident_helper.utils import sanitize_command
            
            # Sanitize the command first
            try:
                sanitized_command = sanitize_command(command)
            except ValueError as e:
                return {
                    "command": command,
                    "error": str(e),
                    "success": False
                }
            
            result = subprocess.run(
                sanitized_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "error": "Command timed out",
                "success": False
            }
        except Exception as e:
            return {
                "command": command,
                "error": str(e),
                "success": False
            }
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage for root partition"""
        try:
            usage = psutil.disk_usage('/')
            return {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": (usage.used / usage.total) * 100
            }
        except:
            return {}
    
    def _get_load_average(self) -> Optional[List[float]]:
        """Get system load average (Unix-like systems only)"""
        try:
            if platform.system() != "Windows":
                return list(psutil.getloadavg())
        except:
            pass
        return None
    
    def _get_uptime(self) -> Optional[float]:
        """Get system uptime in seconds"""
        try:
            import time
            return time.time() - psutil.boot_time()
        except:
            return None