#!/usr/bin/env python3
"""Test script to verify the AgentFactory refactoring works correctly."""

from anges.agents.agent_utils.agent_factory import AgentFactory, AgentType, AgentConfig

def test_all_agent_types():
    """Test creating all native agent types."""
    print("Testing AgentFactory with all native agent types...")
    
    for agent_type in AgentType:
        try:
            config = AgentConfig(agent_type=agent_type.value)
            agent = AgentFactory.create_agent(config)
            print(f"✓ Created {agent_type.value}: {type(agent).__name__}")
        except Exception as e:
            print(f"✗ Failed to create {agent_type.value}: {e}")

def test_byo_agent():
    """Test creating a BYO agent."""
    print("\nTesting BYO agent creation...")
    
    try:
        config = AgentConfig(
            agent_type="byo",
            custom_module="anges.agents.default_agent",
            custom_class="DefaultAgent"
        )
        agent = AgentFactory.create_agent(config)
        print(f"✓ Created BYO agent: {type(agent).__name__}")
    except Exception as e:
        print(f"✗ Failed to create BYO agent: {e}")

if __name__ == "__main__":
    test_all_agent_types()
    test_byo_agent()
    print("\nAgent factory testing completed!")