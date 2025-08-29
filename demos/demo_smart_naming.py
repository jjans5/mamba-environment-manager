#!/usr/bin/env python3
"""
Smart Naming for conda-pack Unpacking Demo

This script demonstrates the enhanced unpacking functionality with smart naming.
"""

import os
import re
from utils.environment_cloner import EnvironmentCloner

def demonstrate_smart_naming():
    print("=== Smart Naming for conda-pack Unpacking ===\n")
    
    cloner = EnvironmentCloner()
    
    # Test archive
    archive_path = './cloned_environments/research_env_3.10_yaml.tar.gz'
    
    print("1. Enhanced Unpacking Features:")
    print("   ✓ Auto-generated names with version suffixes")
    print("   ✓ Custom environment names")
    print("   ✓ Same naming logic as YAML export/import")
    print("   ✓ Smart version detection from archive names")
    print("   ✓ Proper conda environments directory installation")
    print()
    
    if os.path.exists(archive_path):
        basename = os.path.splitext(os.path.splitext(os.path.basename(archive_path))[0])[0]
        
        print("2. Archive Analysis:")
        print(f"   Archive: {archive_path}")
        print(f"   Basename: {basename}")
        
        # Simulate version detection
        env_info = {'name': basename, 'python_version': None, 'r_version': None}
        
        # Version detection logic
        if '_py' in basename:
            py_match = re.search(r'_py(\d+)', basename)
            if py_match:
                py_digits = py_match.group(1)
                if len(py_digits) >= 3:
                    env_info['python_version'] = f"{py_digits[0]}.{py_digits[1:]}"
        
        if '_r' in basename:
            r_match = re.search(r'_r(\d+)', basename)
            if r_match:
                env_info['r_version'] = r_match.group(1)
        
        print(f"   Detected Python: {env_info['python_version'] or 'None'}")
        print(f"   Detected R: {env_info['r_version'] or 'None'}")
        print()
        
        print("3. Naming Options:")
        
        # Auto naming
        auto_name = cloner._generate_new_name(basename, "auto")
        print(f"   Auto:   '{basename}' -> '{auto_name}'")
        
        # Custom naming
        custom_name = cloner._generate_new_name(basename, "my_analysis_env")
        print(f"   Custom: 'my_analysis_env' -> '{custom_name}'")
        
        # Archive basename
        basename_name = cloner._generate_new_name(basename, basename)
        print(f"   Original: '{basename}' -> '{basename_name}'")
        print()
        
        print("4. CLI Usage Examples:")
        print(f"   # Auto-generate name with version suffixes:")
        print(f"   python utils/environment_cloner.py unpack {archive_path}")
        print(f"   python utils/environment_cloner.py unpack {archive_path} auto")
        print()
        print(f"   # Use custom name:")
        print(f"   python utils/environment_cloner.py unpack {archive_path} my_analysis_env")
        print()
        print(f"   # Use original archive name:")
        print(f"   python utils/environment_cloner.py unpack {archive_path} {basename}")
        print()
        
        print("5. Interactive Main Menu:")
        print("   python environment_manager.py")
        print("   -> Select option 3: [UNPACK]")
        print("   -> Choose from 3 naming options:")
        print("      1. Auto-generate with version suffixes (recommended)")
        print("      2. Use archive name")
        print("      3. Enter custom name")
        print()
        
        print("6. HPC Installation Example:")
        envs_dir = cloner._get_conda_envs_directory()
        print(f"   Current envs directory: {envs_dir}")
        print(f"   On HPC would be: /scratch/username/miniforge3/envs/")
        print(f"   Final environment: <envs_dir>/{auto_name}/")
        print(f"   Activation: conda activate {auto_name}")
        print()
        
        print("7. Complete Integration:")
        print("   ✓ Same smart naming as YAML export/import")
        print("   ✓ Version suffix generation")
        print("   ✓ Proper conda environments structure")
        print("   ✓ HPC-compatible paths") 
        print("   ✓ Automatic conda-unpack execution")
        print("   ✓ Ready-to-use environments")
        
    else:
        print("2. No test archive found.")
        print("   Create one with: conda-pack cloning method")
        print()
        print("3. Usage Examples (general):")
        print("   python utils/environment_cloner.py unpack <archive.tar.gz>")
        print("   python utils/environment_cloner.py unpack <archive.tar.gz> auto")
        print("   python utils/environment_cloner.py unpack <archive.tar.gz> custom_name")

if __name__ == "__main__":
    demonstrate_smart_naming()
