#!/usr/bin/env python3
"""
Demo script showing how agents can use MCP tools
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from agents.mcp_client import mcp_client_manager, MCPServerConfig, use_mcp_tool
from agents.base_agent import BaseAgent, AgentConfig
from utils.config_loader import ConfigLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDeveloperAgent(BaseAgent):
    """Mock developer agent for testing MCP tools"""
    
    def _format_task(self, task: str) -> str:
        return f"Development task: {task}"
    
    def _process_response(self, response: str, task: str, context: dict) -> dict:
        return {
            'success': True,
            'agent': self.name,
            'output': response,
            'task': task
        }

async def demo_mcp_tools():
    """Demonstrate MCP tools functionality"""
    
    print("🔧 MCP Tools Demo - Agent Tool Usage")
    print("=" * 50)
    
    # Configure a simple filesystem MCP server
    filesystem_config = MCPServerConfig(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        description="File system operations for testing",
        enabled=True
    )
    
    print(f"📁 Adding filesystem MCP server...")
    mcp_client_manager.add_server(filesystem_config)
    
    # Try to connect to the server
    print(f"🔌 Connecting to filesystem server...")
    try:
        connected = await mcp_client_manager.connect_to_server("filesystem")
        if connected:
            print("✅ Successfully connected to filesystem server")
            
            # List available tools
            tools = mcp_client_manager.get_server_tools("filesystem")
            print(f"🛠  Available tools: {list(tools.keys())}")
        else:
            print("❌ Failed to connect to filesystem server")
            print("ℹ️  This demo requires Node.js and the MCP filesystem server package")
            return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("ℹ️  This demo requires Node.js and the MCP filesystem server package")
        return
    
    # Create a mock agent with tool capabilities
    agent_config = AgentConfig(
        name="Developer",
        model={
            'provider': 'openai',
            'model': 'gpt-4',
            'temperature': 0.7
        },
        description="Developer agent with MCP tool access",
        tools_enabled=True,
        available_tools=["read_file", "write_file", "list_directory"],
        max_tool_calls=3
    )
    
    # We'll simulate tool usage without actually creating the agent
    # since it would require API keys
    
    print("\n🤖 Simulating Agent Tool Usage")
    print("-" * 30)
    
    # Test 1: Create a file
    print("📝 Test 1: Creating a test file...")
    result = await use_mcp_tool("write_file", {
        "path": "/tmp/mcp_demo.txt", 
        "content": "Hello from MCP tools demo!\nThis file was created by an AI agent using MCP tools."
    })
    
    if result['success']:
        print("✅ File created successfully")
        print(f"   Result: {result['result'][:100]}...")
    else:
        print(f"❌ Failed to create file: {result['error']}")
    
    # Test 2: Read the file back
    print("\n📖 Test 2: Reading the file back...")
    result = await use_mcp_tool("read_file", {"path": "/tmp/mcp_demo.txt"})
    
    if result['success']:
        print("✅ File read successfully")
        print(f"   Content: {result['result']}")
    else:
        print(f"❌ Failed to read file: {result['error']}")
    
    # Test 3: List directory contents
    print("\n📂 Test 3: Listing directory contents...")
    result = await use_mcp_tool("list_directory", {"path": "/tmp"})
    
    if result['success']:
        print("✅ Directory listed successfully")
        lines = result['result'].split('\n')
        demo_files = [line for line in lines[:10] if 'mcp_demo' in line or 'test' in line]
        if demo_files:
            print(f"   Found demo files: {demo_files}")
        else:
            print(f"   Directory contents (first 10 items): {lines[:10]}")
    else:
        print(f"❌ Failed to list directory: {result['error']}")
    
    print("\n🎯 Key Benefits Demonstrated:")
    print("  ✓ Agents can use external tools through MCP")
    print("  ✓ Tools are dynamically discovered and called")
    print("  ✓ Multiple servers can provide different capabilities")
    print("  ✓ Tool calls are logged and trackable")
    print("  ✓ Error handling for failed tool operations")
    
    # Cleanup
    await mcp_client_manager.shutdown()
    print("\n✅ Demo completed!")

async def demo_agent_workflow_with_tools():
    """Demonstrate how agents would use tools in a workflow"""
    
    print("\n🔄 Agent Workflow with Tools Demo")
    print("=" * 40)
    
    # This demonstrates how an agent's response would be processed
    # when it includes tool calls
    
    mock_agent_response = """
    I'll help you create a Python web application. Let me start by checking what files exist and creating the project structure.
    
    [TOOL_CALL: list_directory | {"path": "/tmp"}]
    
    Now I'll create the main application file:
    
    [TOOL_CALL: write_file | {"path": "/tmp/app.py", "content": "from flask import Flask\\n\\napp = Flask(__name__)\\n\\n@app.route('/')\\ndef hello():\\n    return 'Hello World!'\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)"}]
    
    And let me read it back to verify:
    
    [TOOL_CALL: read_file | {"path": "/tmp/app.py"}]
    
    Perfect! I've created a basic Flask application with the following features:
    - Simple route handler for the home page
    - Debug mode enabled for development
    - Clean, minimal structure
    """
    
    print("📄 Mock Agent Response:")
    print(mock_agent_response)
    
    print("\n🔧 Processing Tool Calls...")
    
    # Simulate the tool call processing that would happen in BaseAgent._process_tool_calls
    import re
    
    tool_call_pattern = r'\[TOOL_CALL:\s*([^|]+)\s*\|\s*(\{[^}]*\}|\{.*?\})\s*\]'
    tool_calls = list(re.finditer(tool_call_pattern, mock_agent_response))
    
    print(f"Found {len(tool_calls)} tool calls:")
    
    for i, match in enumerate(tool_calls, 1):
        tool_name = match.group(1).strip()
        try:
            import json
            arguments = json.loads(match.group(2).strip())
        except:
            arguments = {}
        
        print(f"\n  {i}. Tool: {tool_name}")
        print(f"     Args: {arguments}")
        
        # Here we would call: await use_mcp_tool(tool_name, arguments)
        # and replace the tool call with the result
    
    print("\n💡 In a real workflow:")
    print("  • Each tool call would be executed")
    print("  • Results would replace the [TOOL_CALL:...] markers")
    print("  • The enhanced response would be processed normally")
    print("  • The agent would have access to real tool results")

def show_configuration_info():
    """Show how to configure MCP tools for agents"""
    
    print("\n⚙️  MCP Configuration Guide")
    print("=" * 30)
    
    print("📋 1. Server Configuration (mcp_servers.yaml):")
    config_example = """
