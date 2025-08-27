#!/usr/bin/env python3
"""
Debug R package detection
"""

from environment_manager import EnvironmentManager
import yaml
from pathlib import Path

def debug_yaml_parsing():
    print("=== Debugging YAML Parsing for R Packages ===\n")
    
    # Create a simple test YAML
    yaml_content = {
        'name': 'R_jjans_4.2_seurat',
        'channels': ['conda-forge', 'r'],
        'dependencies': [
            'python=3.11.0',
            'r-base=4.2.0',
            'r-seurat=4.3.0',
            'r-dplyr=1.0.10'
        ]
    }
    
    yaml_file = Path("debug_seurat.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    print("Created YAML file:")
    with open(yaml_file, 'r') as f:
        print(f.read())
    
    print("\nTesting package detection:")
    manager = EnvironmentManager()
    
    # Test with original name and cleaned name
    test_names = ['R_jjans_4.2_seurat', 'r_jjans_seurat']
    
    for test_name in test_names:
        print(f"\nTesting with name: '{test_name}'")
        detected = manager._extract_package_versions_from_yaml(yaml_file, test_name)
        print(f"Detected packages: {detected}")
        
        # Let's also debug the internal logic
        print("Debug: checking package mappings...")
        
        # Check if 'seurat' is in the name
        env_name_lower = test_name.lower()
        print(f"Environment name (lower): '{env_name_lower}'")
        print(f"'seurat' in name: {'seurat' in env_name_lower}")
        
        # Check the package mapping
        package_mappings = {
            'seurat': ['rpy2', 'seurat'],
            'cistopic': ['pycistopic', 'cistopic'],
        }
        
        relevant_packages = set()
        for key, packages in package_mappings.items():
            if key in env_name_lower:
                print(f"Found key '{key}' in name, adding packages: {packages}")
                relevant_packages.update(packages)
        
        print(f"Relevant packages from mappings: {relevant_packages}")
        
        # Check dependencies parsing
        with open(yaml_file, 'r') as f:
            env_data = yaml.safe_load(f)
        
        dependencies = env_data.get('dependencies', [])
        print(f"Dependencies from YAML: {dependencies}")
        
        # Check dependency parsing
        for dep in dependencies:
            if isinstance(dep, str):
                pkg_name = dep.split('=')[0].strip()
                print(f"Checking dependency: '{dep}' -> package name: '{pkg_name}'")
                if any(pkg in env_name_lower for pkg in [pkg_name.lower()]):
                    print(f"  -> Package '{pkg_name}' mentioned in environment name")
                else:
                    print(f"  -> Package '{pkg_name}' NOT mentioned in environment name")
    
    # Clean up
    yaml_file.unlink()

if __name__ == "__main__":
    debug_yaml_parsing()
