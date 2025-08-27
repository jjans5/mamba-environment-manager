#!/usr/bin/env python3
"""
Test script for empty environment detection
"""

import sys
import tempfile
import shutil
from pathlib import Path
from environment_manager import EnvironmentManager

def test_empty_environment_detection():
    """Test that empty environments are properly detected and handled"""
    
    print("Testing empty environment detection...")
    
    # Create a manager instance
    manager = EnvironmentManager(use_mamba=True)
    
    # Create a test environment with no packages
    test_env = "test_empty_env"
    
    print(f"Creating empty test environment: {test_env}")
    try:
        # Create an empty environment (just python)
        result = manager._run_command([
            manager.cmd_base, "create", "-n", test_env, "-y"
        ], check=False)
        
        if result.returncode != 0:
            print(f"Failed to create test environment: {result.stderr}")
            return False
        
        print(f"✓ Created empty environment: {test_env}")
        
        # Test export
        print("Testing export of empty environment...")
        export_result = manager.export_environment(test_env)
        
        if export_result == "EMPTY":
            print("✓ Empty environment correctly detected!")
            
            # Test the full process_environment workflow
            print("Testing full process workflow...")
            env_info = {
                'name': test_env,
                'python_version': None,
                'r_version': None,
                'path': f"/some/path/{test_env}"
            }
            
            all_envs = [env_info]
            result = manager.process_environment(env_info, all_envs)
            
            if result:
                print("✓ Empty environment was successfully processed (removed)")
                
                # Verify environment was removed
                envs = manager.list_environments()
                if not any(env['name'] == test_env for env in envs):
                    print("✓ Empty environment was successfully removed")
                    return True
                else:
                    print("✗ Environment still exists after processing")
                    return False
            else:
                print("✗ Processing failed")
                return False
        else:
            print(f"✗ Expected 'EMPTY', got: {export_result}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        # Cleanup: try to remove test environment if it still exists
        try:
            manager._run_command([
                manager.cmd_base, "env", "remove", "-n", test_env, "-y"
            ], check=False)
        except:
            pass

def test_yaml_empty_detection():
    """Test the _is_environment_empty method with sample YAML data"""
    
    print("\nTesting YAML empty detection logic...")
    
    manager = EnvironmentManager(use_mamba=True)
    
    # Test case 1: Completely empty dependencies
    empty_yaml1 = {
        'name': 'test_env',
        'channels': [],
        'dependencies': []
    }
    
    if manager._is_environment_empty(empty_yaml1):
        print("✓ Empty dependencies list correctly detected")
    else:
        print("✗ Failed to detect empty dependencies list")
        return False
    
    # Test case 2: Only base packages
    empty_yaml2 = {
        'name': 'test_env',
        'channels': ['defaults'],
        'dependencies': [
            'python=3.9.0',
            '_libgcc_mutex=0.1',
            'libgcc-ng=11.2.0'
        ]
    }
    
    if manager._is_environment_empty(empty_yaml2):
        print("✓ Base-packages-only environment correctly detected as empty")
    else:
        print("✗ Failed to detect base-packages-only environment as empty")
        return False
    
    # Test case 3: Has meaningful packages
    non_empty_yaml = {
        'name': 'test_env',
        'channels': ['defaults'],
        'dependencies': [
            'python=3.9.0',
            'numpy=1.21.0',
            'pandas=1.3.0'
        ]
    }
    
    if not manager._is_environment_empty(non_empty_yaml):
        print("✓ Non-empty environment correctly detected as non-empty")
    else:
        print("✗ Non-empty environment incorrectly detected as empty")
        return False
    
    # Test case 4: Has pip packages
    pip_yaml = {
        'name': 'test_env',
        'channels': ['defaults'],
        'dependencies': [
            'python=3.9.0',
            {'pip': ['requests==2.25.1', 'flask==2.0.1']}
        ]
    }
    
    if not manager._is_environment_empty(pip_yaml):
        print("✓ Environment with pip packages correctly detected as non-empty")
    else:
        print("✗ Environment with pip packages incorrectly detected as empty")
        return False
    
    print("✓ All YAML empty detection tests passed!")
    return True

def main():
    """Run all tests"""
    
    print("🧪 Testing empty environment handling...\n")
    
    # Test YAML detection logic
    if not test_yaml_empty_detection():
        print("\n❌ YAML detection tests failed!")
        return False
    
    # Test actual environment handling
    if not test_empty_environment_detection():
        print("\n❌ Environment processing tests failed!")
        return False
    
    print("\n✅ All empty environment tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
