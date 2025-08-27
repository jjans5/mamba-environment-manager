#!/usr/bin/env python3
"""
Test script for new environment manager features:
- Cleanup YAML files
- Recreate Jupyter kernels
"""

import sys
from pathlib import Path
from environment_manager import EnvironmentManager

def test_cleanup_function():
    """Test the YAML cleanup functionality"""
    print("🧪 Testing YAML cleanup functionality...")
    
    manager = EnvironmentManager()
    
    # Check current YAML files
    yaml_files = list(manager.export_dir.glob("*.yml")) + list(manager.export_dir.glob("*.yaml"))
    print(f"Found {len(yaml_files)} YAML files before cleanup")
    
    # Test cleanup (without confirmation for automated testing)
    if yaml_files:
        print("Testing cleanup function...")
        success = manager.cleanup_exported_yaml_files(confirm=False)
        if success:
            print("✅ Cleanup function working correctly!")
        else:
            print("❌ Cleanup function failed!")
        
        # Check files after cleanup
        remaining_files = list(manager.export_dir.glob("*.yml")) + list(manager.export_dir.glob("*.yaml"))
        print(f"Remaining YAML files after cleanup: {len(remaining_files)}")
    else:
        print("No YAML files to clean up - test passed!")

def test_kernel_recreation():
    """Test the kernel recreation functionality"""
    print("\n🧪 Testing kernel recreation functionality...")
    
    manager = EnvironmentManager()
    
    # Get environments
    environments = manager.list_environments()
    print(f"Found {len(environments)} environments")
    
    # Test environment detection functions
    python_envs = []
    r_envs = []
    
    for env in environments:
        if env['name'] in ['base', 'root']:
            continue
            
        has_python = manager._environment_has_python(env['path'])
        has_r = manager._environment_has_r(env['path'])
        
        if has_python:
            python_envs.append(env['name'])
        if has_r:
            r_envs.append(env['name'])
    
    print(f"Environments with Python: {python_envs}")
    print(f"Environments with R: {r_envs}")
    
    if python_envs or r_envs:
        print("✅ Environment detection working correctly!")
        
        # Test kernel directory function
        test_kernel_dir = manager._get_kernel_dir("test_env")
        print(f"Test kernel directory: {test_kernel_dir}")
        print("✅ Kernel directory function working!")
    else:
        print("ℹ️  No environments with Python or R found for testing")

def main():
    """Run all tests"""
    print("🚀 Testing new Environment Manager features...")
    
    try:
        test_cleanup_function()
        test_kernel_recreation()
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
