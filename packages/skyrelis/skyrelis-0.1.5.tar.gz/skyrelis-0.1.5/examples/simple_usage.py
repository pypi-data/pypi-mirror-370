#!/usr/bin/env python3
"""
Skyrelis AI Agent Security Library - Simple Usage Example

This example shows how easy it is to add enterprise-grade security 
monitoring to your AI agents with just one decorator.
"""

import os
from typing import List

# Install: pip install skyrelis langchain langchain-openai
from skyrelis import observe
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import StructuredTool


# Define some simple tools for demonstration
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # In a real app, this would call a weather API
    return f"Weather in {location}: Sunny, 72°F"

def search_database(query: str) -> str:
    """Search the company database."""
    # In a real app, this would query your database
    return f"Database results for '{query}': 3 matching records found"

def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    # In a real app, this would send actual emails
    return f"Email sent to {recipient} with subject '{subject}'"


# Create LangChain tools
tools = [
    StructuredTool.from_function(get_weather),
    StructuredTool.from_function(search_database), 
    StructuredTool.from_function(send_email)
]

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful business assistant with access to various tools.
    
    You can:
    - Check weather information
    - Search the company database
    - Send emails on behalf of users
    
    Always be helpful, accurate, and professional. Use tools when appropriate."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create the agent
agent = create_openai_functions_agent(llm, tools, prompt)


# 🔒 ADD ENTERPRISE SECURITY WITH ONE DECORATOR! 🔒
@observe(
    monitor_url=os.getenv("SKYRELIS_MONITOR_URL", "https://your-security-monitor.com"),
    agent_name="business_assistant",
    security_level="production"
)
class SecureBusinessAgent(AgentExecutor):
    """
    A secure business assistant with full observability.
    
    This agent now has:
    ✅ Complete execution tracing
    ✅ System prompt monitoring
    ✅ Tool usage auditing  
    ✅ Real-time security alerts
    ✅ Compliance logging
    ✅ Agent registry integration
    """
    pass


def main():
    """Demonstrate the secure agent in action."""
    print("🔒 Skyrelis AI Agent Security Library Demo")
    print("=" * 50)
    
    # Initialize the secure agent
    secure_agent = SecureBusinessAgent(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Example interactions - all will be monitored and audited
    test_queries = [
        "What's the weather like in New York?",
        "Search the database for customer information about Smith",
        "Send an email to john@company.com about the quarterly report",
        "What tools do you have available?"
    ]
    
    print("\n🤖 Running secure agent interactions...")
    print("All interactions are being monitored for security!")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        try:
            # This invoke call is automatically monitored
            result = secure_agent.invoke({"input": query})
            print(f"✅ Response: {result['output']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Errors are also captured and monitored
    
    print("\n🎉 Demo complete!")
    print("\nSecurity Data Captured:")
    print("✅ System prompts and agent configuration")
    print("✅ All user inputs and agent outputs")
    print("✅ Tool calls and their parameters/results")
    print("✅ LLM interactions and token usage") 
    print("✅ Performance metrics and timing")
    print("✅ Any errors or security events")
    print("\nCheck your Skyrelis security monitor for complete audit trail!")


if __name__ == "__main__":
    # Set up environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-openai-api-key'")
        exit(1)
    
    if not os.getenv("SKYRELIS_MONITOR_URL"):
        print("ℹ️  Using default monitor URL. Set SKYRELIS_MONITOR_URL for your monitor:")
        print("   export SKYRELIS_MONITOR_URL='https://your-security-monitor.com'")
    
    main() 