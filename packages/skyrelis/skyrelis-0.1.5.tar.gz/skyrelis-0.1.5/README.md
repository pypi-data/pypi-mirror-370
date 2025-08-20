# 🔒 Skyrelis: AI Agent Security Library

**Enterprise-grade security for AI agents, starting with comprehensive observability.**

[![PyPI version](https://badge.fury.io/py/skyrelis.svg)](https://badge.fury.io/py/skyrelis)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-orange.svg)](https://github.com/skyrelis/skyrelis/blob/main/LICENSE)
[![Security](https://img.shields.io/badge/security-focused-red.svg)](https://skyrelis.com)

---

## 🛡️ **Why Agent Security Matters**

As AI agents become more powerful and autonomous, they present new security challenges:
- **Prompt Injection Attacks**: Malicious inputs that hijack agent behavior
- **Data Exposure**: Agents accessing sensitive information inappropriately  
- **Uncontrolled Actions**: Agents performing unintended or harmful operations
- **Compliance Risks**: Lack of audit trails for regulated industries

**Skyrelis provides the security foundation your AI agents need.**

---

## ✨ Current Security Features (v1.0)

🔍 **Complete Observability** - Full visibility into agent execution and decision-making  
🎯 **System Prompt Security** - Monitor and protect agent instructions and behaviors  
📊 **Real-time Monitoring** - Instant alerts for suspicious agent activities  
🏷️ **Agent Registry** - Centralized inventory and security posture management  
🔗 **Zero-Config Integration** - Add security with just a decorator  
⚡ **Production Ready** - Built for enterprise scale and reliability  
🌐 **Standards Compliant** - OpenTelemetry, audit logging, and compliance ready  

## 🚧 Coming Soon (Roadmap)

🛡️ **Prompt Injection Detection** - AI-powered input validation and threat detection  
🏗️ **Agent Sandboxing** - Isolated execution environments with controlled permissions  
👥 **Access Control & RBAC** - Role-based permissions for agent operations  
🧠 **Behavioral Analysis** - ML-based anomaly detection for agent activities  
📋 **Compliance Frameworks** - SOC2, GDPR, HIPAA compliance tools  
🔐 **Secret Management** - Secure handling of API keys and sensitive data  

---

## 🚀 Quick Start

### Installation

```bash
pip install skyrelis
```

### Secure Your Agent in 30 Seconds

Transform any LangChain agent into a security-monitored agent with one decorator:

```python
from skyrelis import observe
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Your normal LangChain agent setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use tools when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_openai_functions_agent(llm, tools, prompt)

# Add enterprise security monitoring with one decorator! 🔒
@observe(remote_observer_url="https://your-security-monitor.com")
class SecureAgent(AgentExecutor):
    pass

# Initialize and use - now with full security monitoring
secure_agent = SecureAgent(agent=agent, tools=tools)
result = secure_agent.invoke({"input": "What's the weather like?"})

# Your agent now has:
# ✅ Complete execution tracing
# ✅ System prompt monitoring  
# ✅ Real-time security alerts
# ✅ Audit trail compliance
# ✅ Agent behavior analysis
```

## 🔒 What Security Data Gets Captured

When you add the `@observe` decorator, Skyrelis automatically captures security-relevant data:

### 🤖 **Agent Security Profile**
- **System Prompts**: Complete instructions given to the agent
- **Tool Access**: What tools the agent can use and how  
- **LLM Configuration**: Model settings, temperature, safety filters
- **Permission Scope**: What the agent is authorized to do

### 📊 **Execution Security Logs** 
- **Input Validation**: All user inputs and their sources
- **Tool Invocations**: Every tool call with parameters and results
- **LLM Interactions**: Complete conversation logs with the language model
- **Output Analysis**: All agent responses and actions taken
- **Error Tracking**: Security-relevant errors and failures

### 🚨 **Security Events**
- **Unusual Behavior**: Deviations from expected agent patterns
- **Failed Operations**: Blocked or failed actions that might indicate attacks
- **Access Attempts**: Unauthorized access attempts to tools or data
- **Performance Anomalies**: Unusual response times or resource usage

### 📋 **Compliance & Audit**
- **Complete Audit Trail**: Every action with timestamps and context
- **User Attribution**: Who triggered each agent interaction
- **Data Access Logs**: What data was accessed or modified
- **Retention Management**: Automated log retention per compliance requirements

---

## 🎛️ Security Configuration

### Basic Security Setup
```python
@observe(
    monitor_url="https://your-security-monitor.com",
    agent_name="customer_service_agent",
    security_level="production",  # "development", "staging", "production"
)
class CustomerServiceAgent(AgentExecutor):
    pass
```

### Advanced Security Configuration
```python
@observe(
    monitor_url="https://your-security-monitor.com",
    agent_name="financial_advisor_agent",
    security_level="production",
    enable_audit_logging=True,      # Full audit trail
    enable_anomaly_detection=True,  # Behavioral analysis (coming soon)
    enable_input_validation=True,   # Prompt injection detection (coming soon)
    compliance_mode="SOC2",         # Compliance framework (coming soon)
    alert_thresholds={              # Security alerting
        "unusual_tool_usage": 0.8,
        "response_time_anomaly": 2.0,
        "error_rate_spike": 0.1
    }
)
class FinancialAdvisorAgent(AgentExecutor):
    pass
```

### Environment-Based Security
```bash
# Security monitoring endpoints
export SKYRELIS_MONITOR_URL="https://your-security-monitor.com"
export SKYRELIS_SECURITY_LEVEL="production"

# Compliance and audit
export SKYRELIS_AUDIT_RETENTION_DAYS="2555"  # 7 years for financial compliance
export SKYRELIS_COMPLIANCE_MODE="SOC2"

# Alert destinations
export SKYRELIS_SLACK_WEBHOOK="https://hooks.slack.com/..."
export SKYRELIS_SECURITY_EMAIL="security-team@company.com"
```

---

## 🔧 Security Integration Examples

### High-Security Financial Agent
```python
from skyrelis import observe
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool

def get_account_balance(account_id: str) -> str:
    # This tool access is now fully monitored and audited
    return f"Account {account_id}: $10,000"

@observe(
    monitor_url="https://security.bank.com/monitor",
    security_level="production",
    compliance_mode="SOX",
    enable_audit_logging=True
)
class BankingAgent(AgentExecutor):
    pass

# Every interaction is now compliance-ready and security-monitored
```

### Customer Service with Threat Detection
```python
@observe(
    monitor_url="https://security.company.com/monitor",
    enable_anomaly_detection=True,      # Detect unusual customer behavior
    enable_input_validation=True,       # Block prompt injection attempts  
    alert_on_threats=True              # Real-time security alerts
)
class CustomerServiceAgent(AgentExecutor):
    pass

# Agent automatically detects and blocks security threats
```

### Research Agent with Data Protection
```python
@observe(
    monitor_url="https://security.research.com/monitor",
    data_classification="confidential",
    enable_data_loss_prevention=True,  # Prevent sensitive data exposure
    audit_data_access=True            # Log all data access events
)
class ResearchAgent(AgentExecutor):
    pass

# Complete data protection and access monitoring
```

---

## 📊 Security Monitoring Dashboard

The Skyrelis Security Monitor provides:

### 🚨 **Real-time Security Alerts**
- **Threat Detection**: Immediate alerts for security events
- **Anomaly Notifications**: Unusual agent behavior alerts  
- **Compliance Violations**: Regulatory compliance failures
- **Performance Issues**: Security-impacting performance problems

### 📈 **Security Analytics**
- **Agent Risk Scores**: Security posture assessment for each agent
- **Threat Landscape**: Attack patterns and security trends
- **Compliance Reporting**: Automated compliance status reports
- **Incident Response**: Security event investigation tools

### 🔍 **Agent Security Inventory**
- **Security Profiles**: All agents with their security configurations
- **Permission Mapping**: What each agent can access and do
- **Vulnerability Assessment**: Security weaknesses and recommendations
- **Policy Compliance**: Adherence to security policies

### 📋 **Audit & Compliance**
- **Complete Audit Trail**: Every action logged for compliance
- **Regulatory Reports**: SOC2, GDPR, HIPAA compliance reporting
- **Data Lineage**: Track data flow through agent operations
- **Retention Management**: Automated compliance-based data retention

---

## 🏗️ Security Architecture

Skyrelis Security Architecture:

1. **Security Decorator**: Wraps agents with security monitoring
2. **Agent Registry**: Centralizes agent security profiles and policies
3. **Real-time Monitoring**: Captures all security-relevant events
4. **Threat Detection**: AI-powered security analysis (coming soon)
5. **Compliance Engine**: Automated compliance and audit reporting
6. **Alert System**: Real-time security notifications and incident response

All security monitoring happens transparently - your agent code remains unchanged while gaining enterprise-grade security!

---

## 📦 Installation Options

```bash
# Basic security monitoring
pip install skyrelis

# With advanced security features (coming soon)
pip install skyrelis[security]

# With compliance reporting
pip install skyrelis[compliance]

# With threat detection (coming soon)  
pip install skyrelis[threat-detection]

# Everything
pip install skyrelis[all]
```

---

## 🎯 Why Choose Skyrelis?

### **For Security Teams**
- **Zero Agent Code Changes**: Add security without disrupting development
- **Complete Visibility**: See everything your agents are doing
- **Compliance Ready**: Built-in support for major compliance frameworks
- **Threat Detection**: AI-powered security monitoring

### **For Development Teams**  
- **One-Line Integration**: Just add a decorator
- **No Performance Impact**: Lightweight, async monitoring
- **Development Friendly**: Rich debugging and troubleshooting tools
- **Production Ready**: Battle-tested at enterprise scale

### **For Compliance Officers**
- **Automated Audit Trails**: Complete logging without manual work
- **Regulatory Support**: SOC2, GDPR, HIPAA, SOX compliance
- **Risk Assessment**: Continuous security posture monitoring
- **Incident Response**: Complete investigation capabilities

---

## 🤝 Contributing

We welcome contributions to make AI agents more secure! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License & Commercial Use

**Skyrelis is proprietary software** - see the [LICENSE](LICENSE) file for details.

### 🏢 **Commercial Licensing**

- **Evaluation & Development**: Free for non-commercial evaluation and development
- **Commercial Use**: Requires a separate commercial license agreement
- **Enterprise**: Contact us for enterprise licensing and support

📧 **Licensing Inquiries**: [security@skyrelis.com](mailto:security@skyrelis.com)

### 🔒 **Why Proprietary?**

As an AI agent security platform, Skyrelis requires:
- **Enterprise Support**: Dedicated support for mission-critical security
- **Compliance Guarantees**: Legal assurances for regulated industries  
- **Advanced Features**: Continuous development of cutting-edge security capabilities
- **Professional Services**: Security consulting and custom implementations

## 🆘 Support

- 📚 **Documentation**: [skyrelis.readthedocs.io](https://skyrelis.readthedocs.io)
- 🔒 **Security Issues**: [security@skyrelis.com](mailto:security@skyrelis.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/skyrelis/skyrelis/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/skyrelis/skyrelis/discussions)

---

**Made with 🔒 by the Skyrelis Security Team**

*Skyrelis: Securing AI agents for the enterprise.* 