import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from incident_helper.cli import app
from incident_helper.context import IncidentContext, IncidentSeverity

runner = CliRunner()

def test_quick_check_command():
    """Test the quick-check command"""
    result = runner.invoke(app, ["quick-check"])
    assert result.exit_code == 0
    assert "Running quick health check" in result.stdout

def test_analyze_logs_command():
    """Test the analyze-logs command"""
    with patch('incident_helper.resolvers.logs.LogResolver.analyze_error_patterns') as mock_analyze:
        mock_analyze.return_value = {"error_count": 5, "patterns": {}}
        
        result = runner.invoke(app, ["analyze-logs", "/var/log/test.log"])
        assert result.exit_code == 0
        mock_analyze.assert_called_once()

def test_test_connectivity_command():
    """Test the test-connectivity command"""
    with patch('incident_helper.resolvers.network.NetworkResolver.check_connectivity') as mock_check:
        mock_check.return_value = {"connectivity_score": "1/1", "successful_connections": 1}
        
        result = runner.invoke(app, ["test-connectivity", "google.com"])
        assert result.exit_code == 0
        mock_check.assert_called_once()

@pytest.fixture
def incident_context():
    """Create a test incident context"""
    ctx = IncidentContext()
    ctx.set("alert", "Test incident")
    ctx.set_severity(IncidentSeverity.MEDIUM)
    return ctx

def test_incident_context_creation(incident_context):
    """Test incident context creation and management"""
    assert incident_context.get("alert") == "Test incident"
    assert incident_context.severity == IncidentSeverity.MEDIUM
    assert len(incident_context.timeline) > 0

def test_incident_context_command_tracking(incident_context):
    """Test command execution tracking"""
    incident_context.add_command("ls -la", "file1\nfile2", True)
    
    assert len(incident_context.commands_executed) == 1
    assert incident_context.commands_executed[0]["command"] == "ls -la"
    assert incident_context.commands_executed[0]["success"] == True

def test_incident_context_export(incident_context):
    """Test incident report export"""
    report = incident_context.export_report()
    assert "incident_summary" in report
    assert "timeline" in report
    assert "commands_executed" in report