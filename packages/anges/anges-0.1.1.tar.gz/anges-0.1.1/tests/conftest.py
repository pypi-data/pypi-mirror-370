import pytest
from dotenv import load_dotenv
import os

def pytest_configure(config):
    """Load environment variables before any tests run"""
    # Load from .env file
    load_dotenv()
    
    # Verify critical environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please ensure these are set in your .env file"
        )