servers:
  filesystem:
    enabled: true
    command: npx
    args: ['-y', '@modelcontextprotocol/server-filesystem', '/tmp']
    description: 'File system operations'
    timeout: 30
  web_search:
    enabled: true
    command: npx
    args: ['-y', '@modelcontextprotocol/server-brave-search']
    env:
      BRAVE_API_KEY: '${BRAVE_API_KEY}'
    description: 'Web search capabilities'

agent_tools:
  developer: ['filesystem', 'git', 'web_search']
  tester: ['filesystem', 'git']
  planner: ['web_search']
"""
    print(config_example)
    
    print("🤖 2. Agent Configuration:")
    agent_config_example = """
# In agent configuration
tools_enabled: true
available_tools: ['filesystem', 'web_search', 'git']
max_tool_calls: 5
"""
    print(agent_config_example)
    
    print("🌐 3. Web Interface:")
    print("  • Visit /mcp-config.html for GUI configuration")
    print("  • Add/remove servers dynamically")
    print("  • Configure agent tool access")
    print("  • Monitor connection status")
    
    print("\n📝 4. Usage in Agent Responses:")
    usage_example = """
# Agents can use this syntax in their responses:
[TOOL_CALL: read_file | {"path": "/path/to/file.py"}]
[TOOL_CALL: web_search | {"query": "Python FastAPI tutorial"}]
[TOOL_CALL: git_status | {}]
"""
    print(usage_example)

async def main():
    """Main demo function"""
    print("🚀 MCP Tools Integration Demo")
    print("🔗 Model Context Protocol + AI Agents")
    print("=" * 50)
    
    # Show configuration information first
    show_configuration_info()
    
    # Demo agent workflow processing
    await demo_agent_workflow_with_tools()
    
    # Only run the live demo if filesystem tools might work
    user_input = input("\n❓ Would you like to run the live filesystem tools demo? (requires Node.js) [y/N]: ")
    if user_input.lower().startswith('y'):
        await demo_mcp_tools()
    else:
        print("ℹ️  Skipping live demo - configuration and workflow examples completed!")
    
    print("\n🎉 MCP Integration Ready!")
    print("✅ Agents now have access to external tools")
    print("✅ Configure tools through web interface")
    print("✅ Tools are called automatically when agents need them")

if __name__ == "__main__":
    asyncio.run(main())