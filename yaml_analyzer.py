#!/usr/bin/env python3
"""
YAML Analysis Module

Provides functions for analyzing, comparing, and managing exported YAML environment files.
This module is independent of the main environment manager and focuses specifically on 
YAML file operations.
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from datetime import datetime
import logging
from colorama import Fore, Style

class YAMLAnalyzer:
    """Analyzes and manages exported YAML environment files"""
    
    def __init__(self, yaml_dir: Optional[Path] = None):
        """
        Initialize the YAML analyzer
        
        Args:
            yaml_dir: Directory containing YAML files (default: exported_environments)
        """
        self.yaml_dir = yaml_dir or Path("exported_environments")
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for YAML operations"""
        logger = logging.getLogger("yaml_analyzer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def analyze_yaml_files(self) -> Dict:
        """
        Analyze all YAML files in the directory
        
        Returns:
            Dict containing analysis results:
            - total_files: Number of YAML files
            - duplicates: Groups of duplicate files
            - by_environment: Files grouped by environment name
            - file_info: Detailed info for each file
        """
        yaml_files = self._get_yaml_files()
        
        if not yaml_files:
            return {
                'total_files': 0,
                'duplicates': [],
                'by_environment': {},
                'file_info': {}
            }
        
        print(f"\n🔍 Analyzing {len(yaml_files)} YAML files...")
        
        file_info = {}
        content_hashes = {}
        env_groups = {}
        
        for yaml_file in yaml_files:
            info = self._analyze_single_file(yaml_file)
            file_info[str(yaml_file)] = info
            
            # Group by content hash for duplicate detection
            content_hash = info['content_hash']
            if content_hash not in content_hashes:
                content_hashes[content_hash] = []
            content_hashes[content_hash].append(yaml_file)
            
            # Group by environment name
            env_name = info['environment_name']
            if env_name not in env_groups:
                env_groups[env_name] = []
            env_groups[env_name].append(yaml_file)
        
        # Find duplicates (same content)
        duplicates = [files for files in content_hashes.values() if len(files) > 1]
        
        return {
            'total_files': len(yaml_files),
            'duplicates': duplicates,
            'by_environment': env_groups,
            'file_info': file_info
        }
    
    def _get_yaml_files(self) -> List[Path]:
        """Get all YAML files in the directory"""
        if not self.yaml_dir.exists():
            return []
        
        return list(self.yaml_dir.glob("*.yml")) + list(self.yaml_dir.glob("*.yaml"))
    
    def _analyze_single_file(self, yaml_file: Path) -> Dict:
        """
        Analyze a single YAML file
        
        Args:
            yaml_file: Path to the YAML file
            
        Returns:
            Dict with file analysis information
        """
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
                yaml_data = yaml.safe_load(content)
            
            # Calculate content hash (ignoring name field for duplicate detection)
            yaml_for_hash = yaml_data.copy() if yaml_data else {}
            if 'name' in yaml_for_hash:
                yaml_for_hash.pop('name')  # Remove name for content comparison
            
            content_hash = hashlib.md5(str(sorted(yaml_for_hash.items())).encode()).hexdigest()
            
            return {
                'file_path': yaml_file,
                'file_name': yaml_file.name,
                'file_size': yaml_file.stat().st_size,
                'modified_time': datetime.fromtimestamp(yaml_file.stat().st_mtime),
                'environment_name': yaml_data.get('name', 'unknown') if yaml_data else 'unknown',
                'channels': yaml_data.get('channels', []) if yaml_data else [],
                'dependencies_count': len(yaml_data.get('dependencies', [])) if yaml_data else 0,
                'content_hash': content_hash,
                'is_valid': yaml_data is not None,
                'raw_content': content
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {yaml_file}: {e}")
            return {
                'file_path': yaml_file,
                'file_name': yaml_file.name,
                'file_size': 0,
                'modified_time': datetime.fromtimestamp(yaml_file.stat().st_mtime),
                'environment_name': 'error',
                'channels': [],
                'dependencies_count': 0,
                'content_hash': 'error',
                'is_valid': False,
                'error': str(e)
            }
    
    def print_analysis_report(self, analysis: Dict):
        """Print a comprehensive analysis report"""
        print(f"\n{Fore.CYAN}📊 YAML Analysis Report{Style.RESET_ALL}")
        print("=" * 50)
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"   Total YAML files: {analysis['total_files']}")
        print(f"   Unique environments: {len(analysis['by_environment'])}")
        print(f"   Duplicate groups: {len(analysis['duplicates'])}")
        
        # Environment groups
        if analysis['by_environment']:
            print(f"\n📁 Files by Environment:")
            for env_name, files in analysis['by_environment'].items():
                if len(files) > 1:
                    print(f"   {env_name}: {len(files)} files ⚠️  Multiple exports")
                    for file in files:
                        info = analysis['file_info'][str(file)]
                        print(f"      - {file.name} ({info['modified_time'].strftime('%Y-%m-%d %H:%M')})")
                else:
                    print(f"   {env_name}: 1 file")
        
        # Duplicates
        if analysis['duplicates']:
            print(f"\n⚠️  {Fore.YELLOW}Duplicate Content Detected:{Style.RESET_ALL}")
            for i, duplicate_group in enumerate(analysis['duplicates'], 1):
                print(f"\n   Group {i} - {len(duplicate_group)} identical files:")
                for file in duplicate_group:
                    info = analysis['file_info'][str(file)]
                    print(f"      - {file.name} (env: {info['environment_name']}, "
                          f"{info['modified_time'].strftime('%Y-%m-%d %H:%M')})")
        
        # File details
        print(f"\n📋 File Details:")
        for file_path, info in analysis['file_info'].items():
            status = "✅" if info['is_valid'] else "❌"
            print(f"   {status} {info['file_name']}")
            print(f"      Env: {info['environment_name']}, "
                  f"Deps: {info['dependencies_count']}, "
                  f"Size: {info['file_size']} bytes")
    
    def cleanup_duplicates(self, analysis: Dict, strategy: str = "keep_newest") -> int:
        """
        Clean up duplicate YAML files
        
        Args:
            analysis: Analysis results from analyze_yaml_files()
            strategy: Cleanup strategy - "keep_newest", "keep_oldest", or "interactive"
            
        Returns:
            Number of files removed
        """
        if not analysis['duplicates']:
            print(f"{Fore.GREEN}No duplicate files found.{Style.RESET_ALL}")
            return 0
        
        removed_count = 0
        
        print(f"\n🗑️  Cleaning up duplicates using strategy: {strategy}")
        
        for i, duplicate_group in enumerate(analysis['duplicates'], 1):
            print(f"\nProcessing duplicate group {i}:")
            
            if strategy == "keep_newest":
                # Sort by modification time, keep the newest
                sorted_files = sorted(duplicate_group, 
                                    key=lambda f: analysis['file_info'][str(f)]['modified_time'], 
                                    reverse=True)
                files_to_remove = sorted_files[1:]  # Remove all except the newest
                
            elif strategy == "keep_oldest":
                # Sort by modification time, keep the oldest
                sorted_files = sorted(duplicate_group, 
                                    key=lambda f: analysis['file_info'][str(f)]['modified_time'])
                files_to_remove = sorted_files[1:]  # Remove all except the oldest
                
            elif strategy == "interactive":
                # Let user choose which to keep
                print("   Which file would you like to keep?")
                for j, file in enumerate(duplicate_group, 1):
                    info = analysis['file_info'][str(file)]
                    print(f"   {j}. {file.name} ({info['modified_time'].strftime('%Y-%m-%d %H:%M')})")
                
                while True:
                    try:
                        choice = int(input("   Enter number to keep (others will be deleted): "))
                        if 1 <= choice <= len(duplicate_group):
                            keep_file = duplicate_group[choice - 1]
                            files_to_remove = [f for f in duplicate_group if f != keep_file]
                            break
                        else:
                            print("   Invalid choice. Please try again.")
                    except ValueError:
                        print("   Please enter a valid number.")
            
            # Remove the selected files
            for file_to_remove in files_to_remove:
                try:
                    file_to_remove.unlink()
                    print(f"   ✅ Removed: {file_to_remove.name}")
                    removed_count += 1
                    self.logger.info(f"Removed duplicate file: {file_to_remove}")
                except Exception as e:
                    print(f"   ❌ Failed to remove {file_to_remove.name}: {e}")
                    self.logger.error(f"Failed to remove {file_to_remove}: {e}")
        
        return removed_count
    
    def cleanup_by_environment(self, analysis: Dict, keep_latest: bool = True) -> int:
        """
        Clean up multiple files for the same environment
        
        Args:
            analysis: Analysis results from analyze_yaml_files()
            keep_latest: If True, keep the latest file; if False, keep the oldest
            
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        print(f"\n🗂️  Cleaning up multiple exports per environment...")
        print(f"   Strategy: Keep {'latest' if keep_latest else 'oldest'} file per environment")
        
        for env_name, files in analysis['by_environment'].items():
            if len(files) <= 1:
                continue
                
            print(f"\n   Environment '{env_name}' has {len(files)} exports:")
            
            # Sort by modification time
            sorted_files = sorted(files, 
                                key=lambda f: analysis['file_info'][str(f)]['modified_time'], 
                                reverse=keep_latest)
            
            keep_file = sorted_files[0]
            files_to_remove = sorted_files[1:]
            
            print(f"      Keeping: {keep_file.name}")
            
            for file_to_remove in files_to_remove:
                try:
                    file_to_remove.unlink()
                    print(f"      ✅ Removed: {file_to_remove.name}")
                    removed_count += 1
                    self.logger.info(f"Removed environment duplicate: {file_to_remove}")
                except Exception as e:
                    print(f"      ❌ Failed to remove {file_to_remove.name}: {e}")
                    self.logger.error(f"Failed to remove {file_to_remove}: {e}")
        
        return removed_count
    
    def cleanup_all_files(self, confirm: bool = True) -> int:
        """
        Remove all YAML files in the directory
        
        Args:
            confirm: Whether to ask for confirmation
            
        Returns:
            Number of files removed
        """
        yaml_files = self._get_yaml_files()
        
        if not yaml_files:
            print(f"{Fore.YELLOW}No YAML files found to clean up.{Style.RESET_ALL}")
            return 0
        
        print(f"\n🗑️  Found {len(yaml_files)} YAML files:")
        for i, file in enumerate(yaml_files, 1):
            print(f"   {i:2d}. {file.name}")
        
        if confirm:
            response = input(f"\n{Fore.YELLOW}Delete all these files? (y/N): {Style.RESET_ALL}")
            if response.lower() not in ['y', 'yes']:
                print("Cleanup cancelled.")
                return 0
        
        removed_count = 0
        for yaml_file in yaml_files:
            try:
                yaml_file.unlink()
                removed_count += 1
                self.logger.info(f"Deleted YAML file: {yaml_file}")
            except Exception as e:
                print(f"❌ Failed to delete {yaml_file.name}: {e}")
                self.logger.error(f"Failed to delete {yaml_file}: {e}")
        
        print(f"{Fore.GREEN}✅ Successfully deleted {removed_count} YAML files{Style.RESET_ALL}")
        return removed_count


def main():
    """Main function for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze and manage YAML environment files")
    parser.add_argument("--dir", type=Path, default="exported_environments",
                       help="Directory containing YAML files")
    parser.add_argument("--analyze", action="store_true", 
                       help="Analyze YAML files and show report")
    parser.add_argument("--cleanup-duplicates", choices=["keep_newest", "keep_oldest", "interactive"],
                       help="Clean up duplicate files")
    parser.add_argument("--cleanup-env-duplicates", action="store_true",
                       help="Clean up multiple files per environment (keep latest)")
    parser.add_argument("--cleanup-all", action="store_true",
                       help="Remove all YAML files")
    parser.add_argument("--no-confirm", action="store_true",
                       help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    analyzer = YAMLAnalyzer(args.dir)
    
    if args.analyze or not any([args.cleanup_duplicates, args.cleanup_env_duplicates, args.cleanup_all]):
        # Default action is to analyze
        analysis = analyzer.analyze_yaml_files()
        analyzer.print_analysis_report(analysis)
        
        if args.cleanup_duplicates:
            analyzer.cleanup_duplicates(analysis, args.cleanup_duplicates)
        
        if args.cleanup_env_duplicates:
            analyzer.cleanup_by_environment(analysis)
    
    if args.cleanup_all:
        analyzer.cleanup_all_files(confirm=not args.no_confirm)


if __name__ == "__main__":
    main()
