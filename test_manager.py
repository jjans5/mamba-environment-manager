#!/usr/bin/env python3
"""
Test script for the Environment Manager
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment_manager import EnvironmentManager

def test_basic_functionality():
    """Test basic functionality of the environment manager"""
    try:
        print("Testing Environment Manager initialization...")
        manager = EnvironmentManager()
        
        print("Testing environment listing...")
        environments = manager.list_environments()
        print(f"Found {len(environments)} environments")
        
        if environments:
            existing_names = [env['name'].lower() for env in environments]
            for env in environments[:5]:  # Show first 5
                print(f"- {env['name']} (Python: {env['python_version']}, R: {env['r_version']})")
                
                # Show cleaned version if applicable
                cleaned = manager._clean_existing_versions(env['name'].lower())
                if cleaned != env['name'].lower():
                    print(f"  Cleaned base: {env['name']} -> {cleaned}")
                
                new_name = manager.generate_new_name(
                    env['name'], 
                    env['python_version'], 
                    env['r_version'],
                    existing_names,
                    None  # No YAML file for basic test
                )
                print(f"  -> Would rename to: {new_name}")
                
                # Check for version detection
                if manager._has_python_version(env['name'].lower()):
                    print(f"  ✓ Already has Python version pattern")
                if manager._has_r_version(env['name'].lower()):
                    print(f"  ✓ Already has R version pattern")
                print()
        
        print("✓ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_functionality()
