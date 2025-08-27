#!/usr/bin/env python3
"""
Test the smart naming functionality with real-world environment examples
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment_manager import EnvironmentManager

def test_naming_patterns():
    """Test naming patterns based on your actual environments"""
    
    # Create test environments based on your list
    test_environments = [
        # Already versioned environments
        {'name': 'py_jjans_3.10', 'python_version': '3.10', 'r_version': None},
        {'name': 'py_jjans_3.10_scanpy', 'python_version': '3.10', 'r_version': None},
        {'name': 'py_jjans_3.7_harmony', 'python_version': '3.7', 'r_version': None},
        {'name': 'R_jjans_4.2_cistopic', 'python_version': None, 'r_version': '4.2'},
        {'name': 'R_jjans_4.2_seurat', 'python_version': None, 'r_version': '4.2'},
        {'name': 'neuronchat_r405', 'python_version': '3.10', 'r_version': '4.0'},
        
        # Descriptive names without versions
        {'name': 'scenicplus', 'python_version': '3.11', 'r_version': None},
        {'name': 'cellxgene', 'python_version': '3.11', 'r_version': None},
        {'name': 'deeptools', 'python_version': '3.9', 'r_version': None},
        {'name': 'biopython', 'python_version': '3.10', 'r_version': None},
        
        # Mixed cases
        {'name': 'conda_DL', 'python_version': '3.9', 'r_version': None},
        {'name': 'cpa-env', 'python_version': '3.10', 'r_version': None},
        {'name': 'R_decon', 'python_version': None, 'r_version': '4.2'},
        {'name': 'scenicplus_dev', 'python_version': '3.11', 'r_version': None},
        {'name': 'scenicplus_v102', 'python_version': '3.11', 'r_version': None},
    ]
    
    print("=== Testing Smart Environment Naming ===\n")
    
    manager = EnvironmentManager()
    existing_names = [env['name'].lower() for env in test_environments]
    
    for env in test_environments:
        print(f"Original: {env['name']}")
        print(f"  Python: {env['python_version']}, R: {env['r_version']}")
        
        # Show what gets cleaned
        cleaned = manager._clean_existing_versions(env['name'].lower())
        if cleaned != env['name'].lower():
            print(f"  Cleaned base: {env['name']} → {cleaned}")
        
        # Check version detection
        has_py = manager._has_python_version(env['name'].lower())
        has_r = manager._has_r_version(env['name'].lower())
        if has_py:
            print(f"  ✓ Detected existing Python version pattern")
        if has_r:
            print(f"  ✓ Detected existing R version pattern")
        
        # Generate new name
        new_name = manager.generate_new_name(
            env['name'], 
            env['python_version'], 
            env['r_version'],
            existing_names
        )
        
        print(f"  New name: {new_name}")
        
        # Check for conflicts
        if new_name.endswith('_v1') or '_v' in new_name.split('_')[-1]:
            print(f"  ⚠ Conflict resolved with version suffix")
        
        print()
    
    print("=== Testing Conflict Resolution ===\n")
    
    # Test conflict resolution
    conflict_test = [
        {'name': 'test_env', 'python_version': '3.10', 'r_version': None},
        {'name': 'test_env_py310', 'python_version': '3.10', 'r_version': None},  # Would conflict
    ]
    
    existing_conflict_names = ['test_env_py310']  # Simulate existing environment
    
    for env in conflict_test:
        new_name = manager.generate_new_name(
            env['name'], 
            env['python_version'], 
            env['r_version'],
            existing_conflict_names
        )
        print(f"{env['name']} → {new_name}")
    
    print("\n✓ Smart naming test completed!")

if __name__ == "__main__":
    test_naming_patterns()
