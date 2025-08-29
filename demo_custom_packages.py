#!/usr/bin/env python3
"""
Demo: Adding Custom Packages to Configuration

This script shows how to add your own packages to the package detection system.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_custom_packages():
    print("=== Custom Package Configuration Demo ===")
    print()
    
    print("1. Current package_config.py includes common packages like:")
    print("   - harmonypy → harmony09 (for version 0.0.9)")
    print("   - scanpy → scanpy18 (for version 1.8.2)")
    print("   - pytorch → pytorch19 (for version 1.9.0)")
    print()
    
    print("2. To add your own packages, edit package_config.py:")
    print()
    
    # Show example of adding custom packages
    example_config = '''
# Add to package_config.py:

'cellranger': {
    'packages': ['cellranger', 'cell-ranger'],
    'include_version': True,
    'version_format': 'major.minor'
},

'custom_analysis': {
    'packages': ['my-analysis-tool', 'analysis-package'],
    'include_version': True,
    'version_format': 'major'
},

'workflow_tool': {
    'packages': ['nextflow', 'snakemake', 'workflow-engine'],
    'include_version': False,  # Just name, no version
    'version_format': 'major'
}
'''
    
    print(example_config)
    print()
    
    print("3. Example results with custom packages:")
    print()
    
    examples = [
        {
            'packages': ['cellranger=7.0.0', 'harmonypy=0.0.9'],
            'result': 'analysis_env_py38_cellranger70_harmony09'
        },
        {
            'packages': ['my-analysis-tool=2.1.0', 'scanpy=1.8.2'],
            'result': 'experiment_py39_custom_analysis2_scanpy18'
        },
        {
            'packages': ['nextflow=21.04.0', 'snakemake=6.8.0'],
            'result': 'workflow_env_py38_workflow_tool'
        }
    ]
    
    for example in examples:
        print(f"   Packages: {example['packages']}")
        print(f"   Result:   {example['result']}")
        print()
    
    print("4. Benefits of custom configuration:")
    print("   ✅ Environment names reflect YOUR specific tools")
    print("   ✅ Version information for packages that matter to you")
    print("   ✅ Easy to identify environments at a glance")
    print("   ✅ Consistent naming across your team/project")
    print()
    
    print("5. To test your configuration:")
    print("   python3 -c \"")
    print("   from utils.environment_cloner import EnvironmentCloner")
    print("   cloner = EnvironmentCloner()")
    print("   # Test with your packages...")
    print("   \"")

if __name__ == "__main__":
    demo_custom_packages()
