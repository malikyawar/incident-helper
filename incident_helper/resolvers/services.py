import subprocess
import platform
from typing import Dict, List, Any, Optional

class ServiceResolver:
    """Handles service management and status checking"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service"""
        if self.os_type == "linux":
            return self._get_systemd_service_status(service_name)
        elif self.os_type == "darwin":
            return self._get_launchd_service_status(service_name)
        else:
            return {"error": f"Service management not supported on {self.os_type}"}
    
    def list_failed_services(self) -> List[Dict[str, Any]]:
        """List all failed services"""
        if self.os_type == "linux":
            return self._list_failed_systemd_services()
        else:
            return [{"error": f"Failed service listing not supported on {self.os_type}"}]
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        """Get recent logs for a service"""
        if self.os_type == "linux":
            return self._get_systemd_logs(service_name, lines)
        else:
            return {"error": f"Service logs not supported on {self.os_type}"}
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a service (requires appropriate permissions)"""
        if self.os_type == "linux":
            return self._restart_systemd_service(service_name)
        else:
            return {"error": f"Service restart not supported on {self.os_type}"}
    
    def _get_systemd_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get systemd service status"""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse systemctl output
            lines = result.stdout.split('\n')
            status_info = {
                "service": service_name,
                "active": "unknown",
                "loaded": "unknown",
                "main_pid": None,
                "memory": None,
                "cpu": None
            }
            
            for line in lines:
                line = line.strip()
                if "Active:" in line:
                    status_info["active"] = line.split("Active:")[1].strip()
                elif "Loaded:" in line:
                    status_info["loaded"] = line.split("Loaded:")[1].strip()
                elif "Main PID:" in line:
                    try:
                        status_info["main_pid"] = int(line.split("Main PID:")[1].split()[0])
                    except:
                        pass
                elif "Memory:" in line:
                    status_info["memory"] = line.split("Memory:")[1].strip()
                elif "CPU:" in line:
                    status_info["cpu"] = line.split("CPU:")[1].strip()
            
            status_info["raw_output"] = result.stdout
            status_info["success"] = result.returncode == 0
            
            return status_info
            
        except Exception as e:
            return {"error": f"Failed to get service status: {e}", "service": service_name}
    
    def _list_failed_systemd_services(self) -> List[Dict[str, Any]]:
        """List failed systemd services"""
        try:
            result = subprocess.run(
                ["systemctl", "--failed", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            failed_services = []
            lines = result.stdout.split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip() and not line.startswith('●') and 'UNIT' not in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        failed_services.append({
                            "unit": parts[0],
                            "load": parts[1],
                            "active": parts[2],
                            "sub": parts[3],
                            "description": ' '.join(parts[4:]) if len(parts) > 4 else ""
                        })
            
            return failed_services
            
        except Exception as e:
            return [{"error": f"Failed to list failed services: {e}"}]
    
    def _get_systemd_logs(self, service_name: str, lines: int) -> Dict[str, Any]:
        """Get systemd service logs"""
        try:
            result = subprocess.run(
                ["journalctl", "-u", service_name, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "service": service_name,
                "logs": result.stdout,
                "success": result.returncode == 0,
                "lines_requested": lines
            }
            
        except Exception as e:
            return {"error": f"Failed to get service logs: {e}", "service": service_name}
    
    def _restart_systemd_service(self, service_name: str) -> Dict[str, Any]:
        """Restart systemd service"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "service": service_name,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {"error": f"Failed to restart service: {e}", "service": service_name}
    
    def _get_launchd_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get launchd service status (macOS)"""
        try:
            result = subprocess.run(
                ["launchctl", "list", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "service": service_name,
                "output": result.stdout,
                "success": result.returncode == 0,
                "error": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {"error": f"Failed to get service status: {e}", "service": service_name}