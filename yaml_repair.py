#!/usr/bin/env python3
"""
Add a YAML repair function to fix common mamba export issues
"""

def repair_mamba_yaml(yaml_content: str, env_name: str) -> str:
    """
    Attempt to repair common mamba YAML export issues
    
    Args:
        yaml_content: Raw YAML content from mamba export
        env_name: Environment name for logging
        
    Returns:
        Repaired YAML content
    """
    import re
    import yaml
    
    # Common fixes for mamba YAML issues
    repaired = yaml_content
    
    # Fix 1: Ensure proper YAML structure
    lines = repaired.split('\n')
    
    # Fix 2: Handle malformed channels section
    # Sometimes mamba outputs channels in wrong format
    for i, line in enumerate(lines):
        if line.strip() == 'channels:':
            # Check next line for proper format
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line doesn't start with '  -' or is empty, fix it
                if next_line.strip() and not next_line.strip().startswith('-'):
                    # Assume it's a single channel without proper list format
                    channel_name = next_line.strip()
                    lines[i + 1] = f"  - {channel_name}"
    
    # Fix 3: Handle malformed dependencies
    in_dependencies = False
    for i, line in enumerate(lines):
        if line.strip() == 'dependencies:':
            in_dependencies = True
            continue
        elif line.strip().endswith(':') and in_dependencies:
            in_dependencies = False
        elif in_dependencies and line.strip() and not line.strip().startswith('-') and not line.strip().startswith('  -'):
            # Fix dependency line that's missing the dash
            if '=' in line.strip():  # Looks like a package spec
                lines[i] = f"  - {line.strip()}"
    
    repaired = '\n'.join(lines)
    
    # Fix 4: Remove any null bytes or other problematic characters
    repaired = repaired.replace('\x00', '')
    
    # Fix 5: Ensure UTF-8 encoding
    repaired = repaired.encode('utf-8', errors='ignore').decode('utf-8')
    
    return repaired

# This would be added to the environment_manager.py file
print("This is the repair function that would be added to environment_manager.py")
