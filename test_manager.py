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
            for env in environments[:3]:  # Show first 3
                print(f"- {env['name']} (Python: {env['python_version']}, R: {env['r_version']})")
                new_name = manager.generate_new_name(
                    env['name'], 
                    env['python_version'], 
                    env['r_version']
                )
                print(f"  -> Would rename to: {new_name}")
        
        print("✓ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_functionality()
