#!/usr/bin/env python3
"""
Diagnose YAML export issues by examining actual exported files
"""

import yaml
import sys
from pathlib import Path

def diagnose_yaml_file(yaml_path):
    """Diagnose issues with a specific YAML file"""
    
    print(f"=== Diagnosing {yaml_path} ===\n")
    
    if not Path(yaml_path).exists():
        print(f"❌ File does not exist: {yaml_path}")
        return
    
    # Check file size
    file_size = Path(yaml_path).stat().st_size
    print(f"File size: {file_size} bytes")
    
    # Read raw content
    print("\n📄 Raw file content (first 20 lines):")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines[:20], 1):
            # Show line with visible whitespace
            visible_line = repr(line)
            print(f"{i:2d}: {visible_line}")
        
        print(f"\nTotal lines: {len(lines)}")
        
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        return
    
    # Try to parse with PyYAML
    print(f"\n🔍 PyYAML parsing test:")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data:
            print("✅ PyYAML parsing successful")
            print(f"Environment name: {data.get('name', 'NOT FOUND')}")
            
            channels = data.get('channels')
            print(f"Channels type: {type(channels)}")
            print(f"Channels value: {channels}")
            
            if channels:
                print("Channels details:")
                for i, channel in enumerate(channels):
                    print(f"  [{i}]: {repr(channel)} (type: {type(channel)})")
            
            dependencies = data.get('dependencies')
            print(f"Dependencies type: {type(dependencies)}")
            if dependencies:
                print(f"Dependencies count: {len(dependencies)}")
                print("First few dependencies:")
                for i, dep in enumerate(dependencies[:5]):
                    print(f"  [{i}]: {repr(dep)} (type: {type(dep)})")
        else:
            print("❌ PyYAML returned None/empty data")
            
    except yaml.YAMLError as e:
        print(f"❌ PyYAML parsing failed: {e}")
        
        # Show the problematic area
        print("\nProblematic content around error:")
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Show first 500 characters as raw string
            print(repr(content[:500]))
        except:
            pass
            
    except Exception as e:
        print(f"❌ Other error during PyYAML parsing: {e}")
    
    # Check for common YAML issues
    print(f"\n🔍 Common issue checks:")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for mixed indentation
        lines = content.split('\n')
        tab_lines = [i+1 for i, line in enumerate(lines) if '\t' in line]
        if tab_lines:
            print(f"⚠️  Found tabs in lines: {tab_lines[:5]}{'...' if len(tab_lines) > 5 else ''}")
        
        # Check for unusual characters
        non_ascii = [(i+1, repr(line)) for i, line in enumerate(lines[:10]) if not line.isascii()]
        if non_ascii:
            print(f"⚠️  Found non-ASCII characters:")
            for line_num, line_repr in non_ascii:
                print(f"    Line {line_num}: {line_repr}")
        
        # Check for null bytes
        if '\x00' in content:
            print("⚠️  Found null bytes in file")
        
        # Check channels section specifically
        channel_lines = [line for line in lines if 'channels:' in line or (line.strip().startswith('- ') and 'channels:' in lines[max(0, lines.index(line)-3):lines.index(line)])]
        if channel_lines:
            print(f"📋 Channels section lines:")
            for line in channel_lines[:5]:
                print(f"    {repr(line)}")
        
    except Exception as e:
        print(f"❌ Error during issue checking: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python diagnose_yaml.py <yaml_file_path>")
        print("\nExample:")
        print("python diagnose_yaml.py exported_environments/anaconda3_20250827_120311.yml")
        sys.exit(1)
    
    yaml_path = sys.argv[1]
    diagnose_yaml_file(yaml_path)

if __name__ == "__main__":
    main()
