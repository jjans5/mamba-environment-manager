#!/usr/bin/env python3
"""
Simple Log Analyzer for Environment Manager HPC Results
"""

import os
import re
import sys

def analyze_failures(log_path="environment_manager.log"):
    """
    Simple function to analyze which environments failed and why.
    
    Args:
        log_path: Path to the log file (default: environment_manager.log)
    """
    
    print("🔍 ANALYZING ENVIRONMENT FAILURES")
    print("=" * 60)
    
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        print("💡 Make sure you're in the directory with the log file")
        return
    
    failed_envs = {}
    successful_envs = []
    
    # Parse the log file
    with open(log_path, 'r') as f:
        current_env = None
        
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Track current environment being processed
            if "Processing environment:" in line:
                match = re.search(r"Processing environment: (\w+)", line)
                if match:
                    current_env = match.group(1)
            
            # Record successes
            elif "Successfully exported" in line:
                match = re.search(r"Successfully exported (\w+)", line)
                if match:
                    env_name = match.group(1)
                    successful_envs.append(env_name)
            
            # Record failures with details
            elif any(keyword in line for keyword in ["ERROR", "Failed", "failed"]):
                # Try to extract environment name from the error line
                env_name = current_env or "Unknown"
                
                # Extract specific error type
                if "Failed to export" in line:
                    error_type = "Export failed"
                elif "Command failed" in line:
                    error_type = "Command execution failed"
                elif "Permission denied" in line:
                    error_type = "Permission denied"
                elif "No such file" in line:
                    error_type = "File not found"
                elif "timeout" in line.lower():
                    error_type = "Timeout"
                else:
                    error_type = "Unknown error"
                
                if env_name not in failed_envs:
                    failed_envs[env_name] = []
                
                failed_envs[env_name].append({
                    'error_type': error_type,
                    'line_number': line_num,
                    'error_message': line[:100] + "..." if len(line) > 100 else line
                })
    
    # Display results
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successful: {len(successful_envs)}")
    print(f"   ❌ Failed: {len(failed_envs)}")
    print()
    
    if successful_envs:
        print("✅ SUCCESSFUL ENVIRONMENTS:")
        for env in sorted(successful_envs):
            print(f"   • {env}")
        print()
    
    if failed_envs:
        print("❌ FAILED ENVIRONMENTS:")
        print("-" * 60)
        
        for env_name, errors in failed_envs.items():
            print(f"\n🔴 {env_name}")
            for error in errors:
                print(f"   └─ {error['error_type']} (line {error['line_number']})")
                print(f"      {error['error_message']}")
        
        # Summary of error types
        error_types = {}
        for errors in failed_envs.values():
            for error in errors:
                error_type = error['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        print(f"\n📈 ERROR TYPE SUMMARY:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {error_type}: {count}")
    
    print(f"\n💡 To see full error context for any environment:")
    print(f"   grep -A 5 -B 5 'ENVIRONMENT_NAME' {log_path}")
    
    return successful_envs, failed_envs

def debug_environment_failure(env_name, log_path="environment_manager.log"):
    """
    Debug specific environment failure with detailed analysis.
    
    Args:
        env_name: Name of the environment to debug
        log_path: Path to the log file
    """
    
    print(f"🔍 DEBUGGING ENVIRONMENT: {env_name}")
    print("=" * 60)
    
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        return
    
    # Find all log entries related to this environment
    related_entries = []
    context_lines = []
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check if line mentions the environment
            if env_name.lower() in line.lower():
                # Collect context (5 lines before and after)
                start_ctx = max(0, i - 5)
                end_ctx = min(len(lines), i + 6)
                
                context = {
                    'line_number': line_num,
                    'content': line.strip(),
                    'context_before': [lines[j].strip() for j in range(start_ctx, i)],
                    'context_after': [lines[j].strip() for j in range(i + 1, end_ctx)]
                }
                
                related_entries.append(context)
    
    if not related_entries:
        print(f"❌ No log entries found for environment '{env_name}'")
        print(f"💡 Check spelling or try: grep -i '{env_name}' {log_path}")
        return
    
    print(f"📊 Found {len(related_entries)} related log entries:")
    print()
    
    # Analyze each entry
    errors = []
    warnings = []
    info = []
    
    for entry in related_entries:
        content = entry['content']
        line_num = entry['line_number']
        
        if any(keyword in content for keyword in ['ERROR', 'Failed', 'failed']):
            errors.append((line_num, content))
        elif any(keyword in content for keyword in ['WARNING', 'WARN']):
            warnings.append((line_num, content))
        else:
            info.append((line_num, content))
    
    # Display errors with context
    if errors:
        print("🔴 ERRORS:")
        for line_num, content in errors:
            print(f"   Line {line_num}: {content}")
            
            # Find the full context for this error
            for entry in related_entries:
                if entry['line_number'] == line_num:
                    if entry['context_before']:
                        print("   Context before:")
                        for ctx_line in entry['context_before'][-3:]:  # Last 3 lines
                            if ctx_line.strip():
                                print(f"     {ctx_line}")
                    if entry['context_after']:
                        print("   Context after:")
                        for ctx_line in entry['context_after'][:3]:  # First 3 lines
                            if ctx_line.strip():
                                print(f"     {ctx_line}")
                    print()
                    break
    
    # Display warnings
    if warnings:
        print("🟡 WARNINGS:")
        for line_num, content in warnings:
            print(f"   Line {line_num}: {content}")
        print()
    
    # Display info messages
    if info:
        print("ℹ️  INFORMATION:")
        for line_num, content in info[:5]:  # Show first 5 info messages
            print(f"   Line {line_num}: {content}")
        if len(info) > 5:
            print(f"   ... and {len(info) - 5} more info messages")
        print()
    
    # Provide specific debugging suggestions
    print("💡 DEBUGGING SUGGESTIONS:")
    
    error_text = ' '.join([content for _, content in errors]).lower()
    
    if 'command failed' in error_text:
        print("   • Command execution failed - check environment path and permissions")
        print("   • Try running the command manually to see detailed error output")
    
    if 'does not exist' in error_text or 'not found' in error_text:
        print("   • Environment path or name issue")
        print(f"   • Verify environment exists: conda env list | grep {env_name}")
        print(f"   • Check environment path permissions")
    
    if 'yaml' in error_text or 'export' in error_text:
        print("   • YAML export/import issue")
        print(f"   • Try manual export: conda env export -n {env_name} > test_export.yml")
        print("   • Check for package conflicts or corrupted environment")
    
    if 'timeout' in error_text:
        print("   • Network or performance issue")
        print("   • Try running during off-peak hours")
        print("   • Check internet connection and conda channels")
    
    if 'permission' in error_text:
        print("   • File/directory permission issue")
        print("   • Check write permissions for output directories")
        print("   • Consider running with appropriate privileges")
    
    print(f"\n🔍 Full context search:")
    print(f"   grep -A 10 -B 10 '{env_name}' {log_path}")
    
    return related_entries

def interactive_debug():
    """Interactive debugging session."""
    print("🛠️  INTERACTIVE ENVIRONMENT DEBUGGER")
    print("=" * 50)
    
    log_path = "environment_manager.log"
    
    while True:
        env_name = input("\n🔍 Enter environment name to debug (or 'quit' to exit): ").strip()
        
        if env_name.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not env_name:
            print("❌ Please enter an environment name")
            continue
        
        debug_environment_failure(env_name, log_path)
        
        continue_debug = input("\n❓ Debug another environment? (y/N): ").strip().lower()
        if continue_debug != 'y':
            break

# Quick run function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            if len(sys.argv) > 2:
                debug_environment_failure(sys.argv[2])
            else:
                interactive_debug()
        else:
            # Assume it's an environment name to debug
            debug_environment_failure(sys.argv[1])
    else:
        analyze_failures()
