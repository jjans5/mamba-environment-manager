#!/usr/bin/env python3
"""
HPC Test Script for Environment Manager

Simple test to verify HPC compatibility and basic functionality.
"""

import subprocess
import sys
import os
from pathlib import Path

def test_conda_mamba():
    """Test if conda/mamba is available"""
    print("=== Testing conda/mamba availability ===")
    
    for cmd in ['mamba', 'conda']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] {cmd} available: {result.stdout.strip()}")
                return cmd
            else:
                print(f"[FAIL] {cmd} not available")
        except FileNotFoundError:
            print(f"[FAIL] {cmd} not found")
    
    print("ERROR: Neither mamba nor conda found!")
    return None

def test_environment_listing(cmd):
    """Test environment listing"""
    print(f"\n=== Testing environment listing with {cmd} ===")
    
    try:
        result = subprocess.run([cmd, 'env', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            env_count = 0
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    env_count += 1
            print(f"[OK] Found {env_count} environments")
            
            # Show first few environments
            for line in lines[:5]:
                if line.strip() and not line.startswith('#'):
                    print(f"  - {line.strip()}")
            
            return True
        else:
            print(f"[FAIL] Failed to list environments: {result.stderr}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_environment_manager():
    """Test if environment manager can be imported"""
    print("\n=== Testing Environment Manager Import ===")
    
    try:
        import environment_manager
        print("[OK] Environment manager imported successfully")
        
        # Test basic initialization
        manager = environment_manager.EnvironmentManager()
        print(f"[OK] Manager initialized with: {manager.cmd_base}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_yaml_export():
    """Test YAML export functionality"""
    print("\n=== Testing YAML Export (Quick Test) ===")
    
    try:
        import environment_manager
        manager = environment_manager.EnvironmentManager()
        
        # Get first environment
        environments = manager.list_environments()
        if environments:
            test_env = environments[0]['name']
            print(f"Testing export of environment: {test_env}")
            
            result = manager.export_environment(test_env)
            if result and result != "EMPTY":
                print(f"[OK] Export successful: {result}")
                return True
            else:
                print(f"[FAIL] Export failed or environment empty")
                return False
        else:
            print("[FAIL] No environments found to test")
            return False
            
    except Exception as e:
        print(f"[FAIL] Export test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("HPC Environment Manager Compatibility Test")
    print("=" * 50)
    
    # Test conda/mamba
    cmd = test_conda_mamba()
    if not cmd:
        sys.exit(1)
    
    # Test environment listing
    if not test_environment_listing(cmd):
        print("WARNING: Environment listing failed")
    
    # Test environment manager
    if not test_environment_manager():
        print("ERROR: Environment manager failed to initialize")
        sys.exit(1)
    
    # Test YAML export
    if not test_yaml_export():
        print("WARNING: YAML export test failed")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Basic compatibility tests completed!")
    print("\nYou can now run:")
    print("  python environment_manager.py")
    print("\nFor your clone issue, try:")
    print("1. conda install conda-pack  # Install conda-pack first")
    print("2. Use YAML method instead of conda-pack")
    print("3. Check that 'py_jjans_3.10' environment exists")

if __name__ == "__main__":
    main()
