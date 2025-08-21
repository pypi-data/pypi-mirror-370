#!/usr/bin/env python3
"""
Test script to verify MSA Reasoning Kernel installation
"""

import subprocess
import sys

def run_command(command, expected_success=True):
    """Run a command and check its output"""
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
                print(f"STDOUT: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
            if result.stderr:
                print(f"STDERR: {result.stderr[:200]}{'...' if len(result.stderr) > 200 else ''}")
            return True
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False

def test_installation():
    """Test MSA Reasoning Kernel installation"""
    print("Testing MSA Reasoning Kernel installation")
    print("=" * 50)
    
    # Test 1: Check if CLI is accessible
    print("\n1. Testing CLI accessibility")
    if not run_command("reasoning-kernel --help"):
        return False
    
    # Test 2: Check version command
    print("\n2. Testing version command")
    if not run_command("reasoning-kernel version"):
        return False
    
    # Test 3: Check that core modules are available
    print("\n3. Testing core modules import")
    try:
        import reasoning_kernel
        print(f"✅ reasoning_kernel imported successfully (version: {reasoning_kernel.__version__})")
        
        from reasoning_kernel.cli import main
        print("✅ reasoning_kernel.cli imported successfully")
        
        from reasoning_kernel.core import KernelManager
        print("✅ reasoning_kernel.core imported successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All installation tests passed!")
    return True

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)