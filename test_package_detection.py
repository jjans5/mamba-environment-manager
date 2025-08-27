#!/usr/bin/env python3
"""
Test package version detection from YAML files
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment_manager import EnvironmentManager
from pathlib import Path

def create_test_yaml():
    """Create a test YAML file with package dependencies"""
    test_yaml_content = """name: test_scanpy_env
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - python=3.10.6
  - scanpy=1.9.1
  - numpy=1.21.5
  - pandas=1.4.4
  - matplotlib=3.5.2
  - seaborn=0.11.2
  - pip=22.1.2
  - pip:
    - harmonypy==0.0.9
    - cellrank==1.5.1
    - scvelo==0.2.5
"""
    
    test_yaml_path = Path("test_environment.yml")
    with open(test_yaml_path, 'w') as f:
        f.write(test_yaml_content)
    
    return test_yaml_path

def test_package_detection():
    """Test package version detection"""
    print("=== Testing Package Version Detection ===\n")
    
    manager = EnvironmentManager()
    
    # Create test YAML file
    yaml_file = create_test_yaml()
    
    try:
        # Test different environment names with the same YAML
        test_cases = [
            {'name': 'scanpy_analysis', 'python_version': '3.10', 'r_version': None},
            {'name': 'harmony_integration', 'python_version': '3.10', 'r_version': None},
            {'name': 'cellrank_trajectory', 'python_version': '3.10', 'r_version': None},
            {'name': 'general_analysis', 'python_version': '3.10', 'r_version': None},
        ]
        
        for test_case in test_cases:
            print(f"Environment: {test_case['name']}")
            
            # Extract package versions
            package_versions = manager._extract_package_versions_from_yaml(yaml_file, test_case['name'])
            print(f"Detected packages: {package_versions}")
            
            # Generate new name with package versions
            new_name = manager.generate_new_name(
                test_case['name'],
                test_case['python_version'],
                test_case['r_version'],
                [],
                yaml_file
            )
            
            print(f"New name: {new_name}")
            print()
        
        print("✓ Package detection test completed!")
        
    finally:
        # Clean up test file
        if yaml_file.exists():
            yaml_file.unlink()

if __name__ == "__main__":
    test_package_detection()
