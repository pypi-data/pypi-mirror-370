"""Anges - Comprehensive Agent Orchestration Framework for AI-Powered Automation"""

__version__ = "0.1.0"
__author__ = "Anges Team"
__email__ = "me@anges.ai"
__description__ = "Comprehensive Agent Orchestration Framework for AI-Powered Automation"

# Import main components for easy access
try:
    from .cli import main as cli_main
except ImportError:
    pass
