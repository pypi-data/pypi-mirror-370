<!-- Language Switcher -->
**Language**: [English](README.md) | [中文](../zh/examples/README.md)

---
# Anges Examples

This directory contains practical example code demonstrating various features and usage patterns of the Anges framework.

## Available Examples

The examples directory contains the following demonstration files:

### [`basic_usage.py`](../../examples/basic_usage.py)
**Purpose**: Demonstrates fundamental usage of the Anges framework  
**Features**: Creating a default agent, running simple tasks, basic configuration  
**Best for**: Getting started with Anges, understanding core concepts  

### [`custom_agent.py`](../../examples/custom_agent.py)
**Purpose**: Shows how to create custom agents by extending the BaseAgent class  
**Features**: Custom agent implementation, specialized behavior, agent-specific logic  
**Best for**: Building specialized agents for specific use cases  

### [`custom_action.py`](../../examples/custom_action.py)
**Purpose**: Demonstrates creating custom actions for extending framework capabilities  
**Features**: Custom action implementation, Git operations example, action integration  
**Best for**: Adding new functionality to agents through custom actions  

### [`orchestrator_demo.py`](../../examples/orchestrator_demo.py)
**Purpose**: Shows how to use the Orchestrator for coordinating multiple agents  
**Features**: Multi-agent coordination, complex task delegation, orchestration patterns  
**Best for**: Managing complex workflows with multiple specialized agents  

## Running Examples

### Prerequisites
- Anges framework installed and configured
- Required environment variables set (see main README.md)
- Python 3.8+ environment

### Basic Usage
```bash
# Run from the project root directory
cd examples/
python basic_usage.py
```

### Custom Agent Example
```bash
cd examples/
python custom_agent.py
```

### Custom Action Example
```bash
cd examples/
python custom_action.py
```

### Orchestrator Demo
```bash
cd examples/
python orchestrator_demo.py
```

## Example Structure

Each example file includes:
- **Header documentation**: Clear description of the example's purpose
- **Import statements**: Required Anges framework components
- **Implementation**: Working code demonstrating specific features
- **Usage functions**: Practical demonstrations of the implemented functionality
- **Main execution**: Example usage when run as a script

## Learning Path

1. **Start with**: [`basic_usage.py`](../../examples/basic_usage.py) to understand core concepts
2. **Extend knowledge**: [`custom_agent.py`](../../examples/custom_agent.py) for specialized agents
3. **Add functionality**: [`custom_action.py`](../../examples/custom_action.py) for custom capabilities
4. **Scale up**: [`orchestrator_demo.py`](../../examples/orchestrator_demo.py) for complex workflows

## Related Documentation

- **[Implementation Guide](../implementation-guide.md)**: Detailed implementation instructions
- **[API Reference](../api-reference.md)**: Complete API documentation
- **[Architecture Overview](../architecture.md)**: System design and concepts
- **[Main Documentation](../README.md)**: Documentation overview and navigation
