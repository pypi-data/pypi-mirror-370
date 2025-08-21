#!/usr/bin/env python3
"""
Test script for Daytona CLI commands
"""

import asyncio
import subprocess
import sys
import os

def run_command(command, expected_success=True):
    """Run a CLI command and check its output"""
    print(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if expected_success and result.returncode != 0:
            print(f"❌ Command failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        elif not expected_success and result.returncode == 0:
            print("❌ Command succeeded when expected to fail")
            return False
        else:
            print("✅ Command executed successfully")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return True
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False

async def test_daytona_cli():
    """Test Daytona CLI commands"""
    print("Testing Daytona CLI commands")
    print("=" * 50)
    
    # Use the correct Python path
    python_cmd = sys.executable  # This will use the current Python interpreter
    
    # Test 1: Check if CLI is accessible
    print("\n1. Testing CLI accessibility")
    if not run_command(f"{python_cmd} -m reasoning_kernel.cli --help"):
        return False
    
    # Test 2: Test sandbox command group help
    print("\n2. Testing sandbox command group")
    if not run_command(f"{python_cmd} -m reasoning_kernel.cli sandbox --help"):
        return False
    
    # Test 3: Test sandbox status command
    print("\n3. Testing sandbox status command")
    # This might fail due to missing Daytona API key, but we'll check that it at least runs
    result = subprocess.run(f"{python_cmd} -m reasoning_kernel.cli sandbox status", 
                          shell=True, capture_output=True, text=True)
    # We expect this to either succeed or fail with a specific error about Daytona not being available
    if result.returncode != 0 and "Daytona service not available" not in result.stdout and "Daytona service not available" not in result.stderr:
        print(f"❌ Command failed unexpectedly with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    else:
        print("✅ Command executed (expected behavior)")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    
    # Test 4: Test sandbox execute command help
    print("\n4. Testing sandbox execute command help")
    if not run_command(f"{python_cmd} -m reasoning_kernel.cli sandbox execute --help"):
        return False
    
    # Test 5: Test sandbox monitor command
    print("\n5. Testing sandbox monitor command")
    # This might fail due to missing Daytona API key, but we'll check that it at least runs
    result = subprocess.run(f"{python_cmd} -m reasoning_kernel.cli sandbox monitor", 
                          shell=True, capture_output=True, text=True)
    # We expect this to either succeed or fail with a specific error about Daytona not being available
    if result.returncode != 0 and "Daytona service not initialized" not in result.stdout and "Daytona service not initialized" not in result.stderr:
        print(f"❌ Command failed unexpectedly with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    else:
        print("✅ Command executed (expected behavior)")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
    
    # Test 6: Test configuration command
    print("\n6. Testing configuration command")
    if not run_command(f"{python_cmd} -m reasoning_kernel.cli config daytona --show"):
        return False
    
    print("\n" + "=" * 50)
    print("✅ All Daytona CLI tests passed!")
    return True

if __name__ == "__main__":
    # Change to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Run tests
    success = asyncio.run(test_daytona_cli())
    sys.exit(0 if success else 1)