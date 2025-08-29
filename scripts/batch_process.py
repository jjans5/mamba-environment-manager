#!/usr/bin/env python3
"""
Batch processing script for environment management
Run this script to process all environments automatically
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment_manager import EnvironmentManager

def main():
    """Run batch processing of all environments"""
    try:
        manager = EnvironmentManager()
        
        print("=== Batch Environment Processing ===")
        print("This will process ALL environments automatically.")
        print("Make sure you have backups of important environments!")
        
        confirm = input("\nContinue? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Operation cancelled.")
            return
        
        environments = manager.list_environments()
        if not environments:
            print("No environments found!")
            return
        
        print(f"\nProcessing {len(environments)} environments...")
        
        successful = 0
        failed = 0
        
        for env in environments:
            if manager.process_environment(env):
                successful += 1
            else:
                failed += 1
        
        print(f"\n=== Final Summary ===")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(environments)}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
