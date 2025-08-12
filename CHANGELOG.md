# Changelog

All notable changes to the Incident Helper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-08

### Added
- **Multi-LLM Provider Support**: Added support for both Ollama (local) and OpenAI (cloud) providers
- **Comprehensive Resolver System**: 
  - SystemResolver: CPU, memory, processes, safe command execution
  - ServiceResolver: systemd services, logs, restart capabilities  
  - LogResolver: Pattern detection, error analysis, real-time monitoring
  - NetworkResolver: Connectivity, DNS, routing diagnostics
  - SSHResolver: Remote access, file transfer, configuration analysis
  - AWSResolver: Elastic Beanstalk logs, health checks, CloudWatch integration
- **Enhanced CLI Experience**: 
  - Rich terminal UI with colors and formatting
  - Interactive command suggestions with auto-execution
  - Built-in help and status commands
  - Quick diagnostic commands
- **Structured Incident Management**:
  - Complete timeline tracking
  - Command execution history with success/failure tracking
  - Severity levels (Low, Medium, High, Critical)
  - Status management (Investigating, Identified, Monitoring, Resolved)
  - Exportable incident reports in JSON format
- **Flexible Severity Input**: Accept multiple formats (1/low, 2/medium, 3/high, 4/critical)
- **Context-Aware AI Prompting**: 
  - Remembers conversation history
  - Detects cloud services (AWS, GCP, Azure, Kubernetes)
  - Provides cloud-specific diagnostic guidance
- **AWS-Specific Commands**:
  - `aws-eb-logs`: Get Elastic Beanstalk logs
  - `aws-eb-health`: Check EB environment health
- **Comprehensive Testing**: Unit tests for all major components
- **Rich Documentation**: Architecture guide, contributing guide, examples

### Enhanced
- **Command Execution**: Safe command execution with sanitization and timeout protection
- **Error Handling**: Graceful degradation when tools/services are unavailable
- **User Experience**: Clear error messages, progressive disclosure, context-aware suggestions
- **Prompting System**: Specialized prompts for different analysis types (logs, system, network)

### Fixed
- **Entry Point Issues**: Resolved CLI installation and execution problems
- **LLM Initialization**: Fixed provider initialization with proper error handling
- **Context Management**: Improved session state management and persistence

### Security
- **Command Sanitization**: Dangerous command detection and user confirmation
- **No Hardcoded Secrets**: All sensitive data uses environment variables
- **Safe Defaults**: Conservative permissions and timeout settings

## [0.1.0] - 2024-12-08

### Added
- Initial release with basic conversational CLI
- Simple Ollama integration
- Basic context management
- Placeholder resolver architecture
- Typer-based CLI framework

### Features
- Natural language incident reporting
- Basic AI-powered diagnostic suggestions
- Simple session management
- Command-line interface with Typer

---

## Upcoming Features (Roadmap)

### [0.3.0] - Planned
- **Cloud Integration**: Enhanced AWS, GCP, Azure resource monitoring
- **Kubernetes Support**: Pod diagnostics, cluster health checks
- **Monitoring Integration**: Prometheus, Grafana, DataDog connectors
- **Playbook System**: Automated response procedures
- **Web Interface**: Browser-based incident management

### [0.4.0] - Planned  
- **Team Collaboration**: Multi-user incident response
- **Alerting Integration**: PagerDuty, Slack notifications
- **Machine Learning**: Pattern recognition and predictive analysis
- **Plugin Marketplace**: Community-contributed resolvers
- **Advanced Reporting**: Incident analytics and trends