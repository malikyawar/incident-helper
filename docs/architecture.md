# Incident Helper Architecture

## Overview

The Incident Helper is designed as a modular, extensible system for AI-powered incident response. The architecture follows a clean separation of concerns with pluggable components for different diagnostic capabilities.

## Core Components

### 1. CLI Layer (`cli.py`)
- **Typer-based CLI** with rich terminal UI
- **Command routing** and user interaction
- **Session management** and flow control
- **Rich formatting** for better UX

### 2. Context Management (`context.py`)
- **IncidentContext**: Central state management
- **Timeline tracking**: All actions and responses
- **Command history**: Executed commands with outputs
- **Status management**: Severity, status, metadata
- **Report generation**: JSON export for documentation

### 3. LLM Integration (`agents.py`)
- **Provider abstraction**: Support multiple LLM services
- **OllamaProvider**: Local LLM integration
- **OpenAIProvider**: Cloud LLM integration
- **Error handling**: Graceful degradation
- **Timeout management**: Prevent hanging requests

### 4. Resolver System
Modular diagnostic components that handle specific system aspects:

#### SystemResolver (`resolvers/system.py`)
- System information gathering
- Resource usage monitoring
- Process management
- Command execution with safety checks

#### ServiceResolver (`resolvers/services.py`)
- systemd service management
- Service status checking
- Log retrieval
- Service restart capabilities

#### LogResolver (`resolvers/logs.py`)
- Log file discovery
- Pattern searching
- Error analysis
- Real-time monitoring

#### NetworkResolver (`resolvers/network.py`)
- Connectivity testing
- DNS resolution
- Port scanning
- Network diagnostics

#### SSHResolver (`resolvers/ssh.py`)
- Remote connectivity testing
- Command execution
- File transfer
- SSH configuration analysis

### 5. Prompt Engineering (`prompts.py`)
- **Context-aware prompts**: Tailored to incident type
- **Diagnostic prompts**: Guide troubleshooting steps
- **Analysis prompts**: Interpret command outputs
- **Specialized prompts**: For different resolver types

### 6. Utilities (`utils.py`)
- **Formatting helpers**: Human-readable output
- **Pattern extraction**: Error detection
- **Validation**: Input sanitization
- **Parsing**: Log and command output analysis

## Data Flow

```
User Input → CLI → Context → LLM → Resolver → System → Context → CLI → User
```

1. **User provides incident description**
2. **CLI captures and validates input**
3. **Context stores incident data**
4. **LLM analyzes context and suggests actions**
5. **Resolver executes diagnostic commands**
6. **System returns results**
7. **Context logs all actions**
8. **CLI presents formatted results**

## Key Design Principles

### 1. Modularity
- Each resolver is independent
- Easy to add new diagnostic capabilities
- Clean interfaces between components

### 2. Safety
- Command sanitization
- Dangerous command detection
- User confirmation for destructive actions
- Timeout protection

### 3. Extensibility
- Plugin architecture for new LLM providers
- Resolver system for new diagnostic types
- Configurable prompts and behaviors

### 4. Observability
- Complete command history
- Timeline tracking
- Structured logging
- Exportable reports

### 5. User Experience
- Rich terminal interface
- Clear error messages
- Progressive disclosure
- Context-aware suggestions

## Configuration

### LLM Providers
```python
# Ollama (local)
llm = LLMEngine(provider="ollama", model="mistral")

# OpenAI (cloud)
llm = LLMEngine(provider="openai", model="gpt-4")
```

### Resolver Configuration
Each resolver can be configured independently:
```python
system_resolver = SystemResolver()
service_resolver = ServiceResolver()
# ... etc
```

## Error Handling

### Graceful Degradation
- LLM failures don't stop diagnostic execution
- Individual resolver failures are isolated
- Fallback to manual command suggestions

### User Feedback
- Clear error messages
- Suggested remediation steps
- Alternative approaches when tools fail

## Security Considerations

### Command Execution
- Whitelist of safe commands
- Dangerous pattern detection
- User confirmation for risky operations
- No automatic privilege escalation

### Data Handling
- Local context storage
- No sensitive data in logs
- Optional report encryption
- Configurable data retention

## Performance

### Optimization Strategies
- Lazy loading of resolvers
- Caching of system information
- Parallel execution where safe
- Timeout management

### Resource Management
- Memory-efficient context storage
- Streaming for large outputs
- Cleanup of temporary files
- Connection pooling for remote operations

## Testing Strategy

### Unit Tests
- Individual resolver testing
- Context management validation
- Prompt generation verification
- Utility function coverage

### Integration Tests
- End-to-end CLI workflows
- LLM provider integration
- System command execution
- Error handling scenarios

### Mock Testing
- External service simulation
- Command output mocking
- Network failure simulation
- Permission error handling

## Future Enhancements

### Planned Features
1. **Cloud Integration**: AWS, GCP, Azure monitoring
2. **Container Support**: Docker, Kubernetes diagnostics
3. **Monitoring Integration**: Prometheus, Grafana
4. **Collaboration**: Multi-user incident response
5. **Automation**: Playbook execution
6. **Web Interface**: Browser-based management

### Architecture Evolution
- Microservice decomposition for scale
- Event-driven architecture for real-time updates
- Plugin marketplace for community resolvers
- Machine learning for pattern recognition