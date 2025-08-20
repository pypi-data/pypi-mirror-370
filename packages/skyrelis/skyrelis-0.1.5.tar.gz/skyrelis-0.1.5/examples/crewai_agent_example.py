"""
CrewAI Agent Observability Example

This example demonstrates how to use the new CrewAI observability features
with the agent decorators framework. It shows how to monitor CrewAI agents,
tasks, and crews with automatic telemetry collection.
"""

import os
from typing import Dict, Any

# Set up environment variables for the demo
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
os.environ["REMOTE_OBSERVER_URL"] = "http://localhost:8000"

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import tool
    from langchain_openai import ChatOpenAI
except ImportError:
    print("CrewAI not installed. Install with: pip install crewai langchain-openai")
    exit(1)

# Import our observability decorators
from agent_decorators import observe_agent, observe_crewai_agent, get_framework_info


# Example tools for our agents
@tool
def search_web(query: str) -> str:
    """Search the web for information on a given query."""
    # In a real implementation, this would use a search API
    return f"Search results for '{query}': Found relevant information about {query}."


@tool
def analyze_data(data: str) -> str:
    """Analyze the provided data and extract insights."""
    # In a real implementation, this would perform actual data analysis
    return f"Analysis of data: The data shows interesting patterns and trends related to {data[:50]}..."


@tool
def write_report(content: str) -> str:
    """Write a formatted report based on the provided content."""
    # In a real implementation, this would format the content properly
    return f"Report generated: {content[:100]}... [Report continues with proper formatting]"


# Example 1: Basic CrewAI Agent with observability
@observe_crewai_agent(
    remote_observer_url="http://localhost:8000",
    agent_name="research_specialist",
    capture_metadata=True
)
class MonitoredResearchAgent(Agent):
    """A research agent with built-in observability."""
    
    def __init__(self):
        super().__init__(
            role='Senior Research Analyst',
            goal='Conduct thorough research and provide comprehensive insights',
            backstory="""You are a seasoned research analyst with over 10 years of experience 
                        in gathering, analyzing, and synthesizing information from multiple sources. 
                        You have a keen eye for detail and excel at identifying patterns and trends.""",
            tools=[search_web, analyze_data],
            verbose=True,
            allow_delegation=False,
            llm=ChatOpenAI(model="gpt-4", temperature=0.1)
        )


# Example 2: Using the general observe_agent decorator
@observe_agent(
    remote_observer_url="http://localhost:8000",
    agent_name="content_writer",
    capture_metadata=True
)
def create_content_writer():
    """Create a content writer agent."""
    return Agent(
        role='Content Writer',
        goal='Create engaging and well-structured content based on research findings',
        backstory="""You are a professional content writer with expertise in transforming 
                    complex research into clear, engaging, and accessible content. You understand 
                    your audience and know how to communicate complex ideas simply.""",
        tools=[write_report],
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    )


# Example 3: Creating a full CrewAI workflow with observability
def create_monitored_research_crew():
    """Create a crew with monitored agents for research and content creation."""
    
    # Create agents
    researcher = MonitoredResearchAgent()
    writer = create_content_writer()
    
    # Define tasks
    research_task = Task(
        description="""Conduct comprehensive research on the latest trends in AI agent frameworks.
                      Focus on:
                      1. Current market leaders and their capabilities
                      2. Emerging technologies and innovations
                      3. Use cases and real-world applications
                      4. Future outlook and predictions
                      
                      Provide detailed findings with supporting data and examples.""",
        expected_output="A comprehensive research report with key findings, data points, and insights",
        agent=researcher
    )
    
    content_creation_task = Task(
        description="""Based on the research findings, create an engaging blog post about 
                      AI agent frameworks. The blog post should:
                      1. Have a compelling introduction
                      2. Present the research findings in an accessible way
                      3. Include practical examples and use cases
                      4. Provide actionable insights for readers
                      5. Have a strong conclusion with key takeaways
                      
                      Target audience: Technical professionals and AI enthusiasts.""",
        expected_output="A well-structured blog post of 1000-1500 words in markdown format",
        agent=writer,
        context=[research_task]  # This task depends on the research task
    )
    
    # Create and return the crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, content_creation_task],
        process=Process.sequential,
        verbose=2
    )
    
    return crew


