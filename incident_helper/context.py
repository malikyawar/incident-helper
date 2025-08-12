import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"

class IncidentContext:
    def __init__(self):
        self.data = {}
        self.commands_executed = []
        self.timeline = []
        self.severity = None
        self.status = IncidentStatus.INVESTIGATING
        self.start_time = datetime.now()
        
    def set(self, key: str, value: Any):
        self.data[key] = value
        self._add_timeline_entry(f"Set {key}: {value}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def add_command(self, command: str, output: str, success: bool = True):
        """Track executed commands and their outputs"""
        cmd_entry = {
            "command": command,
            "output": output,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.commands_executed.append(cmd_entry)
        self._add_timeline_entry(f"Executed: {command}")
    
    def _add_timeline_entry(self, entry: str):
        self.timeline.append({
            "timestamp": datetime.now().isoformat(),
            "entry": entry
        })
    
    def set_severity(self, severity: IncidentSeverity):
        self.severity = severity
        self._add_timeline_entry(f"Severity set to: {severity.value}")
    
    def set_status(self, status: IncidentStatus):
        self.status = status
        self._add_timeline_entry(f"Status changed to: {status.value}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive incident summary"""
        return {
            "alert": self.get("alert", "Unknown incident"),
            "severity": self.severity.value if self.severity else "unknown",
            "status": self.status.value,
            "duration": str(datetime.now() - self.start_time),
            "commands_run": len(self.commands_executed),
            "os": self.get("os", "unknown"),
            "environment": self.get("environment", "unknown"),
            "affected_services": self.get("affected_services", [])
        }
    
    def export_report(self) -> str:
        """Export incident report as JSON"""
        report = {
            "incident_summary": self.get_summary(),
            "timeline": self.timeline,
            "commands_executed": self.commands_executed,
            "context_data": self.data
        }
        return json.dumps(report, indent=2)
