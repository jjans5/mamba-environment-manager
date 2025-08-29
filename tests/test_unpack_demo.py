#!/usr/bin/env python3
"""
Test script to demonstrate the new conda-pack unpacking functionality.
"""

import os
import sys
import tempfile
from utils.environment_cloner import EnvironmentCloner

def demo_unpack_functionality():
    """Demonstrate the new unpacking functionality."""
    print("=== conda-pack Unpacking Demo ===\n")
    
    cloner = EnvironmentCloner()
    
    # 1. Show available commands
    print("1. New CLI Commands Available:")
    print("   python utils/environment_cloner.py clone <env_name>     # Clone environment")
    print("   python utils/environment_cloner.py unpack <archive>     # Unpack archive")
    print("   python utils/environment_cloner.py list                 # List archives")
    print()
    
    # 2. List any existing archives
    print("2. Checking for existing archives...")
    archives = cloner.list_archives()
    print()
    
    # 3. Check different directories
    search_dirs = ["./cloned_environments", "./exported_environments", ".", "./backup_environments"]
    print("3. Searching in common directories:")
    for directory in search_dirs:
        if os.path.exists(directory):
            tar_files = [f for f in os.listdir(directory) if f.endswith('.tar.gz')]
            if tar_files:
                print(f"   {directory}: {len(tar_files)} .tar.gz files found")
                for f in tar_files[:3]:  # Show first 3
                    print(f"     - {f}")
                if len(tar_files) > 3:
                    print(f"     ... and {len(tar_files) - 3} more")
            else:
                print(f"   {directory}: No .tar.gz files")
        else:
            print(f"   {directory}: Directory not found")
    print()
    
    # 4. Show what the new functionality does
    print("4. New Functionality Added:")
    print("   ✓ conda-pack cloning now asks if you want to unpack immediately")
    print("   ✓ Archives are automatically unpacked to conda environments directory")
    print("   ✓ conda-unpack is run automatically to finalize the environment")
    print("   ✓ New menu option [3. UNPACK] in main environment manager")
    print("   ✓ CLI commands for managing archives separately")
    print()
    
    # 5. Show the process
    print("5. conda-pack Process Now:")
    print("   Step 1: Pack environment → creates .tar.gz archive")
    print("   Step 2: Ask user if they want to unpack now (NEW)")
    print("   Step 3: If yes, unpack to conda environments directory (NEW)")
    print("   Step 4: Run conda-unpack to finalize environment (NEW)")
    print("   Step 5: Environment ready for 'conda activate <name>' (NEW)")
    print()
    
    # 6. Integration with main tool
    print("6. Integration with Main Tool:")
    print("   - Menu option 3: [UNPACK] Unpack conda-pack archive")
    print("   - Searches common directories for .tar.gz files")
    print("   - Interactive selection and unpacking")
    print("   - Full error handling and logging")
    print()
    
    print("Demo complete! Your existing archive can now be unpacked with:")
    print("python utils/environment_cloner.py unpack ./cloned_environments/py_jjans_3.10_yaml.tar.gz")
    print("Or use the main menu: python environment_manager.py → option 3")

if __name__ == "__main__":
    demo_unpack_functionality()
