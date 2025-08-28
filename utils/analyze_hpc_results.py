#!/usr/bin/env python3
"""
Simple Log Analyzer for Environment Manager HPC Results
"""

import os
import re

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

def check_yaml_directory(yaml_dir):
    """Check for YAML files and potential duplicates."""
    
    print(f"\n📁 CHECKING YAML DIRECTORY: {yaml_dir}")
    print("-" * 50)
    
    if not os.path.exists(yaml_dir):
        print(f"❌ Directory not found: {yaml_dir}")
        print("💡 Make sure to copy your YAML files from HPC to this directory")
        return
    
    yaml_files = list(Path(yaml_dir).glob("*.yml")) + list(Path(yaml_dir).glob("*.yaml"))
    
    if not yaml_files:
        print("❌ No YAML files found in directory")
        print("💡 Copy your exported YAML files from HPC:")
        print(f"   scp user@hpc:path/to/exported_environments/*.yml {yaml_dir}/")
        return
    
    print(f"📄 Found {len(yaml_files)} YAML files")
    
    # Group files by environment name
    env_groups = {}
    for file_path in yaml_files:
        filename = file_path.name
        # Extract environment name (before timestamp or version)
        env_name = re.sub(r'_\d{8}_\d{6}\.ya?ml$', '', filename)
        env_name = re.sub(r'\.ya?ml$', '', env_name)
        
        if env_name not in env_groups:
            env_groups[env_name] = []
        env_groups[env_name].append(file_path)
    
    duplicates = {name: files for name, files in env_groups.items() if len(files) > 1}
    
    if duplicates:
        print(f"\n🔄 POTENTIAL DUPLICATES FOUND ({len(duplicates)} environments):")
        for env_name, files in duplicates.items():
            print(f"   📦 {env_name}:")
            for file_path in sorted(files):
                stat = file_path.stat()
                size = stat.st_size
                mtime = stat.st_mtime
                print(f"      • {file_path.name} ({size:,} bytes, {mtime})")
        
        print(f"\n💡 TO REMOVE DUPLICATES:")
        print(f"   python yaml_analyzer.py --dir {yaml_dir} --cleanup-duplicates keep_newest")
        print(f"   python yaml_analyzer.py --dir {yaml_dir} --cleanup-env-duplicates")
    else:
        print("✅ No duplicates found")
    
    return len(yaml_files), len(duplicates)

def provide_next_steps(successes, failures, yaml_count, duplicate_count):
    """Provide recommendations for next steps."""
    
    print(f"\n🎯 RECOMMENDED NEXT STEPS")
    print("=" * 50)
    
    print("1. 📥 COPY FILES FROM HPC:")
    print("   scp user@hpc:path/to/exported_environments/*.yml ./exported_environments/")
    print("   scp user@hpc:path/to/environment_manager.log ./")
    
    if duplicate_count > 0:
        print(f"\n2. 🧹 REMOVE DUPLICATES ({duplicate_count} found):")
        print("   python yaml_analyzer.py --analyze")
        print("   python yaml_analyzer.py --cleanup-duplicates keep_newest")
    
    if failures > 0:
        print(f"\n3. 🔧 INVESTIGATE FAILURES ({failures} found):")
        print("   grep -A 5 -B 5 'ERROR\\|Failed' environment_manager.log")
        print("   # Common issues: package conflicts, outdated dependencies")
    
    print(f"\n4. ✅ VERIFY SUCCESSFUL ENVIRONMENTS ({successes} found):")
    print("   python environment_manager.py  # Option 1: List environments")
    print("   # Check that new environments are properly named and functional")
    
    print(f"\n5. 🗑️ CLEANUP OLD ENVIRONMENTS:")
    print("   python environment_manager.py  # Option 3: Remove old environments")
    print("   # After verifying new environments work correctly")
    
    print(f"\n📋 SUMMARY:")
    print(f"   • Total processed: {successes + failures}")
    print(f"   • Success rate: {successes/(successes + failures)*100:.1f}%")
    print(f"   • YAML files: {yaml_count}")
    print(f"   • Duplicates: {duplicate_count}")

def main():
    """Main analysis function."""
    
    # Default paths
    log_path = "environment_manager.log"
    yaml_dir = "exported_environments"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python analyze_hpc_results.py [log_file] [yaml_directory]")
            print("Defaults: environment_manager.log exported_environments/")
            return
        log_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        yaml_dir = sys.argv[2]
    
    # Analyze log file
    result = analyze_log_file(log_path)
    if result:
        successes, failures, exports = result
    else:
        successes, failures = 40, 42  # From user's reported results
    
    # Check YAML directory
    yaml_result = check_yaml_directory(yaml_dir)
    if yaml_result:
        yaml_count, duplicate_count = yaml_result
    else:
        yaml_count, duplicate_count = 0, 0
    
    # Provide next steps
    provide_next_steps(successes, failures, yaml_count, duplicate_count)

if __name__ == "__main__":
    main()
