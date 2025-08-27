#!/usr/bin/env python3
"""
Test pip package detection with the pycistopic example
"""

from environment_manager import EnvironmentManager
import yaml
from pathlib import Path

def test_pip_package_detection():
    print("=== Testing Pip Package Detection ===\n")
    
    # Create the exact YAML structure from your example
    yaml_content = {
        'name': 'pycistopic',
        'channels': ['conda-forge'],
        'dependencies': [
            '_libgcc_mutex=0.1=conda_forge',
            'python=3.11.0=he550d4f_1_cpython',
            'pip=24.0=pyhd8ed1ab_0',
            {
                'pip': [
                    'pycisTopic==2.0a0'
                ]
            }
        ]
    }
    
    yaml_file = Path("test_pycistopic.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    print("Created YAML file:")
    with open(yaml_file, 'r') as f:
        print(f.read())
    
    manager = EnvironmentManager()
    
    # Test with the environment name
    test_name = 'pycistopic'
    print(f"Testing with name: '{test_name}'")
    
    # Debug the package detection step by step
    print("\n🔍 Debug package detection:")
    
    env_name_lower = test_name.lower()
    print(f"Environment name (lower): '{env_name_lower}'")
    
    # Check package mappings
    package_mappings = {
        'cistopic': ['pycistopic', 'cistopic'],
    }
    
    relevant_packages = set()
    for key, packages in package_mappings.items():
        if key in env_name_lower:
            print(f"Found key '{key}' in name, adding packages: {packages}")
            relevant_packages.update(packages)
    
    print(f"Relevant packages from mappings: {relevant_packages}")
    
    # Check pip dependencies parsing
    dependencies = yaml_content['dependencies']
    for dep in dependencies:
        if isinstance(dep, dict) and 'pip' in dep:
            pip_deps = dep['pip']
            print(f"Found pip dependencies: {pip_deps}")
            
            for pip_dep in pip_deps:
                print(f"Processing pip dependency: '{pip_dep}'")
                
                # Test the current regex
                import re
                match = re.match(r'([^=><]+)[=><]+([0-9.]+)', pip_dep)
                print(f"Current regex match: {match}")
                if match:
                    pkg_name, version = match.groups()
                    print(f"  -> Package: '{pkg_name}', Version: '{version}'")
                else:
                    print("  -> No match with current regex")
                
                # Test a better regex
                better_match = re.match(r'([^=><]+)[=><]+(.+)', pip_dep)
                print(f"Better regex match: {better_match}")
                if better_match:
                    pkg_name, version = better_match.groups()
                    print(f"  -> Package: '{pkg_name.strip()}', Version: '{version.strip()}'")
                
                # Test case-insensitive matching
                pkg_name = re.split(r'[=><]', pip_dep)[0].strip()
                print(f"Package name extracted: '{pkg_name}'")
                print(f"Package name (lower): '{pkg_name.lower()}'")
                print(f"Relevant packages (lower): {[p.lower() for p in relevant_packages]}")
                print(f"Match found: {pkg_name.lower() in [p.lower() for p in relevant_packages]}")
    
    # Test the actual extraction function
    print(f"\n🧪 Testing actual extraction function:")
    detected = manager._extract_package_versions_from_yaml(yaml_file, test_name)
    print(f"Detected packages: {detected}")
    
    # Test full naming
    final_name = manager.generate_new_name(
        test_name,
        python_version="3.11",
        r_version=None,
        existing_names=[],
        yaml_file=yaml_file
    )
    print(f"Final name: {final_name}")
    
    # Clean up
    yaml_file.unlink()

if __name__ == "__main__":
    test_pip_package_detection()
