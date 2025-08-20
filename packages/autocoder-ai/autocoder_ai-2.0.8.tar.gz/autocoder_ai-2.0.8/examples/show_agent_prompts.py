#!/usr/bin/env python3
"""
Example script to demonstrate the enhanced agent prompts
"""

from utils.agent_prompts import AGENT_SYSTEM_PROMPTS

def display_agent_prompts():
    """Display a summary of each agent's prompt"""
    print("=" * 80)
    print("AUTOCODER AGENT SYSTEM PROMPTS")
    print("=" * 80)
    
    for agent_name, prompt in AGENT_SYSTEM_PROMPTS.items():
        print(f"\n{'='*40}")
        print(f"AGENT: {agent_name.upper()}")
        print(f"{'='*40}")
        
        # Extract and display the first paragraph as a summary
        lines = prompt.split('\n')
        summary_lines = []
        for line in lines[:10]:  # Get first 10 lines for summary
            if line.strip():
                summary_lines.append(line.strip())
            if len(summary_lines) >= 3:
                break
        
        print("\nSUMMARY:")
        for line in summary_lines[:3]:
            print(f"  {line}")
        
        # Extract operating principles
        if "## Operating Principles" in prompt:
            print("\nOPERATING PRINCIPLES:")
            principles_start = prompt.index("## Operating Principles")
            principles_section = prompt[principles_start:principles_start+500]
            principle_lines = principles_section.split('\n')[1:7]
            for line in principle_lines:
                if line.strip() and line.strip()[0].isdigit():
                    print(f"  {line.strip()}")

if __name__ == "__main__":
    display_agent_prompts()
    
    print("\n" + "=" * 80)
    print("USAGE EXAMPLE:")
    print("=" * 80)
    print("""
To use these prompts in your agents, the base_agent.py automatically loads them:

from agents.base_agent import BaseAgent, AgentConfig

config = AgentConfig(
    name="planner",
    model={"provider": "openai", "model": "gpt-4"},
    description="Planning and coordination agent"
)

agent = PlannerAgent(config)
# The agent will automatically use the professional planner prompt
""")
