**Languages**: [English](README.md) | [中文](zh/README.md)

---
# Anges Documentation

Welcome to the comprehensive documentation for **Anges**, an AI agent framework designed for multi-step task execution in Linux environments. This documentation hub provides everything you need to understand, use, and extend the Anges framework.

## 🚀 Getting Started

New to Anges? Follow this recommended learning path:

1. **Start Here**: Read the [Architecture Overview](#architecture-documentation) to understand core concepts
2. **See It in Action**: Explore [Code Examples](#code-examples) to see practical implementations
3. **Build Your Own**: Follow the [Implementation Guide](#implementation-guide) to create custom agents and actions
4. **Reference**: Use the [API Reference](#api-reference) for detailed technical specifications

## 📚 Documentation Structure

### Architecture Documentation
**File**: [`architecture.md`](./architecture.md)

**What's Inside**: Comprehensive technical documentation covering the core architectural components of Anges, including:
- Event loop system and execution flow
- Action system architecture and lifecycle
- Agent framework design patterns
- Core abstractions and interfaces
- System integration patterns

**Best For**: Developers who want to understand how Anges works under the hood, system architects, and contributors to the project.

### API Reference
**File**: [`api-reference.md`](./api-reference.md)

**What's Inside**: Complete API documentation framework providing:
- Core API specifications
- Method signatures and parameters
- Return types and error handling
- Usage examples for each API endpoint
- Integration guidelines

**Best For**: Developers integrating Anges into existing systems, API consumers, and those needing quick reference during development.

### Implementation Guide
**File**: [`implementation-guide.md`](./implementation-guide.md)

**What's Inside**: Step-by-step instructions for extending Anges with custom functionality:
- Creating custom agents with specialized behaviors
- Developing custom actions for specific use cases
- Best practices for extension development
- Testing and validation strategies
- Real-world implementation patterns


### CLI Usage Guide
**File**: [`cli-usage.md`](./cli-usage.md)

**What's Inside**: Comprehensive command-line interface documentation covering:
- All CLI arguments and modes of operation
- Interactive, file-based, and direct question modes
- Notes feature for providing contextual information
- JSON format requirements and usage examples
- Web interface launch options

**Best For**: Users who prefer command-line interaction, automation scripts, and those needing to provide structured context through the notes feature.

### Documentation Examples
**Directory**: [`examples/`](./examples/)

**What's Inside**: Curated examples and demonstrations within the documentation:
- Code snippets and usage patterns
- Configuration examples
- Integration scenarios
- Best practice demonstrations

**Best For**: Learning by example, quick reference, and understanding documentation patterns.

## 💻 Code Examples

### Project Examples Directory
**Location**: [`../examples/`](../examples/)

The main examples directory contains practical, runnable code demonstrations:

#### Available Examples

- **[`basic_usage.py`](../examples/basic_usage.py)**
  - Simple agent setup and basic task execution
  - Perfect starting point for new users
  - Demonstrates core workflow patterns

- **[`custom_agent.py`](../examples/custom_agent.py)**
  - Complete custom agent implementation
  - Shows advanced agent customization techniques
  - Includes error handling and state management

- **[`custom_action.py`](../examples/custom_action.py)**
  - Custom action development examples
  - Demonstrates action lifecycle and integration
  - Shows parameter handling and validation

- **[`orchestrator_demo.py`](../examples/orchestrator_demo.py)**
  - Advanced orchestration patterns
  - Multi-agent coordination examples
  - Complex workflow demonstrations

## 🗺️ Documentation Navigation Guide

### For New Users
1. **Understand the Basics**: Start with [`architecture.md`](./architecture.md) - Event Loop System section
2. **See It Work**: Run [`../examples/basic_usage.py`](../examples/basic_usage.py)
3. **Learn the API**: Browse [`api-reference.md`](./api-reference.md) - Getting Started section

### For Developers
1. **Architecture Deep Dive**: Read [`architecture.md`](./architecture.md) completely
2. **API Mastery**: Study [`api-reference.md`](./api-reference.md) - Core API section
3. **Custom Development**: Follow [`implementation-guide.md`](./implementation-guide.md)
4. **Advanced Examples**: Explore [`../examples/custom_agent.py`](../examples/custom_agent.py) and [`../examples/custom_action.py`](../examples/custom_action.py)

### For System Integrators
1. **Integration Patterns**: [`architecture.md`](./architecture.md) - System Integration section
2. **API Integration**: [`api-reference.md`](./api-reference.md) - Integration Guidelines
3. **Orchestration**: [`../examples/orchestrator_demo.py`](../examples/orchestrator_demo.py)

### For Contributors
1. **Complete Architecture**: [`architecture.md`](./architecture.md)
2. **Extension Patterns**: [`implementation-guide.md`](./implementation-guide.md)
3. **All Examples**: Review entire [`../examples/`](../examples/) directory

## 🔧 Quick Reference

### Key Concepts
- **Agent**: The core AI entity that processes tasks and makes decisions
- **Action**: Individual operations that agents can perform (shell commands, file operations, etc.)
- **Event Loop**: The execution engine that manages agent-action interactions
- **Task**: A user request that may require multiple steps to complete

### Common Use Cases
- **System Administration**: Automate complex multi-step operations
- **Development Workflows**: Intelligent code analysis and modification
- **Data Processing**: Multi-stage data transformation pipelines
- **Infrastructure Management**: Automated deployment and configuration

## 📖 Additional Resources

### Documentation Maintenance
This documentation is actively maintained and updated. Each file includes:
- Last updated timestamps
- Version compatibility information
- Change logs for major updates

### Getting Help
- **Issues**: Report documentation issues or request improvements
- **Examples**: Request additional examples for specific use cases
- **Contributions**: Guidelines for contributing to documentation

### Documentation Standards
All documentation follows consistent formatting and includes:
- Clear section headers and navigation
- Practical examples with explanations
- Cross-references between related concepts
- Progressive complexity from basic to advanced topics

---

**Next Steps**: Choose your path above based on your role and experience level. Each documentation file is designed to be self-contained while linking to related concepts across the documentation set.

*Happy building with Anges! 🚀*