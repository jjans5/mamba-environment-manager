#!/usr/bin/env python3
"""
Test selective package version detection - only add versions for packages mentioned in environment names
"""

from pathlib import Path
import yaml
import tempfile
import os
from environment_manager import EnvironmentManager

def create_test_yaml(name, packages_dict):
    """Create a test YAML file with specific packages"""
    yaml_content = {
        'name': name,
        'channels': ['conda-forge', 'bioconda'],
        'dependencies': [
            'python=3.10.6',
        ]
    }
    
    # Add conda packages
    for pkg, version in packages_dict.items():
        if not pkg.startswith('pip:'):
            yaml_content['dependencies'].append(f'{pkg}={version}')
    
    # Add pip packages if any
    pip_packages = []
    for pkg, version in packages_dict.items():
        if pkg.startswith('pip:'):
            pip_pkg = pkg.replace('pip:', '')
            pip_packages.append(f'{pip_pkg}=={version}')
    
    if pip_packages:
        yaml_content['dependencies'].append({
            'pip': pip_packages
        })
    
    # Write to temporary file
    yaml_file = Path(f"test_{name}.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    return yaml_file

def main():
    print("=== Testing Selective Package Version Detection ===\n")
    
    manager = EnvironmentManager()
    
    test_cases = [
        {
            'name': 'scanpy_analysis',
            'packages': {'scanpy': '1.9.1', 'pandas': '1.4.4', 'numpy': '1.21.5'},
            'expected': 'Should add scanpy version (scanpy mentioned in name)'
        },
        {
            'name': 'harmony_integration',
            'packages': {'pip:harmonypy': '0.0.9', 'pandas': '1.4.4', 'scanpy': '1.8.0'},
            'expected': 'Should add harmonypy version (harmony mentioned in name), skip scanpy'
        },
        {
            'name': 'cellrank_trajectory',
            'packages': {'pip:cellrank': '1.5.1', 'scanpy': '1.9.0', 'pandas': '1.4.4'},
            'expected': 'Should add cellrank version (cellrank mentioned in name), skip scanpy'
        },
        {
            'name': 'general_analysis',
            'packages': {'scanpy': '1.9.1', 'pandas': '1.4.4', 'numpy': '1.21.5', 'matplotlib': '3.5.2'},
            'expected': 'Should NOT add any package versions (no packages mentioned in name)'
        },
        {
            'name': 'data_science',
            'packages': {'pandas': '1.4.4', 'numpy': '1.21.5', 'matplotlib': '3.5.2', 'scikit-learn': '1.1.0'},
            'expected': 'Should NOT add any package versions (no packages mentioned in name)'
        }
    ]
    
    yaml_files = []
    
    try:
        for test_case in test_cases:
            print(f"🧪 Testing: {test_case['name']}")
            print(f"   Expected: {test_case['expected']}")
            
            # Create YAML file
            yaml_file = create_test_yaml(test_case['name'], test_case['packages'])
            yaml_files.append(yaml_file)
            
            # Extract package versions
            detected = manager._extract_package_versions_from_yaml(yaml_file, test_case['name'])
            print(f"   Available packages: {test_case['packages']}")
            print(f"   Detected (relevant): {detected}")
            
            # Generate new name
            new_name = manager.generate_new_name(
                test_case['name'], 
                python_version="3.10", 
                r_version=None,
                existing_names=["existing1", "existing2"],
                yaml_file=yaml_file
            )
            print(f"   New name: {new_name}")
            
            # Validate result
            if test_case['name'] in ['scanpy_analysis', 'harmony_integration', 'cellrank_trajectory']:
                if any(pkg in new_name.lower() for pkg in ['scanpy', 'harmony', 'cellrank']) and any(c.isdigit() for c in new_name):
                    print("   ✅ Package version correctly added")
                else:
                    print("   ❌ Expected package version missing")
            else:
                if new_name == f"{test_case['name']}_py310":
                    print("   ✅ No package versions added (correct)")
                else:
                    print("   ❌ Unexpected package versions added")
            
            print()
        
        print("✅ Selective package detection test completed!")
        
    finally:
        # Clean up test files
        for yaml_file in yaml_files:
            if yaml_file.exists():
                yaml_file.unlink()

if __name__ == "__main__":
    main()
