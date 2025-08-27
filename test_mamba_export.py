#!/usr/bin/env python3
"""
Test mamba-style export (stdout capture) to see if that causes YAML corruption
"""

import subprocess
from pathlib import Path
import yaml

def test_mamba_style_export():
    print("=== Testing Mamba-style Export (stdout capture) ===\n")
    
    # Simulate what the mamba export path does
    test_env = "cellxgene"
    export_file = Path("test_mamba_export.yml")
    
    print(f"Testing mamba-style export for environment: {test_env}")
    
    try:
        # Use conda env export but capture stdout (like mamba path does)
        cmd = ["conda", "env", "export", "-n", test_env]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✅ Command succeeded, stdout has {len(result.stdout)} characters")
            
            # Write to file manually (like mamba path does)
            with open(export_file, 'w') as f:
                f.write(result.stdout)
            
            print(f"✅ Written to file: {export_file}")
            print(f"File size: {export_file.stat().st_size} bytes")
            
            # Validate the written file
            print("\n📄 Raw file content (first 10 lines):")
            with open(export_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10], 1):
                    print(f"{i:2d}: {repr(line)}")  # Use repr to see any hidden characters
            
            # Try to parse the YAML
            print("\n🔍 Parsing YAML...")
            try:
                with open(export_file, 'r') as f:
                    env_data = yaml.safe_load(f)
                
                if env_data:
                    print("✅ YAML parsing successful")
                    print(f"Environment name: {env_data.get('name', 'NOT FOUND')}")
                    print(f"Channels: {env_data.get('channels', 'NOT FOUND')}")
                    print(f"Dependencies type: {type(env_data.get('dependencies', 'NOT FOUND'))}")
                else:
                    print("❌ YAML parsing returned None")
                    
            except yaml.YAMLError as e:
                print(f"❌ YAML parsing failed: {e}")
                
                # Show raw content around the error
                print("\nRaw content (first 200 chars):")
                with open(export_file, 'r') as f:
                    content = f.read()
                    print(repr(content[:200]))
                    
            # Test if there are any encoding issues
            print("\n🔍 Checking for encoding issues...")
            with open(export_file, 'rb') as f:
                raw_bytes = f.read(100)
                print(f"First 100 bytes: {raw_bytes}")
                
            # Clean up
            export_file.unlink()
            print(f"\n🧹 Cleaned up {export_file}")
            
        else:
            print(f"❌ Command failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_mamba_style_export()
