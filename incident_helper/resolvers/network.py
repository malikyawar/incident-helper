import subprocess
import socket
import platform
from typing import Dict, List, Any, Optional

class NetworkResolver:
    """Handles network diagnostics and connectivity testing"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
    
    def ping_host(self, host: str, count: int = 4) -> Dict[str, Any]:
        """Ping a host to test connectivity"""
        try:
            ping_cmd = "ping"
            if self.os_type == "windows":
                args = [ping_cmd, "-n", str(count), host]
            else:
                args = [ping_cmd, "-c", str(count), host]
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "host": host,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "packet_count": count
            }
            
        except Exception as e:
            return {"error": f"Failed to ping {host}: {e}", "host": host}
    
    def test_port(self, host: str, port: int, timeout: int = 5) -> Dict[str, Any]:
        """Test if a specific port is open on a host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return {
                "host": host,
                "port": port,
                "open": result == 0,
                "timeout": timeout,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Failed to test port {port} on {host}: {e}",
                "host": host,
                "port": port,
                "success": False
            }
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information"""
        try:
            if self.os_type == "linux" or self.os_type == "darwin":
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ["ipconfig", "/all"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            return [{
                "raw_output": result.stdout,
                "success": result.returncode == 0,
                "command_used": "ifconfig" if self.os_type != "windows" else "ipconfig"
            }]
            
        except Exception as e:
            return [{"error": f"Failed to get network interfaces: {e}"}]
    
    def get_routing_table(self) -> Dict[str, Any]:
        """Get system routing table"""
        try:
            if self.os_type == "linux":
                cmd = ["route", "-n"]
            elif self.os_type == "darwin":
                cmd = ["netstat", "-rn"]
            elif self.os_type == "windows":
                cmd = ["route", "print"]
            else:
                return {"error": f"Routing table not supported on {self.os_type}"}
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "routing_table": result.stdout,
                "success": result.returncode == 0,
                "command_used": " ".join(cmd)
            }
            
        except Exception as e:
            return {"error": f"Failed to get routing table: {e}"}
    
    def get_dns_info(self, domain: str) -> Dict[str, Any]:
        """Get DNS information for a domain"""
        try:
            # Try nslookup first
            nslookup_result = subprocess.run(
                ["nslookup", domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            dns_info = {
                "domain": domain,
                "nslookup_output": nslookup_result.stdout,
                "nslookup_success": nslookup_result.returncode == 0
            }
            
            # Try dig if available (more detailed)
            try:
                dig_result = subprocess.run(
                    ["dig", domain],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                dns_info["dig_output"] = dig_result.stdout
                dns_info["dig_success"] = dig_result.returncode == 0
            except FileNotFoundError:
                dns_info["dig_output"] = "dig command not available"
            
            return dns_info
            
        except Exception as e:
            return {"error": f"Failed to get DNS info for {domain}: {e}", "domain": domain}
    
    def trace_route(self, host: str, max_hops: int = 30) -> Dict[str, Any]:
        """Trace route to a host"""
        try:
            if self.os_type == "windows":
                cmd = ["tracert", "-h", str(max_hops), host]
            else:
                cmd = ["traceroute", "-m", str(max_hops), host]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "host": host,
                "max_hops": max_hops,
                "output": result.stdout,
                "success": result.returncode == 0,
                "command_used": " ".join(cmd)
            }
            
        except Exception as e:
            return {"error": f"Failed to trace route to {host}: {e}", "host": host}
    
    def get_listening_ports(self) -> Dict[str, Any]:
        """Get list of listening ports"""
        try:
            if self.os_type == "windows":
                cmd = ["netstat", "-an"]
            else:
                cmd = ["netstat", "-tuln"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "listening_ports": result.stdout,
                "success": result.returncode == 0,
                "command_used": " ".join(cmd)
            }
            
        except Exception as e:
            return {"error": f"Failed to get listening ports: {e}"}
    
    def check_connectivity(self, targets: List[str] = None) -> Dict[str, Any]:
        """Check connectivity to common services"""
        if not targets:
            targets = ["8.8.8.8", "1.1.1.1", "google.com", "github.com"]
        
        results = {}
        for target in targets:
            results[target] = self.ping_host(target, count=2)
        
        # Summary
        successful = sum(1 for r in results.values() if r.get("success", False))
        
        return {
            "targets_tested": len(targets),
            "successful_connections": successful,
            "connectivity_score": f"{successful}/{len(targets)}",
            "results": results
        }
    
    def diagnose_connection_issue(self, host: str, port: int = None) -> Dict[str, Any]:
        """Comprehensive connection diagnosis"""
        diagnosis = {
            "host": host,
            "port": port,
            "tests": {}
        }
        
        # Test basic connectivity
        diagnosis["tests"]["ping"] = self.ping_host(host, count=3)
        
        # Test DNS resolution
        diagnosis["tests"]["dns"] = self.get_dns_info(host)
        
        # Test specific port if provided
        if port:
            diagnosis["tests"]["port"] = self.test_port(host, port)
        
        # Test common ports if no specific port
        else:
            common_ports = [80, 443, 22, 21, 25, 53]
            port_results = {}
            for p in common_ports:
                port_results[p] = self.test_port(host, p, timeout=3)
            diagnosis["tests"]["common_ports"] = port_results
        
        return diagnosis