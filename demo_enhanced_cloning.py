#!/usr/bin/env python3
"""
Interactive naming demo for environment cloning
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.environment_cloner import EnvironmentCloner

def demo_interactive_naming():
    """Demo the interactive naming functionality"""
    print("=== Interactive Naming Demo ===")
    print("This simulates the enhanced naming process for environment cloning.")
    
    cloner = EnvironmentCloner()
    
    # Mock environment data (simulates a real environment like py_jjans_3.7_harmony)
    mock_env = {
        'name': 'py_jjans_3.7_harmony_yaml',
        'path': '/fake/path',
        'python_version': '3.7',
        'r_version': None,
        'packages': [
            'harmonypy=0.0.9',
            'scanpy=1.8.2', 
            'pandas=1.3.3',
            'numpy=1.21.2',
            'scipy=1.7.1',
            'matplotlib=3.4.3'
        ]
    }
    
    print(f"\nSimulating clone of environment: {mock_env['name']}")
    print("This would normally show the interactive naming dialog...")
    print()
    
    # Show what the analysis would display
    key_packages = cloner._detect_key_packages(mock_env)
    
    print("[SMART NAMING] Environment analysis:")
    if mock_env.get('python_version'):
        print(f"  Python: {mock_env['python_version']}")
    if mock_env.get('r_version'):
        print(f"  R: {mock_env['r_version']}")
    if key_packages:
        print(f"  Key packages: {', '.join(key_packages)}")
    
    # Generate auto name
    auto_name = cloner._generate_new_name(mock_env, 'auto', interactive=False)
    print(f"  Auto-generated name: {auto_name}")
    print()
    
    print("Interactive options would be:")
    print("  y - Use auto-generated name")
    print("  n - Enter custom name") 
    print("  edit - Edit the auto-generated name")
    print()
    
    # Show the improvements
    print("=== Improvements Made ===")
    print("✅ Removes '_yaml' suffix automatically")
    print("✅ Detects Python 3.7 and adds 'py37' suffix") 
    print("✅ Detects harmonypy package and adds 'harmony' indicator")
    print("✅ Detects scanpy package and adds 'scanpy' indicator")
    print("✅ Interactive editing allows customization")
    print("✅ No more generic '_yaml' names!")
    print()
    
    print("The new name would be:")
    print(f"  OLD: py_jjans_3.7_harmony -> py_jjans_3.7_harmony_yaml (generic)")
    print(f"  NEW: py_jjans_3.7_harmony -> {auto_name} (smart)")

if __name__ == "__main__":
    demo_interactive_naming()
