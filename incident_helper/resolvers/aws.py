import subprocess
import json
from typing import Dict, List, Any, Optional

class AWSResolver:
    """Handles AWS-specific diagnostics and operations"""
    
    def __init__(self):
        self.aws_cli_available = self._check_aws_cli()
    
    def _check_aws_cli(self) -> bool:
        """Check if AWS CLI is available"""
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_eb_logs(self, environment_name: str = None, lines: int = 100) -> Dict[str, Any]:
        """Get Elastic Beanstalk logs"""
        if not self.aws_cli_available:
            return {"error": "AWS CLI not available. Install with: pip install awscli"}
        
        try:
            cmd = ["eb", "logs"]
            if environment_name:
                cmd.extend(["-e", environment_name])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "command": " ".join(cmd),
                "success": result.returncode == 0,
                "logs": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except FileNotFoundError:
            return {
                "error": "EB CLI not found. Install with: pip install awsebcli",
                "alternative": "Use AWS Console → Elastic Beanstalk → Environment → Logs"
            }
        except Exception as e:
            return {"error": f"Failed to get EB logs: {e}"}
    
    def get_cloudwatch_logs(self, log_group: str, hours: int = 1) -> Dict[str, Any]:
        """Get CloudWatch logs"""
        if not self.aws_cli_available:
            return {"error": "AWS CLI not available"}
        
        try:
            # Get logs from last N hours
            import datetime
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(hours=hours)
            
            cmd = [
                "aws", "logs", "filter-log-events",
                "--log-group-name", log_group,
                "--start-time", str(int(start_time.timestamp() * 1000)),
                "--end-time", str(int(end_time.timestamp() * 1000))
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    log_data = json.loads(result.stdout)
                    events = log_data.get("events", [])
                    return {
                        "log_group": log_group,
                        "events_count": len(events),
                        "events": events[-50:],  # Last 50 events
                        "success": True
                    }
                except json.JSONDecodeError:
                    return {
                        "log_group": log_group,
                        "raw_output": result.stdout,
                        "success": True
                    }
            else:
                return {
                    "error": f"Failed to get CloudWatch logs: {result.stderr}",
                    "log_group": log_group
                }
                
        except Exception as e:
            return {"error": f"Failed to get CloudWatch logs: {e}"}
    
    def get_elb_health(self, load_balancer_name: str = None) -> Dict[str, Any]:
        """Get ELB health status"""
        if not self.aws_cli_available:
            return {"error": "AWS CLI not available"}
        
        try:
            if load_balancer_name:
                cmd = ["aws", "elb", "describe-instance-health", "--load-balancer-name", load_balancer_name]
            else:
                # List all load balancers first
                cmd = ["aws", "elb", "describe-load-balancers"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return {
                        "command": " ".join(cmd),
                        "data": data,
                        "success": True
                    }
                except json.JSONDecodeError:
                    return {
                        "command": " ".join(cmd),
                        "raw_output": result.stdout,
                        "success": True
                    }
            else:
                return {
                    "error": f"Failed to get ELB health: {result.stderr}",
                    "command": " ".join(cmd)
                }
                
        except Exception as e:
            return {"error": f"Failed to get ELB health: {e}"}
    
    def get_eb_health(self, environment_name: str = None) -> Dict[str, Any]:
        """Get Elastic Beanstalk environment health"""
        try:
            cmd = ["eb", "health"]
            if environment_name:
                cmd.extend(["-e", environment_name])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            return {
                "command": " ".join(cmd),
                "success": result.returncode == 0,
                "health_info": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except FileNotFoundError:
            return {
                "error": "EB CLI not found. Install with: pip install awsebcli",
                "alternative": "Use AWS Console → Elastic Beanstalk → Environment → Health"
            }
        except Exception as e:
            return {"error": f"Failed to get EB health: {e}"}
    
    def get_cloudwatch_metrics(self, metric_name: str, namespace: str, hours: int = 1) -> Dict[str, Any]:
        """Get CloudWatch metrics"""
        if not self.aws_cli_available:
            return {"error": "AWS CLI not available"}
        
        try:
            import datetime
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(hours=hours)
            
            cmd = [
                "aws", "cloudwatch", "get-metric-statistics",
                "--namespace", namespace,
                "--metric-name", metric_name,
                "--start-time", start_time.isoformat(),
                "--end-time", end_time.isoformat(),
                "--period", "300",
                "--statistics", "Average,Maximum"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return {
                        "metric": f"{namespace}/{metric_name}",
                        "datapoints": data.get("Datapoints", []),
                        "success": True
                    }
                except json.JSONDecodeError:
                    return {
                        "metric": f"{namespace}/{metric_name}",
                        "raw_output": result.stdout,
                        "success": True
                    }
            else:
                return {
                    "error": f"Failed to get metrics: {result.stderr}",
                    "metric": f"{namespace}/{metric_name}"
                }
                
        except Exception as e:
            return {"error": f"Failed to get CloudWatch metrics: {e}"}
    
    def suggest_eb_commands(self, issue_type: str = "5xx_errors") -> List[str]:
        """Suggest relevant EB commands based on issue type"""
        commands = {
            "5xx_errors": [
                "eb logs --all",
                "eb health --refresh",
                "eb status",
                "aws logs describe-log-groups --log-group-name-prefix '/aws/elasticbeanstalk'",
                "aws cloudwatch get-metric-statistics --namespace AWS/ELB --metric-name HTTPCode_ELB_5XX"
            ],
            "unhealthy_instances": [
                "eb health",
                "eb ssh",
                "eb logs --all",
                "aws ec2 describe-instance-status"
            ],
            "deployment_issues": [
                "eb logs --all",
                "eb events",
                "eb status",
                "eb health"
            ]
        }
        
        return commands.get(issue_type, commands["5xx_errors"])
    
    def get_eb_environment_info(self) -> Dict[str, Any]:
        """Get current EB environment information"""
        try:
            result = subprocess.run(
                ["eb", "status"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "command": "eb status",
                "success": result.returncode == 0,
                "environment_info": result.stdout,
                "error": result.stderr if result.stderr else None
            }
            
        except FileNotFoundError:
            return {
                "error": "EB CLI not found. Install with: pip install awsebcli",
                "manual_steps": [
                    "1. Go to AWS Console → Elastic Beanstalk",
                    "2. Select your application and environment",
                    "3. Check Health tab for instance status",
                    "4. Check Logs tab for application logs",
                    "5. Check Monitoring tab for metrics"
                ]
            }
        except Exception as e:
            return {"error": f"Failed to get EB environment info: {e}"}