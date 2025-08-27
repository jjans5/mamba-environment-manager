#!/usr/bin/env python3
"""
Debug the base environment detection logic
"""

from environment_manager import EnvironmentManager

def debug_base_environment_detection():
    """Debug why test environments are being detected as base environments"""
    
    manager = EnvironmentManager(use_mamba=False)
    
    # Get environment list to see paths
    environments = manager.list_environments()
    
    print("=== Environment Path Analysis ===")
    for env in environments:
        name = env['name']
        path = env['path']
        
        print(f"\nEnvironment: {name}")
        print(f"Path: {path}")
        
        # Debug the base environment detection logic
        import os
        parent_dir = os.path.basename(os.path.dirname(path))
        print(f"Parent directory: {parent_dir}")
        print(f"Name == parent_dir: {name == parent_dir}")
        print(f"'envs' in path: {'envs' in path}")
        print(f"Is base environment: {manager._is_base_environment(path, name)}")
        
        # Show the specific checks
        if name == 'base':
            print("  -> Detected as base: name is 'base'")
        elif name == parent_dir:
            print("  -> Detected as base: name matches parent directory")
        elif 'envs' not in path:
            print("  -> Detected as base: no 'envs' in path")
        else:
            print("  -> Not a base environment")

if __name__ == "__main__":
    debug_base_environment_detection()
