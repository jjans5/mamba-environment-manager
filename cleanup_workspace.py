#!/usr/bin/env python3
"""
Workspace Cleanup Utility

Maintains the organized project structure by cleaning up temporary files,
organizing loose files, and ensuring directories are properly maintained.
"""

import os
import glob
import shutil
from pathlib import Path
import subprocess

def clean_python_cache():
    """Remove Python cache files and directories"""
    print("🧹 Cleaning Python cache files...")
    
    # Remove __pycache__ directories
    for cache_dir in glob.glob("**/__pycache__", recursive=True):
        shutil.rmtree(cache_dir, ignore_errors=True)
        print(f"  Removed: {cache_dir}")
    
    # Remove .pyc files
    pyc_count = 0
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        os.remove(pyc_file)
        pyc_count += 1
    
    if pyc_count > 0:
        print(f"  Removed: {pyc_count} .pyc files")

def organize_loose_files():
    """Move any loose files to appropriate directories"""
    print("📁 Organizing loose files...")
    
    # Move any demo files that might be in root
    demo_files = glob.glob("demo_*.py")
    if demo_files:
        os.makedirs("demos", exist_ok=True)
        for file in demo_files:
            shutil.move(file, f"demos/{file}")
            print(f"  Moved: {file} → demos/")
    
    # Move any test files that might be in root
    test_files = glob.glob("test_*.py")
    if test_files:
        os.makedirs("tests", exist_ok=True)
        for file in test_files:
            shutil.move(file, f"tests/{file}")
            print(f"  Moved: {file} → tests/")
    
    # Move documentation files
    doc_patterns = ["*_SUMMARY.md", "*_GUIDE.md", "*SOLUTIONS.md"]
    os.makedirs("documentation", exist_ok=True)
    for pattern in doc_patterns:
        doc_files = glob.glob(pattern)
        for file in doc_files:
            if file != "README.md":  # Keep main README in root
                shutil.move(file, f"documentation/{file}")
                print(f"  Moved: {file} → documentation/")
    
    # Move log files
    log_files = glob.glob("*.log")
    if log_files:
        os.makedirs("logs", exist_ok=True)
        for file in log_files:
            shutil.move(file, f"logs/{file}")
            print(f"  Moved: {file} → logs/")

def ensure_directories():
    """Ensure all required directories exist"""
    print("📂 Ensuring directory structure...")
    
    required_dirs = [
        "scripts",
        "utils", 
        "tests",
        "demos",
        "documentation",
        "logs",
        "backup_environments",
        "exported_environments", 
        "cloned_environments",
        "docs"
    ]
    
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        if not os.listdir(dir_name):
            # Create a .gitkeep file for empty directories
            with open(f"{dir_name}/.gitkeep", "w") as f:
                f.write("# This file ensures the directory is tracked by git\n")

def clean_temporary_files():
    """Remove temporary and backup files"""
    print("🗑️  Cleaning temporary files...")
    
    temp_patterns = [
        "*.tmp",
        "*.bak", 
        "*.backup",
        "*~",
        "*.swp",
        "*.swo",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    removed_count = 0
    for pattern in temp_patterns:
        for file in glob.glob(pattern, recursive=True):
            os.remove(file)
            removed_count += 1
            print(f"  Removed: {file}")
    
    if removed_count == 0:
        print("  No temporary files found")

def update_gitignore():
    """Ensure .gitignore is comprehensive"""
    print("📝 Updating .gitignore...")
    
    gitignore_additions = [
        "# Project-specific ignores",
        "logs/*.log",
        "backup_environments/*.log",
        "exported_environments/*.log",
        "*.tmp",
        "*.bak",
        "*.backup",
        ".DS_Store",
        "Thumbs.db",
        "*~",
        "*.swp",
        "*.swo"
    ]
    
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            current_content = f.read()
        
        # Only add missing entries
        new_entries = []
        for entry in gitignore_additions:
            if entry not in current_content and not entry.startswith("#"):
                new_entries.append(entry)
        
        if new_entries:
            with open(".gitignore", "a") as f:
                f.write("\n" + "\n".join(new_entries) + "\n")
            print(f"  Added {len(new_entries)} new entries to .gitignore")
        else:
            print("  .gitignore is up to date")

def show_cleanup_summary():
    """Show summary of the cleaned workspace"""
    print("\n📊 Cleanup Summary")
    print("=" * 50)
    
    # Count files in each directory
    directories = ["scripts", "utils", "tests", "demos", "documentation", "logs"]
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            file_count = len([f for f in os.listdir(dir_name) if f != ".gitkeep"])
            print(f"  {dir_name:<15} : {file_count:>3} files")
    
    # Show main directory
    main_files = [f for f in os.listdir(".") if f.endswith(".py") and os.path.isfile(f)]
    print(f"  {'main directory':<15} : {len(main_files):>3} Python files")

def main():
    """Run complete workspace cleanup"""
    print("🧹 Mamba Environment Manager - Workspace Cleanup")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run cleanup operations
    clean_python_cache()
    print()
    
    organize_loose_files()
    print()
    
    ensure_directories()
    print()
    
    clean_temporary_files()
    print()
    
    update_gitignore()
    print()
    
    show_cleanup_summary()
    print()
    
    print("✅ Workspace cleanup completed!")
    print("\nTo view the organized structure, run:")
    print("  python navigate.py structure")

if __name__ == "__main__":
    main()
