#!/usr/bin/env python3
"""
Test script to verify interactive mode functionality
"""

import subprocess
import time
import sys

def test_interactive_mode():
    """Test the interactive mode by sending commands programmatically"""
    print("Testing interactive mode...")
    
    # Test 1: Basic interactive mode startup
    print("\n=== Test 1: Interactive mode startup ===")
    proc = subprocess.Popen(
        [sys.executable, "-m", "anges.cli", "-i"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/hailongli/anges-dev"
    )
    
    # Send help command
    stdout, stderr = proc.communicate(input="help\nquit\n")
    
    print("STDERR output:")
    print(stderr)
    print("\nSTDOUT output:")
    print(stdout)
    print(f"\nExit code: {proc.returncode}")
    
    # Test 2: Test with a simple task
    print("\n=== Test 2: Simple task processing ===")
    proc2 = subprocess.Popen(
        [sys.executable, "-m", "anges.cli", "-i"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/hailongli/anges-dev"
    )
    
    # Send a simple task and then quit
    stdout2, stderr2 = proc2.communicate(input="echo hello world\nexit\n")
    
    print("STDERR output:")
    print(stderr2)
    print("\nSTDOUT output:")
    print(stdout2)
    print(f"\nExit code: {proc2.returncode}")
    
    return proc.returncode == 0 and proc2.returncode == 0

if __name__ == "__main__":
    success = test_interactive_mode()
    if success:
        print("\n✅ Interactive mode tests passed!")
    else:
        print("\n❌ Interactive mode tests failed!")
    sys.exit(0 if success else 1)