# Example 4: Demonstrating framework detection and metadata extraction
def demonstrate_framework_detection():
    """Show how the framework detection and metadata extraction works."""
    
    print("🔍 Framework Detection and Metadata Extraction Demo")
    print("=" * 60)
    
    # Show supported frameworks
    frameworks = get_framework_info()
    print("\n📋 Supported Frameworks:")
    for framework in frameworks:
        print(f"  - {framework['name']}: {framework['available']}")
        print(f"    Version: {framework['version_requirement']}")
        print(f"    Adapter: {framework['adapter_class']}")
        print()
    
    # Create a CrewAI agent and extract metadata
    agent = Agent(
        role='Demo Agent',
        goal='Demonstrate metadata extraction',
        backstory='A simple agent for demonstration purposes.',
        tools=[search_web],
        verbose=True,
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    )
    
    # Import framework registry for direct access
    from agent_decorators.core.framework_adapters import registry
    
    # Detect framework
    adapter = registry.detect_framework(agent)
    if adapter:
        print(f"🎯 Detected Framework: {adapter.framework_name}")
        
        # Extract metadata
        metadata = adapter.extract_agent_metadata(agent)
        print("\n📊 Extracted Metadata:")
        print(f"  Agent Type: {metadata.get('agent_type', 'Unknown')}")
        print(f"  Framework: {metadata.get('framework', 'Unknown')}")
        
        # Show system prompts
        system_prompts = metadata.get('system_prompts', [])
        if system_prompts:
            print(f"\n💬 System Prompts ({len(system_prompts)} found):")
            for i, prompt in enumerate(system_prompts, 1):
                print(f"  {i}. {prompt['type']} from {prompt['source']}")
                print(f"     Template: {prompt['template'][:100]}...")
        
        # Show tools
        tools = metadata.get('tools', [])
        if tools:
            print(f"\n🛠️  Tools ({len(tools)} found):")
            for tool in tools:
                print(f"  - {tool['name']} ({tool['type']})")
                if tool.get('description'):
                    print(f"    Description: {tool['description']}")
        
        # Show LLM info
        llm_info = metadata.get('llm_info', {})
        if llm_info:
            print(f"\n🤖 LLM Configuration:")
            for key, value in llm_info.items():
                if value is not None:
                    print(f"  {key}: {value}")
    else:
        print("❌ Framework not detected or not supported")


def main():
    """Main demo function."""
    print("🚀 CrewAI Observability Demo")
    print("=" * 50)
    
    # Demo 1: Framework detection
    demonstrate_framework_detection()
    
    print("\n" + "=" * 50)
    print("🎬 Running CrewAI Workflow with Observability")
    print("=" * 50)
    
    # Create the monitored crew
    crew = create_monitored_research_crew()
    
    # Run the crew workflow
    try:
        result = crew.kickoff(inputs={
            "topic": "AI Agent Frameworks"
        })
        
        print("\n✅ Workflow completed successfully!")
        print("\n📄 Final Result:")
        print("-" * 30)
        print(result)
        
        # Show telemetry information
        print("\n📊 Observability Information:")
        print("- All agent interactions have been captured")
        print("- Traces sent to observer at:", os.getenv("REMOTE_OBSERVER_URL"))
        print("- Agent metadata extracted and stored")
        print("- Tool usage and LLM calls monitored")
        
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        print("Make sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Started the agent monitor service")
        print("3. Installed required dependencies: pip install crewai langchain-openai")


if __name__ == "__main__":
    # Check if we're in the right environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        print("You can do this by running: export OPENAI_API_KEY=your-key-here")
        exit(1)
    
    main() 