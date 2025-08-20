# Skyrelis Changelog

All notable changes to the Skyrelis AI Agent Security Library will be documented in this file.

## [0.1.3] - 2024-08-12

### 🚀 Major Features Added

#### **Multi-Framework Support**
- Added comprehensive **CrewAI** framework support alongside existing LangChain support
- Implemented plugin-based framework detection system
- Universal `@observe_agent` decorator with automatic framework detection

#### **CrewAI Integration**
- Full support for CrewAI agents, tasks, crews, and workflows
- OpenTelemetry-based instrumentation integration
- Rich metadata extraction from roles, goals, backstories
- Automatic workflow tracing (`Crew.kickoff`, `Agent.execute_task`, `Task.execute_sync`)

#### **Framework Plugin Architecture**
- `BaseFrameworkAdapter` interface for extensible framework support
- `FrameworkRegistry` for managing multiple framework adapters
- Easy framework addition without breaking existing functionality

### ✨ New Features

#### **Enhanced Decorators**
- `@observe_crewai_agent` - CrewAI-specific decorator with targeted features
- `@observe_agent` - Universal decorator supporting all frameworks
- Enhanced metadata capture across frameworks

#### **Developer Experience**
- `get_supported_frameworks()` - Check available framework support
- `get_framework_info()` - Detailed framework information and status
- Automatic framework detection with graceful fallbacks

### 🔧 Technical Improvements
- Clean separation of framework-specific logic
- Lazy loading of framework dependencies
- Enhanced error handling and graceful degradation
- Performance optimizations for framework detection

### 📦 Dependencies
- Added optional `crewai` extras: `pip install skyrelis[crewai]`
- OpenTelemetry integration dependencies for CrewAI support
- Maintained minimal core dependencies

### 🔄 Migration Guide

#### From v0.1.2 to v0.1.3:
```python
# v0.1.2 (still works in v0.1.3)
from skyrelis import observe

@observe()
class MyLangChainAgent(AgentExecutor):
    pass

# v0.1.3 - New multi-framework support
from skyrelis import observe_agent, observe_crewai_agent

@observe_agent()  # Auto-detects framework
def create_any_agent():
    return agent  # Works with LangChain, CrewAI, etc.

@observe_crewai_agent()  # CrewAI-specific
class MyCrewAIAgent(Agent):
    pass
```

---

## [0.1.2] - 2024-07-26

### Previous Release
- LangChain agent observability and security
- Basic monitoring and tracing capabilities
- Agent metadata extraction
- Integration with monitoring dashboard 