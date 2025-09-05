#!/usr/bin/env python3
"""
Test script for HPC conda/mamba detection
"""

import sys
import os

# Add the current directory to the path to import our module
sys.path.insert(0, '.')

try:
    from environment_manager import EnvironmentManager
    
    print("Testing environment manager initialization...")
    manager = EnvironmentManager()
    print(f"✅ Successfully initialized with: {manager.cmd_base}")
    print(f"Using mamba: {manager.use_mamba}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
