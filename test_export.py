#!/usr/bin/env python3
"""
Test the export functionality
"""

from environment_manager import EnvironmentManager
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)

def main():
    print("=== Testing Export Functionality ===\n")
    
    manager = EnvironmentManager()
    
    # Try to export a simple environment
    test_env = "cellxgene"  # This should exist based on conda env list
    
    print(f"Testing export of environment: {test_env}")
    result = manager.export_environment(test_env)
    
    if result:
        print(f"✅ Export successful: {result}")
        # Check if file actually exists and has content
        if result.exists() and result.stat().st_size > 0:
            print(f"✅ File exists and has content ({result.stat().st_size} bytes)")
        else:
            print("❌ File is missing or empty")
    else:
        print("❌ Export failed")

if __name__ == "__main__":
    main()
