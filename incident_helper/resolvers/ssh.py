import subprocess
import os
from typing import Dict, List, Any, Optional

class SSHResolver:
    """Handles SSH connectivity and remote command execution"""
    
    def test_ssh_connection(self, host: str, user: str = None, port: int = 22, 
                           key_file: str = None) -> Dict[str, Any]:
        """Test SSH connectivity to a host"""
        try:
            ssh_args = ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes"]
            
            if port != 22:
                ssh_args.extend(["-p", str(port)])
            
            if key_file and os.path.exists(key_file):
                ssh_args.extend(["-i", key_file])
            
            if user:
                target = f"{user}@{host}"
            else:
                target = host
            
            ssh_args.extend([target, "echo", "SSH connection successful"])
            
            result = subprocess.run(
                ssh_args,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "host": host,
                "user": user,
                "port": port,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "key_file": key_file
            }
            
        except Exception as e:
            return {
                "error": f"Failed to test SSH connection to {host}: {e}",
                "host": host,
                "user": user,
                "port": port
            }
    
    def execute_remote_command(self, host: str, command: str, user: str = None, 
                              port: int = 22, key_file: str = None, 
                              timeout: int = 30) -> Dict[str, Any]:
        """Execute a command on a remote host via SSH"""
        try:
            ssh_args = ["ssh", "-o", "ConnectTimeout=10"]
            
            if port != 22:
                ssh_args.extend(["-p", str(port)])
            
            if key_file and os.path.exists(key_file):
                ssh_args.extend(["-i", key_file])
            
            if user:
                target = f"{user}@{host}"
            else:
                target = host
            
            ssh_args.extend([target, command])
            
            result = subprocess.run(
                ssh_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "host": host,
                "user": user,
                "command": command,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "error": f"Command timed out after {timeout} seconds",
                "host": host,
                "command": command,
                "timeout": timeout
            }
        except Exception as e:
            return {
                "error": f"Failed to execute remote command: {e}",
                "host": host,
                "command": command
            }
    
    def copy_file_to_remote(self, local_path: str, remote_path: str, host: str,
                           user: str = None, port: int = 22, 
                           key_file: str = None) -> Dict[str, Any]:
        """Copy a file to remote host using SCP"""
        try:
            if not os.path.exists(local_path):
                return {"error": f"Local file not found: {local_path}"}
            
            scp_args = ["scp", "-o", "ConnectTimeout=10"]
            
            if port != 22:
                scp_args.extend(["-P", str(port)])
            
            if key_file and os.path.exists(key_file):
                scp_args.extend(["-i", key_file])
            
            if user:
                target = f"{user}@{host}:{remote_path}"
            else:
                target = f"{host}:{remote_path}"
            
            scp_args.extend([local_path, target])
            
            result = subprocess.run(
                scp_args,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "local_path": local_path,
                "remote_path": remote_path,
                "host": host,
                "user": user,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                "error": f"Failed to copy file to remote: {e}",
                "local_path": local_path,
                "remote_path": remote_path,
                "host": host
            }
    
    def copy_file_from_remote(self, remote_path: str, local_path: str, host: str,
                             user: str = None, port: int = 22, 
                             key_file: str = None) -> Dict[str, Any]:
        """Copy a file from remote host using SCP"""
        try:
            scp_args = ["scp", "-o", "ConnectTimeout=10"]
            
            if port != 22:
                scp_args.extend(["-P", str(port)])
            
            if key_file and os.path.exists(key_file):
                scp_args.extend(["-i", key_file])
            
            if user:
                source = f"{user}@{host}:{remote_path}"
            else:
                source = f"{host}:{remote_path}"
            
            scp_args.extend([source, local_path])
            
            result = subprocess.run(
                scp_args,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "remote_path": remote_path,
                "local_path": local_path,
                "host": host,
                "user": user,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                "error": f"Failed to copy file from remote: {e}",
                "remote_path": remote_path,
                "local_path": local_path,
                "host": host
            }
    
    def get_ssh_config(self) -> Dict[str, Any]:
        """Get SSH client configuration"""
        try:
            ssh_config_path = os.path.expanduser("~/.ssh/config")
            
            if os.path.exists(ssh_config_path):
                with open(ssh_config_path, 'r') as f:
                    config_content = f.read()
                
                return {
                    "config_path": ssh_config_path,
                    "config_content": config_content,
                    "exists": True
                }
            else:
                return {
                    "config_path": ssh_config_path,
                    "exists": False,
                    "message": "SSH config file not found"
                }
                
        except Exception as e:
            return {"error": f"Failed to read SSH config: {e}"}
    
    def list_ssh_keys(self) -> List[Dict[str, Any]]:
        """List available SSH keys"""
        try:
            ssh_dir = os.path.expanduser("~/.ssh")
            if not os.path.exists(ssh_dir):
                return [{"message": "SSH directory not found"}]
            
            key_files = []
            common_key_names = ["id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"]
            
            for key_name in common_key_names:
                private_key = os.path.join(ssh_dir, key_name)
                public_key = os.path.join(ssh_dir, f"{key_name}.pub")
                
                if os.path.exists(private_key):
                    key_info = {
                        "name": key_name,
                        "private_key": private_key,
                        "public_key": public_key if os.path.exists(public_key) else None,
                        "private_key_exists": True,
                        "public_key_exists": os.path.exists(public_key)
                    }
                    
                    # Get key permissions
                    try:
                        stat = os.stat(private_key)
                        key_info["permissions"] = oct(stat.st_mode)[-3:]
                    except:
                        pass
                    
                    key_files.append(key_info)
            
            return key_files
            
        except Exception as e:
            return [{"error": f"Failed to list SSH keys: {e}"}]
    
    def diagnose_ssh_issue(self, host: str, user: str = None, port: int = 22) -> Dict[str, Any]:
        """Comprehensive SSH connection diagnosis"""
        diagnosis = {
            "host": host,
            "user": user,
            "port": port,
            "tests": {}
        }
        
        # Test basic connectivity
        diagnosis["tests"]["connectivity"] = self.test_ssh_connection(host, user, port)
        
        # Check SSH keys
        diagnosis["tests"]["ssh_keys"] = self.list_ssh_keys()
        
        # Check SSH config
        diagnosis["tests"]["ssh_config"] = self.get_ssh_config()
        
        # Test with verbose output for debugging
        try:
            ssh_args = ["ssh", "-v", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes"]
            if port != 22:
                ssh_args.extend(["-p", str(port)])
            
            target = f"{user}@{host}" if user else host
            ssh_args.extend([target, "echo", "test"])
            
            result = subprocess.run(
                ssh_args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            diagnosis["tests"]["verbose_output"] = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            diagnosis["tests"]["verbose_output"] = {"error": str(e)}
        
        return diagnosis