#!/usr/bin/env python3
"""
Project Navigation Helper

This script helps users understand and navigate the organized project structure.
"""

import os
import sys
from pathlib import Path

def show_project_structure():
    """Display the organized project structure"""
    
    print("🗂️  Mamba Environment Manager - Project Structure")
    print("=" * 60)
    
    structure = {
        "📁 Main Files": [
            "environment_manager.py - Main application",
            "requirements.txt - Python dependencies",
            "README.md - Project documentation"
        ],
        "📁 scripts/": [
            "batch_process.py - Batch processing utility",
            "package_config.py - Package configuration",
            "yaml_analyzer.py - YAML file analysis",
            "yaml_conflict_solver.py - Conflict resolution"
        ],
        "📁 utils/": [
            "environment_cloner.py - Enhanced cloning functionality",
            "simple_log_analyzer.py - Log analysis and debugging",
            "config_template.py - Configuration templates",
            "Other utility modules..."
        ],
        "📁 tests/": [
            "test_manager.py - Main manager tests",
            "test_enhanced_cloning.py - Cloning tests",
            "test_smart_naming.py - Naming tests",
            "Many other test files..."
        ],
        "📁 demos/": [
            "demo_enhanced_cloning.py - Cloning demonstration",
            "demo_environment_deletion.py - Deletion demo",
            "demo_kernel_list_input.py - Kernel creation demo",
            "Other demo scripts..."
        ],
        "📁 documentation/": [
            "Feature summaries and guides",
            "Technical documentation",
            "Configuration guides"
        ],
        "📁 Data Directories": [
            "backup_environments/ - YAML backups and logs",
            "exported_environments/ - Exported YAML files", 
            "cloned_environments/ - Conda-pack archives",
            "logs/ - Application log files"
        ]
    }
    
    for category, items in structure.items():
        print(f"\n{category}")
        print("-" * len(category.replace("📁 ", "")))
        for item in items:
            print(f"  • {item}")

def show_quick_commands():
    """Show quick command reference"""
    
    print("\n🚀 Quick Command Reference")
    print("=" * 60)
    
    commands = [
        ("Main Application", "python environment_manager.py"),
        ("Batch Processing", "python scripts/batch_process.py"),
        ("Environment Cloning", "python utils/environment_cloner.py"),
        ("Log Analysis", "python utils/simple_log_analyzer.py"),
        ("Run Tests", "python -m pytest tests/"),
        ("Cloning Demo", "python demos/demo_enhanced_cloning.py"),
        ("Deletion Demo", "python demos/demo_environment_deletion.py"),
        ("Kernel Demo", "python demos/demo_kernel_list_input.py")
    ]
    
    for name, command in commands:
        print(f"  {name:20} : {command}")

def check_project_health():
    """Check if all important files are in place"""
    
    print("\n🔍 Project Health Check")
    print("=" * 60)
    
    important_files = [
        "environment_manager.py",
        "requirements.txt",
        "scripts/batch_process.py",
        "scripts/yaml_analyzer.py",
        "utils/environment_cloner.py",
        "utils/simple_log_analyzer.py"
    ]
    
    missing = []
    present = []
    
    for file_path in important_files:
        if os.path.exists(file_path):
            present.append(file_path)
        else:
            missing.append(file_path)
    
    print(f"✅ Present files: {len(present)}")
    for file_path in present:
        print(f"  • {file_path}")
    
    if missing:
        print(f"\n❌ Missing files: {len(missing)}")
        for file_path in missing:
            print(f"  • {file_path}")
    else:
        print("\n🎉 All important files are present!")

def main():
    """Main navigation helper"""
    
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        if option in ['structure', 'struct', 's']:
            show_project_structure()
        elif option in ['commands', 'cmd', 'c']:
            show_quick_commands()
        elif option in ['health', 'check', 'h']:
            check_project_health()
        elif option in ['all', 'a']:
            show_project_structure()
            show_quick_commands()
            check_project_health()
        else:
            print(f"Unknown option: {option}")
            print("Available options: structure, commands, health, all")
    else:
        print("🗂️  Mamba Environment Manager - Navigation Helper\n")
        print("Usage:")
        print("  python navigate.py structure  - Show project structure")
        print("  python navigate.py commands   - Show quick commands")
        print("  python navigate.py health     - Check project health")
        print("  python navigate.py all        - Show everything")

if __name__ == "__main__":
    main()
