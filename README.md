# 🛠️ Incident Helper CLI v2.0

## AI-powered incident response tool for SREs and DevOps engineers

Triage incidents, analyze logs, debug systems, and execute diagnostics with AI assistance. Built for production environments with comprehensive system integration.

## 🚀 Key Features

### 🔍 **Intelligent Incident Management**
- Natural language incident reporting and analysis
- Structured incident workflow with severity tracking
- Comprehensive incident timeline and command history
- Automated report generation

### 🤖 **Multi-LLM Support**
- **Ollama** (local): Mistral, Llama2, CodeLlama, etc.
- **OpenAI**: GPT-3.5, GPT-4
- Pluggable architecture for easy model switching

### 🛠️ **Comprehensive System Diagnostics**
- **System Resources**: CPU, memory, disk, processes
- **Service Management**: systemd, service status, logs
- **Network Diagnostics**: connectivity, DNS, routing
- **Log Analysis**: pattern detection, error analysis
- **SSH Operations**: remote diagnostics, file transfer

### 💻 **Enhanced CLI Experience**
- Rich terminal UI with colors and formatting
- Interactive command suggestions with auto-execution
- Quick health checks and targeted diagnostics
- Real-time command execution and output analysis

## 📦 Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com) (for local LLM) or OpenAI API key
- System tools: `systemctl`, `journalctl`, `netstat`, `ping`, etc.

### Install
```bash
git clone https://github.com/malikyawar/incident-helper.git
cd incident-helper
pip install -e .

# For development
pip install -e ".[dev]"
```

### Setup LLM Provider

**Option 1: Ollama (Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull mistral
```

**Option 2: OpenAI**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Usage

### Interactive Incident Response
```bash
# Start with Ollama (default)
incident-helper start

# Use OpenAI
incident-helper start --provider openai --model gpt-4

# Auto-execute suggested commands
incident-helper start --auto-execute
```

### Quick Diagnostics
```bash
# System health check
incident-helper quick-check

# Check specific service
incident-helper quick-check --service nginx

# Analyze logs
incident-helper analyze-logs /var/log/nginx/error.log --pattern "error"

# Test connectivity
incident-helper test-connectivity google.com --port 443
```

### Example Session
```bash
$ incident-helper start

🛠️ Incident Helper - AI-powered SRE Assistant
✅ Using ollama provider

👋 Describe your incident
> Web server returning 502 errors

🔍 Gathering system context...
Environment [production]: production
Severity [1 (Low)/2 (Medium)/3 (High)/4 (Critical)]: 3

💬 Starting diagnostic conversation...

🤖 AI Assistant
Based on 502 errors from your web server, let's check the upstream services first.

Let's examine the nginx error logs:
`tail -f /var/log/nginx/error.log`

This will show recent errors. What do you see in the logs?

> I see "connect() failed (111: Connection refused) while connecting to upstream"

🤖 AI Assistant  
The upstream service is refusing connections. Let's check if your application server is running:

`systemctl status your-app-service`

What's the status of your application service?

> !systemctl status myapp
⚡ Executing: systemctl status myapp
❌ Command failed
Error: Unit myapp.service could not be found.

🤖 AI Assistant
The service isn't found. Let's list all failed services:
`systemctl --failed`

This will show any services that have failed to start.
```

## 🔧 Advanced Features

### Command Execution
- Prefix commands with `!` to execute directly: `!ps aux | grep nginx`
- Auto-execution mode suggests and runs commands with confirmation
- All commands are logged with output for incident reports

### Built-in Commands
- `help` - Show available commands
- `status` - Display current incident status
- `report` - Generate incident report
- `exit` - End session with optional report generation

### System Integration
The tool integrates with common system utilities:
- **systemd**: Service management and logs
- **journalctl**: System journal analysis  
- **netstat/ss**: Network connection analysis
- **ping/traceroute**: Network diagnostics
- **SSH**: Remote system access
- **Log files**: Automated log analysis

## 🏗️ Architecture

### Resolver System
Modular diagnostic components:
- `SystemResolver`: CPU, memory, processes, command execution
- `ServiceResolver`: systemd services, status, logs
- `LogResolver`: Log file analysis, pattern detection
- `NetworkResolver`: Connectivity, DNS, routing
- `SSHResolver`: Remote access, file transfer

### Context Management
- Structured incident tracking with timeline
- Command history with success/failure tracking
- Severity and status management
- Exportable incident reports

### LLM Integration
- Provider abstraction for multiple LLM services
- Context-aware prompting for diagnostic guidance
- Specialized prompts for different analysis types

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=incident_helper

# Run specific test
pytest tests/test_cli.py::test_quick_check_command
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest`
5. Format code: `black incident_helper/`
6. Submit a pull request

## 📋 Roadmap

- [ ] **Cloud Integration**: AWS, GCP, Azure resource monitoring
- [ ] **Kubernetes Support**: Pod diagnostics, cluster health
- [ ] **Monitoring Integration**: Prometheus, Grafana, DataDog
- [ ] **Alerting**: PagerDuty, Slack notifications
- [ ] **Playbooks**: Automated response procedures
- [ ] **Web Interface**: Browser-based incident management
- [ ] **Team Collaboration**: Multi-user incident response

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.
