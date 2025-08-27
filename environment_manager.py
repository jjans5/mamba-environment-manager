#!/usr/bin/env python3
"""
Mamba Environment Manager

A comprehensive tool for managing mamba/conda environments with features for:
- Exporting broken environments to YAML files
- Reinstalling environments from YAML files
- Renaming environments with proper versioning
- Verification and cleanup of old environments
- Detailed logging and error handling
"""

import os
import sys
import subprocess
import logging
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import yaml
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class EnvironmentManager:
    """Main class for managing mamba/conda environments"""
    
    def __init__(self, use_mamba: bool = True):
        """
        Initialize the environment manager
        
        Args:
            use_mamba: Whether to use mamba instead of conda (default: True)
        """
        self.use_mamba = use_mamba
        self.cmd_base = "mamba" if use_mamba else "conda"
        self.log_file = "environment_manager.log"
        self.export_dir = Path("exported_environments")
        self.backup_dir = Path("backup_environments")
        
        # Setup logging
        self._setup_logging()
        
        # Create necessary directories
        self.export_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Verify mamba/conda is available
        self._verify_tool_availability()
        
        self.logger.info(f"Environment Manager initialized using {self.cmd_base}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _verify_tool_availability(self):
        """Verify that mamba or conda is available"""
        try:
            result = subprocess.run([self.cmd_base, "--version"], 
                                  capture_output=True, text=True, check=True)
            self.logger.info(f"{self.cmd_base} version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            if self.use_mamba:
                self.logger.warning("Mamba not found, falling back to conda")
                self.cmd_base = "conda"
                self.use_mamba = False
                self._verify_tool_availability()
            else:
                raise RuntimeError("Neither mamba nor conda found in PATH")
    
    def _run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a command and handle errors gracefully
        
        Args:
            cmd: Command to run as list of strings
            check: Whether to raise exception on non-zero exit code
            
        Returns:
            CompletedProcess object
        """
        try:
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            if result.returncode != 0 and check:
                self.logger.error(f"Command failed: {' '.join(cmd)}")
                self.logger.error(f"Error output: {result.stderr}")
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed with exit code {e.returncode}: {' '.join(cmd)}")
            self.logger.error(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error running command: {e}")
            raise
    
    def list_environments(self) -> List[Dict[str, str]]:
        """
        List all available environments with their details
        
        Returns:
            List of environment dictionaries with name, path, and python version
        """
        try:
            cmd = [self.cmd_base, "env", "list", "--json"]
            result = self._run_command(cmd)
            
            env_data = json.loads(result.stdout)
            environments = []
            
            for env_path in env_data['envs']:
                env_name = os.path.basename(env_path)
                if env_name == 'base':
                    continue
                    
                # Get Python version for this environment
                python_version = self._get_python_version(env_path)
                r_version = self._get_r_version(env_path)
                
                environments.append({
                    'name': env_name,
                    'path': env_path,
                    'python_version': python_version,
                    'r_version': r_version
                })
            
            return environments
        except Exception as e:
            self.logger.error(f"Failed to list environments: {e}")
            return []
    
    def _get_python_version(self, env_path: str) -> Optional[str]:
        """Get Python version for an environment"""
        try:
            python_exe = os.path.join(env_path, 'bin', 'python')
            if not os.path.exists(python_exe):
                python_exe = os.path.join(env_path, 'python.exe')  # Windows
            
            if os.path.exists(python_exe):
                result = subprocess.run([python_exe, '--version'], 
                                      capture_output=True, text=True, check=True)
                version_match = re.search(r'Python (\d+\.\d+)', result.stdout)
                if version_match:
                    return version_match.group(1)
        except:
            pass
        return None
    
    def _get_r_version(self, env_path: str) -> Optional[str]:
        """Get R version for an environment"""
        try:
            r_exe = os.path.join(env_path, 'bin', 'R')
            if not os.path.exists(r_exe):
                r_exe = os.path.join(env_path, 'R.exe')  # Windows
            
            if os.path.exists(r_exe):
                result = subprocess.run([r_exe, '--version'], 
                                      capture_output=True, text=True, check=True)
                version_match = re.search(r'R version (\d+\.\d+)', result.stdout)
                if version_match:
                    return version_match.group(1)
        except:
            pass
        return None
    
    def export_environment(self, env_name: str) -> Optional[Path]:
        """
        Export an environment to a YAML file
        
        Args:
            env_name: Name of the environment to export
            
        Returns:
            Path to the exported YAML file, or None if failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.export_dir / f"{env_name}_{timestamp}.yml"
            
            cmd = [self.cmd_base, "env", "export", "-n", env_name, "-f", str(export_file)]
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully exported {env_name} to {export_file}")
                return export_file
            else:
                self.logger.error(f"Failed to export {env_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error exporting environment {env_name}: {e}")
            return None
    
    def generate_new_name(self, old_name: str, python_version: Optional[str], 
                         r_version: Optional[str]) -> str:
        """
        Generate a new environment name based on naming convention
        
        Args:
            old_name: Original environment name
            python_version: Python version (e.g., "3.9")
            r_version: R version (e.g., "4.1")
            
        Returns:
            New environment name in lowercase with version suffix
        """
        # Convert to lowercase
        new_name = old_name.lower()
        
        # Add version suffixes
        if python_version:
            new_name += f"_py{python_version.replace('.', '')}"
        if r_version:
            new_name += f"_r{r_version.replace('.', '')}"
        
        return new_name
    
    def create_environment_from_yaml(self, yaml_file: Path, new_name: str) -> bool:
        """
        Create a new environment from a YAML file
        
        Args:
            yaml_file: Path to the YAML file
            new_name: Name for the new environment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, try to modify the YAML to use the new name
            self._update_yaml_name(yaml_file, new_name)
            
            cmd = [self.cmd_base, "env", "create", "-f", str(yaml_file), "-n", new_name]
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully created environment {new_name}")
                return True
            else:
                self.logger.error(f"Failed to create environment {new_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating environment {new_name}: {e}")
            return False
    
    def _update_yaml_name(self, yaml_file: Path, new_name: str):
        """Update the name field in a YAML file"""
        try:
            with open(yaml_file, 'r') as f:
                content = f.read()
            
            # Replace the name field
            content = re.sub(r'^name:.*$', f'name: {new_name}', content, flags=re.MULTILINE)
            
            with open(yaml_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            self.logger.warning(f"Could not update YAML name field: {e}")
    
    def verify_environment(self, env_name: str) -> bool:
        """
        Verify that an environment was created successfully
        
        Args:
            env_name: Name of the environment to verify
            
        Returns:
            True if environment exists and is functional, False otherwise
        """
        try:
            # Check if environment exists
            cmd = [self.cmd_base, "env", "list", "--json"]
            result = self._run_command(cmd)
            env_data = json.loads(result.stdout)
            
            env_exists = any(env_name in env_path for env_path in env_data['envs'])
            
            if not env_exists:
                self.logger.error(f"Environment {env_name} does not exist")
                return False
            
            # Try to activate and run a simple command
            if self.use_mamba:
                test_cmd = [self.cmd_base, "run", "-n", env_name, "python", "--version"]
            else:
                test_cmd = ["conda", "run", "-n", env_name, "python", "--version"]
            
            result = self._run_command(test_cmd, check=False)
            
            if result.returncode == 0:
                self.logger.info(f"Environment {env_name} verified successfully")
                return True
            else:
                self.logger.warning(f"Environment {env_name} exists but may have issues")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying environment {env_name}: {e}")
            return False
    
    def remove_environment(self, env_name: str) -> bool:
        """
        Remove an environment
        
        Args:
            env_name: Name of the environment to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [self.cmd_base, "env", "remove", "-n", env_name, "--yes"]
            result = self._run_command(cmd)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully removed environment {env_name}")
                return True
            else:
                self.logger.error(f"Failed to remove environment {env_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing environment {env_name}: {e}")
            return False
    
    def process_environment(self, env_info: Dict[str, str]) -> bool:
        """
        Process a single environment: export, reinstall, verify, and cleanup
        
        Args:
            env_info: Dictionary containing environment information
            
        Returns:
            True if all steps successful, False otherwise
        """
        env_name = env_info['name']
        python_version = env_info['python_version']
        r_version = env_info['r_version']
        
        self.logger.info(f"\n{Fore.CYAN}=== Processing environment: {env_name} ==={Style.RESET_ALL}")
        
        # Step 1: Export environment
        self.logger.info(f"{Fore.YELLOW}Step 1: Exporting environment...{Style.RESET_ALL}")
        yaml_file = self.export_environment(env_name)
        if not yaml_file:
            self.logger.error(f"Failed to export {env_name}, skipping...")
            return False
        
        # Step 2: Generate new name
        new_name = self.generate_new_name(env_name, python_version, r_version)
        self.logger.info(f"New environment name: {new_name}")
        
        # Step 3: Create new environment
        self.logger.info(f"{Fore.YELLOW}Step 2: Creating new environment...{Style.RESET_ALL}")
        if not self.create_environment_from_yaml(yaml_file, new_name):
            self.logger.error(f"Failed to create new environment {new_name}")
            return False
        
        # Step 4: Verify new environment
        self.logger.info(f"{Fore.YELLOW}Step 3: Verifying new environment...{Style.RESET_ALL}")
        if not self.verify_environment(new_name):
            self.logger.error(f"New environment {new_name} verification failed")
            return False
        
        # Step 5: Remove old environment
        self.logger.info(f"{Fore.YELLOW}Step 4: Removing old environment...{Style.RESET_ALL}")
        if not self.remove_environment(env_name):
            self.logger.warning(f"Failed to remove old environment {env_name}")
            # Don't return False here as the main goal (new env) was achieved
        
        self.logger.info(f"{Fore.GREEN}✓ Successfully processed {env_name} -> {new_name}{Style.RESET_ALL}")
        return True
    
    def run_interactive_mode(self):
        """Run the tool in interactive mode"""
        print(f"\n{Fore.CYAN}=== Mamba Environment Manager ==={Style.RESET_ALL}")
        print("This tool will help you reinstall and rename your environments.\n")
        
        # List all environments
        environments = self.list_environments()
        if not environments:
            print(f"{Fore.RED}No environments found!{Style.RESET_ALL}")
            return
        
        print(f"Found {len(environments)} environments:")
        for i, env in enumerate(environments, 1):
            python_ver = env['python_version'] or 'Unknown'
            r_ver = env['r_version'] or 'None'
            new_name = self.generate_new_name(env['name'], env['python_version'], env['r_version'])
            print(f"{i:2}. {env['name']} (Python: {python_ver}, R: {r_ver}) -> {new_name}")
        
        print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print("1. Process all environments")
        print("2. Select specific environments")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            self._process_all_environments(environments)
        elif choice == "2":
            self._process_selected_environments(environments)
        elif choice == "3":
            print("Exiting...")
            return
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
    
    def _process_all_environments(self, environments: List[Dict[str, str]]):
        """Process all environments"""
        print(f"\n{Fore.YELLOW}Processing all {len(environments)} environments...{Style.RESET_ALL}")
        
        successful = 0
        failed = 0
        
        for env in environments:
            if self.process_environment(env):
                successful += 1
            else:
                failed += 1
        
        print(f"\n{Fore.CYAN}=== Summary ==={Style.RESET_ALL}")
        print(f"{Fore.GREEN}Successful: {successful}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    def _process_selected_environments(self, environments: List[Dict[str, str]]):
        """Process selected environments"""
        print("\nEnter environment numbers to process (comma-separated):")
        print("Example: 1,3,5 or 1-3,5")
        
        selection = input("Selection: ").strip()
        
        try:
            indices = self._parse_selection(selection, len(environments))
            selected_envs = [environments[i-1] for i in indices]
            
            print(f"\nProcessing {len(selected_envs)} selected environments...")
            
            successful = 0
            failed = 0
            
            for env in selected_envs:
                if self.process_environment(env):
                    successful += 1
                else:
                    failed += 1
            
            print(f"\n{Fore.CYAN}=== Summary ==={Style.RESET_ALL}")
            print(f"{Fore.GREEN}Successful: {successful}{Style.RESET_ALL}")
            print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
            
        except ValueError as e:
            print(f"{Fore.RED}Invalid selection: {e}{Style.RESET_ALL}")
    
    def _parse_selection(self, selection: str, max_num: int) -> List[int]:
        """Parse user selection string into list of indices"""
        indices = set()
        
        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                indices.update(range(start, end + 1))
            else:
                indices.add(int(part))
        
        # Validate indices
        for idx in indices:
            if idx < 1 or idx > max_num:
                raise ValueError(f"Index {idx} is out of range (1-{max_num})")
        
        return sorted(list(indices))


def main():
    """Main entry point"""
    try:
        manager = EnvironmentManager()
        manager.run_interactive_mode()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
