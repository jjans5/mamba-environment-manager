#!/usr/bin/env python3
"""
Test package version detection with real YAML exports
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment_manager import EnvironmentManager
from pathlib import Path

def create_realistic_yaml_files():
    """Create realistic YAML files based on actual conda environment exports"""
    
    # Scanpy environment YAML
    scanpy_yaml = """name: scanpy_analysis
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.10.6
  - scanpy=1.9.1
  - pandas=1.4.4
  - numpy=1.21.5
  - matplotlib=3.5.2
  - seaborn=0.11.2
  - scipy=1.8.1
  - pip:
    - harmonypy==0.0.9
    - cellrank==1.5.1
"""

    # Harmony environment YAML (should not add harmonypy since harmony is in name)
    harmony_yaml = """name: harmony_integration
channels:
  - conda-forge
dependencies:
  - python=3.10.6
  - pandas=1.4.4
  - numpy=1.21.5
  - pip:
    - harmonypy==0.0.9
    - scanpy==1.9.1
    - scvelo==0.2.5
"""

    # Environment where scanpy is already in name
    scanpy_existing_yaml = """name: py_scanpy_env
channels:
  - conda-forge
dependencies:
  - python=3.9.7
  - scanpy=1.8.2
  - pandas=1.3.5
"""

    # Create temporary files
    temp_dir = Path(tempfile.mkdtemp())
    
    scanpy_file = temp_dir / "scanpy_analysis.yml"
    harmony_file = temp_dir / "harmony_integration.yml"
    existing_file = temp_dir / "py_scanpy_env.yml"
    
    scanpy_file.write_text(scanpy_yaml)
    harmony_file.write_text(harmony_yaml)
    existing_file.write_text(scanpy_existing_yaml)
    
    return {
        'scanpy_analysis': scanpy_file,
        'harmony_integration': harmony_file,
        'py_scanpy_env': existing_file,
        'temp_dir': temp_dir
    }

def test_realistic_package_detection():
    """Test package detection with realistic scenarios"""
    
    print("=== Testing Realistic Package Version Detection ===\n")
    
    manager = EnvironmentManager()
    
    # Create realistic YAML files
    yaml_files = create_realistic_yaml_files()
    
    try:
        test_cases = [
            {
                'name': 'scanpy_analysis',
                'python_version': '3.10',
                'r_version': None,
                'yaml_file': yaml_files['scanpy_analysis'],
                'expected': 'scanpy should NOT be added (already in name)'
            },
            {
                'name': 'harmony_integration', 
                'python_version': '3.10',
                'r_version': None,
                'yaml_file': yaml_files['harmony_integration'],
                'expected': 'harmonypy should NOT be added (harmony in name), scanpy might be added'
            },
            {
                'name': 'general_analysis',
                'python_version': '3.10', 
                'r_version': None,
                'yaml_file': yaml_files['scanpy_analysis'],  # Use scanpy YAML but different name
                'expected': 'scanpy should be added (not in name)'
            },
            {
                'name': 'py_scanpy_env',
                'python_version': '3.9',
                'r_version': None, 
                'yaml_file': yaml_files['py_scanpy_env'],
                'expected': 'scanpy should NOT be added (already in name)'
            }
        ]
        
        for test_case in test_cases:
            print(f"🧪 Testing: {test_case['name']}")
            print(f"   Expected: {test_case['expected']}")
            
            # Extract package versions
            package_versions = manager._extract_package_versions_from_yaml(
                test_case['yaml_file'], 
                test_case['name']
            )
            print(f"   Detected packages: {package_versions}")
            
            # Test the add package versions function
            base_name = manager._clean_existing_versions(test_case['name'].lower())
            name_with_packages = manager._add_package_versions_to_name(base_name, package_versions)
            print(f"   Base name: {test_case['name']} → {base_name}")
            print(f"   With packages: {name_with_packages}")
            
            # Generate full new name
            new_name = manager.generate_new_name(
                test_case['name'],
                test_case['python_version'],
                test_case['r_version'],
                [],
                test_case['yaml_file']
            )
            print(f"   Final name: {new_name}")
            
            # Check for duplication more accurately
            if test_case['name'].lower() in ['scanpy_analysis', 'harmony_integration', 'py_scanpy_env']:
                # Check if any package names from detected packages appear in the final name
                # but exclude cases where they were properly skipped
                name_parts = new_name.split('_')
                detected_pkg_names = list(package_versions.keys())
                
                duplication_found = False
                for pkg in detected_pkg_names:
                    # Check if package appears twice: once in base name, once as version suffix
                    pkg_in_base = any(pkg.lower() in part.lower() for part in test_case['name'].lower().split('_'))
                    pkg_in_suffix = any(pkg.lower() in part.lower() for part in name_parts if part not in test_case['name'].lower().split('_'))
                    
                    if pkg_in_base and pkg_in_suffix:
                        duplication_found = True
                        print(f"   ❌ DUPLICATION: {pkg} found in both base name and suffix")
                        break
                
                if not duplication_found:
                    print(f"   ✅ No duplication detected - package properly handled")
            
            print()
        
        print("✅ Realistic package detection test completed!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(yaml_files['temp_dir'])

if __name__ == "__main__":
    test_realistic_package_detection()
