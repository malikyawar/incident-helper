import pytest
from unittest.mock import Mock, patch, mock_open
from incident_helper.resolvers.system import SystemResolver
from incident_helper.resolvers.logs import LogResolver
from incident_helper.resolvers.network import NetworkResolver
from incident_helper.resolvers.services import ServiceResolver

class TestSystemResolver:
    def test_get_system_info(self):
        resolver = SystemResolver()
        info = resolver.get_system_info()
        
        assert "os" in info
        assert "hostname" in info
        assert "cpu_count" in info

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success output",
            stderr=""
        )
        
        resolver = SystemResolver()
        result = resolver.run_command("echo test")
        
        assert result["success"] == True
        assert result["stdout"] == "success output"

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error output"
        )
        
        resolver = SystemResolver()
        result = resolver.run_command("false")
        
        assert result["success"] == False
        assert result["stderr"] == "error output"

class TestLogResolver:
    def test_find_log_files(self):
        resolver = LogResolver()
        with patch('os.path.exists', return_value=True), \
             patch('os.stat') as mock_stat, \
             patch('os.access', return_value=True):
            
            mock_stat.return_value = Mock(st_size=1024, st_mtime=1234567890)
            
            logs = resolver.find_log_files()
            assert len(logs) > 0
            assert all("path" in log for log in logs)

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('os.access', return_value=True)
    def test_tail_log(self, mock_access, mock_exists, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="line1\nline2\nline3"
        )
        
        resolver = LogResolver()
        result = resolver.tail_log("/var/log/test.log", 3)
        
        assert result["success"] == True
        assert len(result["lines"]) == 3

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_search_logs(self, mock_exists, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="1:error line\n2:another error"
        )
        
        resolver = LogResolver()
        result = resolver.search_logs("/var/log/test.log", "error")
        
        assert result["success"] == True
        assert result["match_count"] == 2

class TestNetworkResolver:
    @patch('subprocess.run')
    def test_ping_host_success(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="PING google.com: 4 packets transmitted, 4 received",
            stderr=""
        )
        
        resolver = NetworkResolver()
        result = resolver.ping_host("google.com", 4)
        
        assert result["success"] == True
        assert result["host"] == "google.com"

    @patch('socket.socket')
    def test_test_port_open(self, mock_socket):
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        resolver = NetworkResolver()
        result = resolver.test_port("google.com", 80)
        
        assert result["open"] == True
        assert result["success"] == True

    @patch('socket.socket')
    def test_test_port_closed(self, mock_socket):
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        resolver = NetworkResolver()
        result = resolver.test_port("google.com", 12345)
        
        assert result["open"] == False
        assert result["success"] == True

class TestServiceResolver:
    @patch('subprocess.run')
    def test_get_systemd_service_status(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="● nginx.service - A high performance web server\n   Loaded: loaded\n   Active: active (running)"
        )
        
        resolver = ServiceResolver()
        result = resolver.get_service_status("nginx")
        
        assert result["success"] == True
        assert result["service"] == "nginx"
        assert "active" in result

    @patch('subprocess.run')
    def test_list_failed_services(self, mock_run):
        mock_run.return_value = Mock(
            returncode=0,
            stdout="UNIT                     LOAD   ACTIVE SUB    DESCRIPTION\nfailed-service.service   loaded failed failed Test service"
        )
        
        resolver = ServiceResolver()
        result = resolver.list_failed_services()
        
        assert len(result) > 0
        assert any("failed-service.service" in str(service) for service in result)