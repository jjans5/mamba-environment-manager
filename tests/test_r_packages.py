#!/usr/bin/env python3
"""
Test R package detection in environments with R packages
"""

from environment_manager import EnvironmentManager
import yaml
from pathlib import Path
import tempfile

def create_r_environment_yaml(name, packages_dict):
    """Create a test YAML file with R packages in conda format"""
    yaml_content = {
        'name': name,
        'channels': ['conda-forge', 'bioconda', 'r'],
        'dependencies': [
            'python=3.11.0',
            'r-base=4.2.0'
        ]
    }
    
    # Add R packages (conda format uses r-packagename)
    for pkg, version in packages_dict.items():
        if pkg.startswith('r-'):
            yaml_content['dependencies'].append(f'{pkg}={version}')
        else:
            yaml_content['dependencies'].append(f'r-{pkg}={version}')
    
    # Write to temporary file
    yaml_file = Path(f"test_{name}.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    return yaml_file

def main():
    print("=== Testing R Package Detection ===\n")
    
    manager = EnvironmentManager()
    
    # Test cases for R environments
    test_cases = [
        {
            'name': 'R_jjans_4.2_seurat',
            'cleaned_name': 'r_jjans_seurat',
            'packages': {'seurat': '4.3.0', 'dplyr': '1.0.10', 'ggplot2': '3.4.0'},
            'expected': 'Should detect seurat version and add seurat430'
        },
        {
            'name': 'R_jjans_4.2_cistopic',
            'cleaned_name': 'r_jjans_cistopic', 
            'packages': {'r-cistopic': '2.1.0', 'r-genomicranges': '1.48.0'},
            'expected': 'Should detect cistopic version and add cistopic210'
        },
        {
            'name': 'some_other_r_env',
            'cleaned_name': 'some_other_r_env',
            'packages': {'seurat': '4.3.0', 'dplyr': '1.0.10'},
            'expected': 'Should NOT detect seurat (not mentioned in name)'
        }
    ]
    
    yaml_files = []
    
    try:
        for test_case in test_cases:
            print(f"🧪 Testing: {test_case['name']}")
            print(f"   Cleaned: {test_case['cleaned_name']}")
            print(f"   Expected: {test_case['expected']}")
            
            # Create YAML file
            yaml_file = create_r_environment_yaml(test_case['name'], test_case['packages'])
            yaml_files.append(yaml_file)
            
            print(f"   Available R packages: {test_case['packages']}")
            
            # Extract package versions using the cleaned name (what would actually be passed)
            detected = manager._extract_package_versions_from_yaml(yaml_file, test_case['cleaned_name'])
            print(f"   Detected (relevant): {detected}")
            
            # Test the add package versions function
            base_name = test_case['cleaned_name']
            name_with_packages = manager._add_package_versions_to_name(base_name, detected)
            print(f"   With packages: {name_with_packages}")
            
            # Show what the final name would be
            final_name = manager.generate_new_name(
                test_case['name'], 
                python_version="3.11", 
                r_version="4.2",
                existing_names=[],
                yaml_file=yaml_file
            )
            print(f"   Final name: {final_name}")
            
            # Validate result
            if 'seurat' in test_case['cleaned_name'] or 'cistopic' in test_case['cleaned_name']:
                if any(pkg in final_name.lower() for pkg in ['seurat', 'cistopic']) and any(c.isdigit() for c in final_name):
                    print("   ✅ Package version correctly added")
                else:
                    print("   ❌ Expected package version missing")
            else:
                if final_name == f"{test_case['cleaned_name']}_py311_r42":
                    print("   ✅ No package versions added (correct)")
                else:
                    print("   ❌ Unexpected package versions added")
            
            print()
        
        print("✅ R package detection test completed!")
        
    finally:
        # Clean up test files
        for yaml_file in yaml_files:
            if yaml_file.exists():
                yaml_file.unlink()

if __name__ == "__main__":
    main()
