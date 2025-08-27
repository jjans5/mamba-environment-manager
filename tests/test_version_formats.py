#!/usr/bin/env python3
"""
Test various pip package version formats
"""

from environment_manager import EnvironmentManager
import yaml
from pathlib import Path

def test_version_formats():
    print("=== Testing Various Version Formats ===\n")
    
    manager = EnvironmentManager()
    
    test_cases = [
        {
            'name': 'test_scanpy',
            'pip_packages': ['scanpy==1.9.1'],
            'expected': 'scanpy191'
        },
        {
            'name': 'test_cistopic',
            'pip_packages': ['pycisTopic==2.0a0'],
            'expected': 'pycistopic20a0'
        },
        {
            'name': 'test_beta',
            'pip_packages': ['somepackage==3.1b2'],
            'expected': 'somepackage31b2'
        },
        {
            'name': 'test_rc',
            'pip_packages': ['anotherpackage==1.5rc1'],
            'expected': 'anotherpackage15rc1'
        },
        {
            'name': 'test_dev',
            'pip_packages': ['devpackage==0.2dev'],
            'expected': 'devpackage02dev'
        },
        {
            'name': 'test_simple',
            'pip_packages': ['simple==1.0'],
            'expected': 'simple10'
        }
    ]
    
    yaml_files = []
    
    try:
        for test_case in test_cases:
            print(f"🧪 Testing: {test_case['name']}")
            print(f"   Pip packages: {test_case['pip_packages']}")
            print(f"   Expected version suffix: {test_case['expected']}")
            
            # Create YAML
            yaml_content = {
                'name': test_case['name'],
                'channels': ['conda-forge'],
                'dependencies': [
                    'python=3.11.0',
                    'pip=24.0',
                    {
                        'pip': test_case['pip_packages']
                    }
                ]
            }
            
            yaml_file = Path(f"test_{test_case['name']}.yaml")
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f, default_flow_style=False)
            
            yaml_files.append(yaml_file)
            
            # Extract packages
            detected = manager._extract_package_versions_from_yaml(yaml_file, test_case['name'])
            print(f"   Detected: {detected}")
            
            # Test version processing
            if detected:
                package_versions = manager._add_package_versions_to_name(test_case['name'], detected)
                print(f"   With versions: {package_versions}")
                
                # Check if expected suffix is in the result
                if test_case['expected'] in package_versions:
                    print(f"   ✅ Version format correct")
                else:
                    print(f"   ❌ Expected '{test_case['expected']}' not found in '{package_versions}'")
            else:
                print(f"   ❌ No packages detected")
            
            print()
        
    finally:
        # Clean up
        for yaml_file in yaml_files:
            if yaml_file.exists():
                yaml_file.unlink()

if __name__ == "__main__":
    test_version_formats()
