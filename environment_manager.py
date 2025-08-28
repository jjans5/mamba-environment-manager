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
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
import yaml
from colorama import init, Fore, Style

# Import the new YAML analyzer
from yaml_analyzer import YAMLAnalyzer

# Import new utilities
try:
    from utils.environment_cloner import EnvironmentCloner
    from utils.simple_log_analyzer import debug_environment_failure, analyze_failures
except ImportError:
    # Fallback if utils not in path
    EnvironmentCloner = None
    debug_environment_failure = None
    analyze_failures = None

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
    
    def _run_command_with_progress(self, cmd: List[str], operation_name: str = "Operation"):
        """
        Run a command with real-time progress output for long operations
        
        Args:
            cmd: Command to run as list of strings
            operation_name: Name of the operation for progress messages
            
        Returns:
            CompletedProcess-like object with combined stdout/stderr
        """
        try:
            self.logger.debug(f"Running command with progress: {' '.join(cmd)}")
            print(f"🔄 {operation_name} in progress...")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            output_lines = []
            last_progress_time = 0
            import time
            
            # Read output line by line
            while True:
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        output_lines.append(line.rstrip())
                        current_time = time.time()
                        
                        # Show progress every 2 seconds or for important lines
                        if (current_time - last_progress_time > 2.0 or 
                            any(keyword in line.lower() for keyword in ['solving', 'downloading', 'extracting', 'installing', 'collecting', 'preparing', 'executing', 'verifying'])):
                            
                            # Clean and show the progress line
                            clean_line = line.strip()
                            if clean_line and not clean_line.startswith('#'):
                                # Make certain progress lines more prominent
                                if any(keyword in clean_line.lower() for keyword in ['solving environment', 'downloading and extracting', 'preparing transaction', 'executing transaction']):
                                    print(f"📦 {clean_line}")
                                elif 'done' in clean_line.lower():
                                    print(f"✓  {clean_line}")
                                else:
                                    print(f"   {clean_line}")
                                last_progress_time = current_time
                
                # Check if process has finished
                if process.poll() is not None:
                    break
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            
            # Create a result object similar to subprocess.run
            combined_output = '\n'.join(output_lines)
            
            # Create a simple result object
            class ProcessResult:
                def __init__(self, returncode: int, stdout: str, stderr: str = ""):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            result = ProcessResult(return_code, combined_output)
            
            if return_code == 0:
                print(f"✅ {operation_name} completed successfully!")
            else:
                print(f"❌ {operation_name} failed with exit code {return_code}")
                self.logger.error(f"Command failed: {' '.join(cmd)}")
                self.logger.error(f"Output: {combined_output}")
            
            return result
            
        except Exception as e:
            print(f"❌ {operation_name} failed with error: {e}")
            self.logger.error(f"Unexpected error running command: {e}")
            raise
    
    def _run_command_with_progress_shell(self, cmd_str: str, operation_name: str = "Operation", log_file: Optional[Path] = None):
        """
        Run a shell command with real-time progress output for long operations
        
        Args:
            cmd_str: Shell command string to run
            operation_name: Name of the operation for progress messages
            log_file: Optional path to log file for output
            
        Returns:
            ProcessResult-like object with combined stdout/stderr
        """
        try:
            self.logger.debug(f"Running shell command with progress: {cmd_str}")
            print(f"🔄 {operation_name} in progress...")
            
            if log_file:
                print(f"📝 Logging to: {log_file}")
            
            # Start the process using shell=True
            process = subprocess.Popen(
                cmd_str,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            output_lines = []
            last_progress_time = 0
            import time
            
            # Prepare log file if specified
            log_file_handle = None
            if log_file:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                log_file_handle = open(log_file, 'w')
            
            # Read output line by line
            while True:
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        output_lines.append(line.rstrip())
                        
                        # Write to log file if specified
                        if log_file_handle:
                            log_file_handle.write(line)
                            log_file_handle.flush()
                        
                        current_time = time.time()
                        
                        # Show progress every 2 seconds or for important lines
                        if (current_time - last_progress_time > 2.0 or 
                            any(keyword in line.lower() for keyword in ['solving', 'downloading', 'extracting', 'installing', 'collecting', 'preparing', 'executing', 'verifying'])):
                            
                            # Clean and show the progress line
                            clean_line = line.strip()
                            if clean_line and not clean_line.startswith('#'):
                                # Make certain progress lines more prominent
                                if any(keyword in clean_line.lower() for keyword in ['solving environment', 'downloading and extracting', 'preparing transaction', 'executing transaction']):
                                    print(f"📦 {clean_line}")
                                elif 'done' in clean_line.lower():
                                    print(f"✓  {clean_line}")
                                else:
                                    print(f"   {clean_line}")
                                last_progress_time = current_time
                
                # Check if process has finished
                if process.poll() is not None:
                    break
            
            # Close log file if it was opened
            if log_file_handle:
                log_file_handle.close()
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            
            # Create a result object similar to subprocess.run
            combined_output = '\n'.join(output_lines)
            
            # Create a simple result object
            class ProcessResult:
                def __init__(self, returncode: int, stdout: str, stderr: str = ""):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            
            result = ProcessResult(return_code, combined_output)
            
            if return_code == 0:
                print(f"✅ {operation_name} completed successfully!")
                if log_file:
                    print(f"📝 Full log saved to: {log_file}")
            else:
                print(f"❌ {operation_name} failed with exit code {return_code}")
                self.logger.error(f"Shell command failed: {cmd_str}")
                self.logger.error(f"Output: {combined_output}")
                if log_file:
                    print(f"📝 Error log saved to: {log_file}")
            
            return result
            
        except Exception as e:
            print(f"❌ {operation_name} failed with error: {e}")
            self.logger.error(f"Unexpected error running shell command: {e}")
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
    
    def _repair_mamba_yaml(self, yaml_content: str, env_name: str) -> str:
        """
        Attempt to repair common mamba YAML export issues
        
        Args:
            yaml_content: Raw YAML content from mamba export
            env_name: Environment name for logging
            
        Returns:
            Repaired YAML content
        """
        self.logger.debug(f"Attempting to repair YAML for {env_name}")
        
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
                        self.logger.debug(f"Fixed channels format: '{next_line.strip()}' -> '  - {channel_name}'")
        
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
                    old_line = line
                    lines[i] = f"  - {line.strip()}"
                    self.logger.debug(f"Fixed dependency format: '{old_line.strip()}' -> '  - {line.strip()}'")
        
        repaired = '\n'.join(lines)
        
        # Fix 4: Remove any null bytes or other problematic characters
        repaired = repaired.replace('\x00', '')
        
        # Fix 5: Ensure UTF-8 encoding
        repaired = repaired.encode('utf-8', errors='ignore').decode('utf-8')
        
        self.logger.debug(f"YAML repair completed for {env_name}")
        return repaired
    
    def _is_environment_empty(self, yaml_data: dict) -> bool:
        """
        Check if an environment is empty (has no meaningful packages)
        
        Args:
            yaml_data: Parsed YAML data from environment export
            
        Returns:
            True if environment is empty, False otherwise
        """
        dependencies = yaml_data.get('dependencies', [])
        if not dependencies:
            return True
            
        # Check if dependencies only contains base packages or is effectively empty
        meaningful_packages = []
        for dep in dependencies:
            if isinstance(dep, str):
                # Skip base packages that come with every conda/mamba environment
                base_packages = {'python', '_libgcc_mutex', '_openmp_mutex', 'libgcc-ng', 'libgomp', 'libstdcxx-ng'}
                package_name = dep.split('=')[0].split()[0].lower()
                if package_name not in base_packages:
                    meaningful_packages.append(dep)
            elif isinstance(dep, dict) and 'pip' in dep:
                # Check pip dependencies
                pip_deps = dep.get('pip', [])
                if pip_deps:
                    meaningful_packages.extend(pip_deps)
        
        return len(meaningful_packages) == 0
    
    def _is_base_environment(self, env_path: str, env_name: str) -> bool:
        """
        Check if an environment is a base environment that should not be removed
        
        Args:
            env_path: Path to the environment
            env_name: Name of the environment
            
        Returns:
            True if it's a base environment, False otherwise
        """
        # Base environment typically has same name as the parent directory
        # or is located directly in the conda/mamba installation directory
        parent_dir = os.path.basename(os.path.dirname(env_path))
        
        # Common base environment patterns:
        # 1. Environment name matches parent directory (e.g., anaconda3/anaconda3, miniconda3/miniconda3)
        # 2. Environment is in root conda installation (no 'envs' in path)
        # 3. Environment name is 'base'
        
        if env_name == 'base':
            return True
            
        if env_name == parent_dir:
            return True
            
        if 'envs' not in env_path:
            return True
            
        return False
    
    def export_environment(self, env_name: str) -> Union[Optional[Path], str]:
        """
        Export an environment to a YAML file
        
        Args:
            env_name: Name of the environment to export
            
        Returns:
            Path to the exported YAML file, or None if failed
        """
        try:
            # First check if environment exists
            env_list = self.list_environments()
            if not any(env['name'] == env_name for env in env_list):
                self.logger.error(f"Environment '{env_name}' does not exist")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.export_dir / f"{env_name}_{timestamp}.yml"
            
            # Different command formats for mamba vs conda
            if self.cmd_base == "mamba":
                # Mamba doesn't have -f/--file option, need to redirect output
                cmd = [self.cmd_base, "env", "export", "-n", env_name]
                self.logger.debug(f"Trying mamba command: {' '.join(cmd)} > {export_file}")
                
                try:
                    result = self._run_command(cmd, check=False)  # Don't raise exception on non-zero exit
                    if result.returncode == 0:
                        # Validate the stdout content before writing
                        if not result.stdout or not result.stdout.strip():
                            self.logger.error(f"Mamba export returned empty output for {env_name}")
                            return None
                        
                        # Try to parse the YAML to validate it
                        try:
                            import yaml
                            yaml_data = yaml.safe_load(result.stdout)
                            if not yaml_data or not isinstance(yaml_data, dict):
                                self.logger.error(f"Mamba export returned invalid YAML structure for {env_name}")
                                self.logger.debug(f"Invalid YAML content: {result.stdout[:500]}")
                                return None
                            
                            # Validate required fields
                            if 'name' not in yaml_data:
                                self.logger.error(f"Mamba export missing 'name' field for {env_name}")
                                return None
                            
                            # Validate channels field
                            channels = yaml_data.get('channels')
                            if channels is not None and not isinstance(channels, list):
                                self.logger.warning(f"Fixing invalid channels format for {env_name}: {type(channels)} -> list")
                                if isinstance(channels, str):
                                    yaml_data['channels'] = [channels]
                                else:
                                    yaml_data['channels'] = []
                            
                            # Validate dependencies field
                            dependencies = yaml_data.get('dependencies')
                            if dependencies is not None and not isinstance(dependencies, list):
                                self.logger.warning(f"Fixing invalid dependencies format for {env_name}: {type(dependencies)} -> list")
                                yaml_data['dependencies'] = []
                            
                            # Check if environment is empty
                            if self._is_environment_empty(yaml_data):
                                self.logger.warning(f"Environment '{env_name}' is empty (no meaningful packages). Marking for deletion.")
                                return "EMPTY"  # Special return value to indicate empty environment
                            
                            # Re-export the cleaned YAML to ensure it's valid
                            clean_yaml = yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)
                            
                        except yaml.YAMLError as e:
                            self.logger.warning(f"Mamba export YAML parsing failed for {env_name}: {e}")
                            self.logger.debug(f"Attempting to repair YAML...")
                            
                            # Try to repair the YAML
                            try:
                                repaired_yaml = self._repair_mamba_yaml(result.stdout, env_name)
                                yaml_data = yaml.safe_load(repaired_yaml)
                                if yaml_data and isinstance(yaml_data, dict):
                                    self.logger.info(f"Successfully repaired YAML for {env_name}")
                                    clean_yaml = repaired_yaml
                                else:
                                    self.logger.error(f"YAML repair failed for {env_name}")
                                    return None
                            except Exception as repair_e:
                                self.logger.error(f"YAML repair failed for {env_name}: {repair_e}")
                                self.logger.debug(f"Original problematic YAML (first 500 chars): {result.stdout[:500]}")
                                return None
                        
                        # Write the validated/cleaned output to file
                        with open(export_file, 'w', encoding='utf-8') as f:
                            if 'clean_yaml' in locals():
                                # Use the cleaned YAML if we had to fix something
                                f.write(clean_yaml)
                                self.logger.debug(f"Wrote cleaned YAML for {env_name}")
                            else:
                                # Use original output if no cleaning was needed
                                f.write(result.stdout)
                        
                        # Double-check the written file
                        try:
                            with open(export_file, 'r', encoding='utf-8') as f:
                                file_data = yaml.safe_load(f)
                            if not file_data:
                                self.logger.error(f"Written YAML file is corrupted for {env_name}")
                                export_file.unlink()  # Clean up corrupted file
                                return None
                        except Exception as e:
                            self.logger.error(f"Written YAML file validation failed for {env_name}: {e}")
                            if export_file.exists():
                                export_file.unlink()  # Clean up corrupted file
                            return None
                        
                        self.logger.info(f"Successfully exported {env_name} to {export_file}")
                        return export_file
                    else:
                        self.logger.error(f"Mamba export failed with exit code {result.returncode}")
                        if result.stderr:
                            self.logger.error(f"Error output: {result.stderr}")
                        return None
                except Exception as e:
                    self.logger.error(f"Mamba export failed with exception: {e}")
                    
                    # If mamba fails, try conda as fallback
                    if self.cmd_base == "mamba":
                        self.logger.warning(f"Trying conda fallback for {env_name}")
                        try:
                            conda_cmd = ["conda", "env", "export", "-n", env_name]
                            conda_result = self._run_command(conda_cmd, check=False)
                            if conda_result.returncode == 0 and conda_result.stdout:
                                # Validate conda output
                                import yaml
                                conda_yaml_data = yaml.safe_load(conda_result.stdout)
                                if conda_yaml_data and isinstance(conda_yaml_data, dict):
                                    # Check if environment is empty
                                    if self._is_environment_empty(conda_yaml_data):
                                        self.logger.warning(f"Environment '{env_name}' is empty (no meaningful packages). Marking for deletion.")
                                        return "EMPTY"  # Special return value to indicate empty environment
                                    
                                    with open(export_file, 'w', encoding='utf-8') as f:
                                        f.write(conda_result.stdout)
                                    self.logger.info(f"Successfully exported {env_name} to {export_file} using conda fallback")
                                    return export_file
                        except Exception as conda_e:
                            self.logger.debug(f"Conda fallback also failed: {conda_e}")
                    
                    return None
                    
            else:
                # Conda has -f/--file option, try different formats
                commands_to_try = [
                    [self.cmd_base, "env", "export", "-n", env_name, "--file", str(export_file)],  # Long form
                    [self.cmd_base, "env", "export", "-n", env_name, "-f", str(export_file)],      # Short form
                    [self.cmd_base, "env", "export", "--name", env_name, "--file", str(export_file)], # All long form
                ]
                
                for cmd in commands_to_try:
                    try:
                        self.logger.debug(f"Trying conda command: {' '.join(cmd)}")
                        result = self._run_command(cmd, check=False)  # Don't raise exception on non-zero exit
                        if result.returncode == 0:
                            # Validate the written file
                            try:
                                with open(export_file, 'r', encoding='utf-8') as f:
                                    import yaml
                                    file_data = yaml.safe_load(f)
                                if not file_data:
                                    self.logger.error(f"Conda export created corrupted YAML file for {env_name}")
                                    if export_file.exists():
                                        export_file.unlink()  # Clean up corrupted file
                                    continue
                                
                                # Check if environment is empty
                                if self._is_environment_empty(file_data):
                                    self.logger.warning(f"Environment '{env_name}' is empty (no meaningful packages). Marking for deletion.")
                                    if export_file.exists():
                                        export_file.unlink()  # Clean up the file since we don't need it
                                    return "EMPTY"  # Special return value to indicate empty environment
                                    
                            except Exception as e:
                                self.logger.error(f"Conda export file validation failed for {env_name}: {e}")
                                if export_file.exists():
                                    export_file.unlink()  # Clean up corrupted file
                                continue
                            
                            self.logger.info(f"Successfully exported {env_name} to {export_file}")
                            return export_file
                        else:
                            self.logger.debug(f"Command failed with exit code {result.returncode}")
                            if result.stderr:
                                self.logger.debug(f"Error output: {result.stderr}")
                            continue
                    except Exception as e:
                        self.logger.debug(f"Command failed with exception: {e}")
                        continue
                
                # If we get here, all conda commands failed
                self.logger.error(f"Failed to export {env_name} after trying multiple conda command formats")
                return None
                
        except Exception as e:
            self.logger.error(f"Error exporting environment {env_name}: {e}")
            return None
    
    def generate_new_name(self, old_name: str, python_version: Optional[str], 
                         r_version: Optional[str], existing_names: Optional[List[str]] = None,
                         yaml_file: Optional[Path] = None) -> str:
        """
        Generate a new environment name based on naming convention with smart conflict resolution
        
        Args:
            old_name: Original environment name
            python_version: Python version (e.g., "3.9")
            r_version: R version (e.g., "4.1")
            existing_names: List of existing environment names to avoid conflicts
            yaml_file: Path to YAML file for package version extraction
            
        Returns:
            New environment name in lowercase with version suffix
        """
        if existing_names is None:
            existing_names = []
        
        # Convert to lowercase
        base_name = old_name.lower()
        
        # Check if name already contains version patterns and clean them
        cleaned_base = self._clean_existing_versions(base_name)
        
        # Extract package versions if YAML file is provided
        package_versions = {}
        if yaml_file and yaml_file.exists():
            package_versions = self._extract_package_versions_from_yaml(yaml_file, old_name)
        
        # Start with cleaned base name
        new_name = cleaned_base
        
        # Add package versions first (before language versions)
        if package_versions:
            new_name = self._add_package_versions_to_name(new_name, package_versions)
        
        # For version addition, we should add them consistently to create standardized names
        # Since we're cleaning the base name and creating a new standardized name,
        # we want consistent versioning regardless of what was in the original
        
        # Add Python version if available
        if python_version:
            py_suffix = f"_py{python_version.replace('.', '')}"
            new_name += py_suffix
        
        # Add R version if available  
        if r_version:
            r_suffix = f"_r{r_version.replace('.', '')}"
            new_name += r_suffix
        
        # Handle conflicts by adding incremental suffix
        original_new_name = new_name
        counter = 1
        while new_name in existing_names or new_name == old_name.lower():
            new_name = f"{original_new_name}_v{counter}"
            counter += 1
        
        return new_name
    
    def _version_already_in_name(self, name: str, version: str, lang_type: str) -> bool:
        """
        Check if a specific version is already present in the name
        
        Args:
            name: Environment name to check
            version: Version string (e.g., "3.10")
            lang_type: Either "python" or "r"
            
        Returns:
            True if version is already present
        """
        import re
        
        # Convert version formats
        version_nodot = version.replace('.', '')
        version_patterns = [
            version,           # 3.10
            version_nodot,     # 310
        ]
        
        for ver_pattern in version_patterns:
            if lang_type == 'python':
                patterns = [
                    rf'_py{re.escape(ver_pattern)}(?:_|$)',
                    rf'_python{re.escape(ver_pattern)}(?:_|$)',
                    rf'py{re.escape(ver_pattern)}(?:_|$)',
                    rf'_{re.escape(version)}(?:_|$)',  # Direct version match
                ]
            else:  # r
                patterns = [
                    rf'_r{re.escape(ver_pattern)}(?:_|$)',
                    rf'r{re.escape(ver_pattern)}(?:_|$)',
                    rf'_{re.escape(version)}(?:_|$)',  # Direct version match
                ]
            
            for pattern in patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    return True
        
        return False
    
    def _clean_existing_versions(self, name: str) -> str:
        """
        Remove existing version patterns from environment names
        
        Args:
            name: Environment name to clean
            
        Returns:
            Cleaned name without version suffixes
        """
        import re
        
        # Remove common version patterns - more comprehensive
        patterns = [
            r'_py\d+(\.\d+)?',          # _py3.10, _py310
            r'_python\d+(\.\d+)?',      # _python3.10
            r'_r\d+(\.\d+)?',           # _r4.2, _r42  
            r'_r_?\d+(\.\d+)?',         # _r4.2, _r_4.2
            r'py\d+(\.\d+)?$',          # py310 at end
            r'python\d+(\.\d+)?$',      # python310 at end
            r'r\d+(\.\d+)?$',           # r42 at end
            r'_\d+\.\d+(?=_|$)',        # _3.10, _4.2 (but keep if part of package name)
            r'_v\d+$',                  # _v1, _v2 version suffixes
            # More specific patterns to avoid duplication
            r'_(\d+)\.(\d+)_py\1\2',    # Remove _3.10_py310 duplication
            r'_(\d+)\.(\d+)_r\1\2',     # Remove _4.2_r42 duplication
        ]
        
        cleaned_name = name
        for pattern in patterns:
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
        
        # Clean up any trailing underscores or double underscores
        cleaned_name = re.sub(r'_+', '_', cleaned_name)  # Multiple underscores to single
        cleaned_name = cleaned_name.strip('_')
        
        # If name becomes empty or too short, use original
        if len(cleaned_name) < 2:
            return name
            
        return cleaned_name
    
    def _has_python_version(self, name: str) -> bool:
        """Check if name already contains Python version"""
        import re
        patterns = [
            r'_py\d+',
            r'_python\d+',
            r'py\d+',
            r'python\d+'
        ]
        return any(re.search(pattern, name, re.IGNORECASE) for pattern in patterns)
    
    def _has_r_version(self, name: str) -> bool:
        """Check if name already contains R version"""
        import re
        patterns = [
            r'_r\d+',
            r'_r_\d+',
            r'r\d+$'
        ]
        return any(re.search(pattern, name, re.IGNORECASE) for pattern in patterns)
    
    def _extract_package_versions_from_yaml(self, yaml_file: Path, env_name: str) -> Dict[str, str]:
        """
        Extract key package versions from exported YAML file
        
        Args:
            yaml_file: Path to the YAML environment file
            env_name: Original environment name to guess relevant packages
            
        Returns:
            Dictionary of package names and versions
        """
        try:
            with open(yaml_file, 'r') as f:
                env_data = yaml.safe_load(f)
            
            # Validate that we have valid YAML data
            if not env_data or not isinstance(env_data, dict):
                self.logger.warning(f"Invalid or empty YAML data in {yaml_file}")
                return {}
            
            package_versions = {}
            dependencies = env_data.get('dependencies', [])
            
            # Handle case where dependencies might be None
            if dependencies is None:
                self.logger.warning(f"No dependencies found in {yaml_file}")
                return {}
            
            # Ensure dependencies is a list
            if not isinstance(dependencies, list):
                self.logger.warning(f"Dependencies is not a list in {yaml_file}: {type(dependencies)}")
                return {}
            
            # Common package mappings for environment names
            package_mappings = {
                'scanpy': ['scanpy', 'scanpy-scripts'],
                'harmony': ['harmonypy', 'harmony-pytorch', 'harmony'],
                'scenic': ['pyscenic', 'scenic'],
                'seurat': ['rpy2', 'seurat'],  # For R packages accessed via Python
                'cistopic': ['pycistopic', 'cistopic'],
                'cellrank': ['cellrank'],
                'cellxgene': ['cellxgene'],
                'napari': ['napari'],
                'neuroglancer': ['neuroglancer'],
                'nextflow': ['nextflow'],
                'deeptools': ['deeptools'],
                'biopython': ['biopython', 'bio'],
                'elastix': ['elastix', 'itk-elastix'],
                'pytorch': ['pytorch', 'torch'],
                'tensorflow': ['tensorflow', 'tf'],
                'keras': ['keras'],
                'sklearn': ['scikit-learn', 'sklearn'],
                'pandas': ['pandas'],
                'numpy': ['numpy'],
                'scipy': ['scipy'],
                'matplotlib': ['matplotlib'],
                'plotly': ['plotly'],
                'jupyter': ['jupyter', 'jupyterlab'],
            }
            
            # Extract package name from environment name
            env_name_lower = env_name.lower()
            
            # Look for relevant packages ONLY if they're mentioned in environment name
            relevant_packages = set()
            for key, packages in package_mappings.items():
                if key in env_name_lower:
                    relevant_packages.update(packages)
            
            # Also check for package names directly mentioned in env name
            # This catches cases where the package name is in the environment name
            for dep in dependencies:
                if isinstance(dep, str):
                    pkg_name = dep.split('=')[0].split('[')[0].strip()
                    # Only add package if it's mentioned in environment name
                    if any(pkg in env_name_lower for pkg in [pkg_name.lower()]):
                        relevant_packages.add(pkg_name)
                elif isinstance(dep, dict) and 'pip' in dep:
                    # Handle pip dependencies
                    pip_deps = dep['pip']
                    if pip_deps and isinstance(pip_deps, list):
                        for pip_dep in pip_deps:
                            if isinstance(pip_dep, str):
                                pkg_name = re.split(r'[=><]', pip_dep)[0].strip()
                                # Only add package if it's mentioned in environment name
                                if any(pkg in env_name_lower for pkg in [pkg_name.lower()]):
                                    relevant_packages.add(pkg_name)
            
            # Extract versions for relevant packages
            for dep in dependencies:
                if isinstance(dep, str):
                    # Handle conda package format: package=version=build or package=version
                    parts = dep.split('=')
                    if len(parts) >= 2:
                        pkg_name = parts[0].strip()
                        version = parts[1].strip()
                        
                        # Check if package matches relevant packages (handle R package naming)
                        pkg_matches_relevant = False
                        
                        # Direct match
                        if pkg_name.lower() in [p.lower() for p in relevant_packages]:
                            pkg_matches_relevant = True
                        
                        # Handle R packages: r-seurat should match 'seurat' in relevant_packages
                        elif pkg_name.lower().startswith('r-'):
                            r_pkg_name = pkg_name[2:]  # Remove 'r-' prefix
                            if r_pkg_name.lower() in [p.lower() for p in relevant_packages]:
                                pkg_matches_relevant = True
                        
                        # Handle python packages: py-package should match 'package' 
                        elif pkg_name.lower().startswith('py-'):
                            py_pkg_name = pkg_name[3:]  # Remove 'py-' prefix
                            if py_pkg_name.lower() in [p.lower() for p in relevant_packages]:
                                pkg_matches_relevant = True
                        
                        if pkg_matches_relevant:
                            # Clean version - keep up to 3 parts (major.minor.patch)
                            clean_version = version
                            # Use the base package name (without r- or py- prefix) for storage
                            base_pkg_name = pkg_name.lower()
                            if base_pkg_name.startswith('r-'):
                                base_pkg_name = base_pkg_name[2:]
                            elif base_pkg_name.startswith('py-'):
                                base_pkg_name = base_pkg_name[3:]
                            package_versions[base_pkg_name] = clean_version
                
                elif isinstance(dep, dict) and 'pip' in dep:
                    # Handle pip dependencies
                    pip_deps = dep['pip']
                    if pip_deps and isinstance(pip_deps, list):
                        for pip_dep in pip_deps:
                            if isinstance(pip_dep, str):
                                # Handle pip format: package==version or package>=version
                                # Updated regex to capture full version including alpha/beta/dev suffixes
                                match = re.match(r'([^=><]+)[=><]+(.+)', pip_dep)
                                if match:
                                    pkg_name, version = match.groups()
                                    pkg_name = pkg_name.strip()
                                    version = version.strip()
                                    
                                    # Check if package matches relevant packages (handle case sensitivity)
                                    pkg_matches_relevant = False
                                    
                                    # Direct match
                                    if pkg_name.lower() in [p.lower() for p in relevant_packages]:
                                        pkg_matches_relevant = True
                                    
                                    if pkg_matches_relevant:
                                        # Store using lowercase package name for consistency
                                        package_versions[pkg_name.lower()] = version
            
            return package_versions
            
        except Exception as e:
            self.logger.warning(f"Could not extract package versions from {yaml_file}: {e}")
            return {}
    
    def _add_package_versions_to_name(self, base_name: str, package_versions: Dict[str, str]) -> str:
        """
        Add relevant package versions to environment name
        
        Args:
            base_name: Base environment name
            package_versions: Dictionary of package versions
            
        Returns:
            Name with package versions added
        """
        if not package_versions:
            return base_name
        
        # Sort packages by name for consistent ordering
        sorted_packages = sorted(package_versions.items())
        
        # Add up to 2 most relevant package versions to avoid overly long names
        # But skip packages that are already mentioned in the base name
        added_versions = []
        for pkg_name, version in sorted_packages[:2]:
            # Check if package name (or similar) is already in the base name
            # If it IS in the name, we WANT to add the version (this is the desired behavior)
            # If it's NOT in the name, we skip it (don't add random packages)
            pkg_variations = [
                pkg_name.lower(),
                pkg_name.lower().replace('py', ''),  # harmonypy → harmony
                pkg_name.lower().replace('r-', ''),   # r-seurat → seurat
                pkg_name.lower().split('-')[0],       # sci-kit-learn → sci
            ]
            
            # Check if any variation is in the base name
            package_in_name = False
            for variation in pkg_variations:
                if variation in base_name.lower() and len(variation) > 2:  # Avoid single letters
                    self.logger.debug(f"Adding version for {pkg_name} - variation '{variation}' found in base name: {base_name}")
                    package_in_name = True
                    break
            
            # Only add version if package is mentioned in the environment name
            if not package_in_name:
                self.logger.debug(f"Skipping {pkg_name} - not mentioned in environment name: {base_name}")
                continue
                
            # Clean version to support up to 3 digits (e.g., 1.9.1 → 191)
            # Handle alpha/beta versions (e.g., 2.0a0 → 200a0)
            if 'a' in version or 'b' in version or 'rc' in version or 'dev' in version:
                # For alpha/beta versions, preserve the suffix
                # Split at alpha/beta marker
                version_match = re.match(r'([0-9.]+)([a-zA-Z]+[0-9]*)', version)
                if version_match:
                    numeric_part, suffix = version_match.groups()
                    version_parts = numeric_part.split('.')
                    if len(version_parts) >= 3:
                        clean_version = f"{version_parts[0]}{version_parts[1]}{version_parts[2]}{suffix}"
                    elif len(version_parts) == 2:
                        clean_version = f"{version_parts[0]}{version_parts[1]}{suffix}"
                    else:
                        clean_version = f"{version_parts[0]}{suffix}" if version_parts else f"0{suffix}"
                else:
                    # Fallback to removing only dots for alpha versions
                    clean_version = version.replace('.', '')
            else:
                # Regular version handling
                version_parts = version.split('.')
                if len(version_parts) >= 3:
                    clean_version = f"{version_parts[0]}{version_parts[1]}{version_parts[2]}"
                elif len(version_parts) == 2:
                    clean_version = f"{version_parts[0]}{version_parts[1]}"
                else:
                    clean_version = version_parts[0] if version_parts else "0"
                
                # Remove any non-digit characters for regular versions
                clean_version = re.sub(r'[^\d]', '', clean_version)
            version_suffix = f"{pkg_name}{clean_version}"
            added_versions.append(version_suffix)
        
        if added_versions:
            return f"{base_name}_{'_'.join(added_versions)}"
        
        return base_name
    
    def create_environment_from_yaml(self, yaml_file: Path, new_name: str, log_to_file: bool = True) -> bool:
        """
        Create a new environment from a YAML file
        
        Args:
            yaml_file: Path to the YAML file
            new_name: Name for the new environment
            log_to_file: Whether to log output to a file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, try to modify the YAML to use the new name
            self._update_yaml_name(yaml_file, new_name)
            
            # Use shell command with 'yes |' to handle any potential prompts automatically
            cmd_str = f"yes | {self.cmd_base} env create -f {yaml_file} -n {new_name}"
            
            # Prepare log file if requested
            log_file = None
            if log_to_file:
                log_dir = Path("backup_environments")
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / f"install_{new_name}.log"
                self.logger.info(f"Logging environment creation to {log_file}")
            
            # Use progress version for environment creation (it's slow)
            result = self._run_command_with_progress_shell(
                cmd_str, 
                f"Creating environment '{new_name}'",
                log_file
            )
            
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
    
    def remove_environment(self, env_name: str, log_to_file: bool = True) -> bool:
        """
        Remove an environment
        
        Args:
            env_name: Name of the environment to remove
            log_to_file: Whether to log output to a file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use shell command with 'yes |' to handle any potential prompts automatically
            cmd_str = f"yes | {self.cmd_base} env remove -n {env_name}"
            
            # Prepare log file if requested
            log_file = None
            if log_to_file:
                log_dir = Path("backup_environments")
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / f"remove_{env_name}.log"
                self.logger.info(f"Logging environment removal to {log_file}")
            
            # Use progress version for environment removal (can be slow for large environments)
            result = self._run_command_with_progress_shell(
                cmd_str, 
                f"Removing environment '{env_name}'",
                log_file
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully removed environment {env_name}")
                return True
            else:
                self.logger.error(f"Failed to remove environment {env_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing environment {env_name}: {e}")
            return False
    
    def process_environment(self, env_info: Dict[str, str], all_environments: List[Dict[str, str]]) -> bool:
        """
        Process a single environment: export, reinstall, verify, and cleanup
        
        Args:
            env_info: Dictionary containing environment information
            all_environments: List of all environments for conflict checking
            
        Returns:
            True if all steps successful, False otherwise
        """
        env_name = env_info['name']
        python_version = env_info['python_version']
        r_version = env_info['r_version']
        
        # Get existing names for conflict resolution
        existing_names = [env['name'].lower() for env in all_environments]
        
        self.logger.info(f"\n{Fore.CYAN}=== Processing environment: {env_name} ==={Style.RESET_ALL}")
        
        # Step 1: Export environment
        self.logger.info(f"{Fore.YELLOW}Step 1: Exporting environment...{Style.RESET_ALL}")
        yaml_file = self.export_environment(env_name)
        if not yaml_file:
            self.logger.error(f"Failed to export {env_name}, skipping...")
            return False
        
        # Check if environment is empty
        if yaml_file == "EMPTY":
            self.logger.warning(f"{Fore.YELLOW}Environment '{env_name}' is empty (no meaningful packages).{Style.RESET_ALL}")
            
            # Check if it's a base environment before trying to remove
            env_path = env_info.get('path', '')
            if self._is_base_environment(env_path, env_name):
                self.logger.warning(f"{Fore.YELLOW}'{env_name}' is a base environment and cannot be removed.{Style.RESET_ALL}")
                self.logger.info(f"{Fore.YELLOW}Skipping base environment: {env_name}{Style.RESET_ALL}")
                return True  # Consider this "successful" since we handled it appropriately
            
            self.logger.info(f"{Fore.YELLOW}Removing empty environment: {env_name}{Style.RESET_ALL}")
            
            # Remove the empty environment
            try:
                # Use shell command with 'yes |' for consistency
                cmd_str = f"yes | {self.cmd_base} env remove -n {env_name}"
                result = self._run_command_with_progress_shell(cmd_str, f"Removing empty environment '{env_name}'")
                if result.returncode == 0:
                    self.logger.info(f"{Fore.GREEN}✓ Successfully removed empty environment: {env_name}{Style.RESET_ALL}")
                    return True
                else:
                    self.logger.error(f"Failed to remove empty environment {env_name}: {result.stderr}")
                    return False
            except Exception as e:
                self.logger.error(f"Error removing empty environment {env_name}: {e}")
                return False
        
        # Step 2: Generate new name (now with package version detection)
        # At this point, yaml_file is definitely a Path (not "EMPTY" or None)
        assert isinstance(yaml_file, Path), "yaml_file must be a Path at this point"
        new_name = self.generate_new_name(
            env_name, python_version, r_version, existing_names, yaml_file
        )
        self.logger.info(f"New environment name: {new_name}")
        
        # Show what was cleaned if original had versions
        cleaned_base = self._clean_existing_versions(env_name.lower())
        if cleaned_base != env_name.lower():
            self.logger.info(f"Cleaned base name: {env_name} -> {cleaned_base}")
        
        # Show package versions if detected
        package_count = 0
        if yaml_file and isinstance(yaml_file, Path):
            package_versions = self._extract_package_versions_from_yaml(yaml_file, env_name)
            if package_versions:
                pkg_info = ', '.join([f"{pkg}={ver}" for pkg, ver in package_versions.items()])
                self.logger.info(f"Detected packages: {pkg_info}")
            
            # Count total packages in YAML for progress context
            try:
                import yaml
                with open(yaml_file, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                dependencies = yaml_data.get('dependencies', [])
                
                conda_packages = 0
                pip_packages = 0
                
                for dep in dependencies:
                    if isinstance(dep, str):
                        conda_packages += 1
                    elif isinstance(dep, dict) and 'pip' in dep:
                        pip_packages += len(dep.get('pip', []))
                
                package_count = conda_packages + pip_packages
                self.logger.info(f"Environment contains {conda_packages} conda packages" + 
                               (f" and {pip_packages} pip packages" if pip_packages > 0 else ""))
            except:
                pass
        
        # Step 3: Create new environment
        step_info = f"Step 2: Creating new environment"
        if package_count > 0:
            step_info += f" ({package_count} packages)"
        self.logger.info(f"{Fore.YELLOW}{step_info}...{Style.RESET_ALL}")
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
        existing_names = [env['name'].lower() for env in environments]
        
        for i, env in enumerate(environments, 1):
            python_ver = env['python_version'] or 'Unknown'
            r_ver = env['r_version'] or 'None'
            
            # Quick export for package detection (for display only)
            temp_yaml = None
            try:
                exported_result = self.export_environment(env['name'])
                if exported_result == "EMPTY":
                    # Environment is empty, skip package detection
                    temp_yaml = None
                elif isinstance(exported_result, Path):
                    temp_yaml = exported_result
            except:
                pass  # Continue without package detection if export fails
            
            new_name = self.generate_new_name(
                env['name'], env['python_version'], env['r_version'], existing_names, temp_yaml
            )
            
            # Show if name will be cleaned
            cleaned_base = self._clean_existing_versions(env['name'].lower())
            name_info = env['name']
            if cleaned_base != env['name'].lower():
                name_info += f" (cleaned: {cleaned_base})"
            
            print(f"{i:2}. {name_info}")
            print(f"    Python: {python_ver}, R: {r_ver}")
            
            # Show package versions if detected
            if temp_yaml and isinstance(temp_yaml, Path):
                package_versions = self._extract_package_versions_from_yaml(temp_yaml, env['name'])
                if package_versions:
                    pkg_info = ', '.join([f"{pkg}={ver}" for pkg, ver in list(package_versions.items())[:2]])
                    print(f"    📦 Key packages: {pkg_info}")
            
            print(f"    → {new_name}")
            if new_name.endswith('_v1') or '_v' in new_name.split('_')[-1]:
                print(f"    {Fore.YELLOW}⚠ Conflict resolved with version suffix{Style.RESET_ALL}")
            print()
        
        print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print("1. Process all environments")
        print("2. Select specific environments")  
        print("3. Preview mode (show changes without processing)")
        print("4. Analyze exported YAML files")
        print("5. Clean up YAML files")
        print("6. Recreate Jupyter kernels")
        print("7. Clone environment (conda-pack or YAML)")
        print("8. Debug environment failures")
        print("9. Analyze log failures")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == "1":
            self._process_all_environments(environments)
        elif choice == "2":
            self._process_selected_environments(environments)
        elif choice == "3":
            self._preview_changes(environments)
        elif choice == "4":
            self._handle_yaml_analysis()
        elif choice == "5":
            self._handle_yaml_cleanup()
        elif choice == "6":
            self._handle_kernel_recreation(environments)
        elif choice == "7":
            self._handle_environment_cloning(environments)
        elif choice == "8":
            self._handle_environment_debugging()
        elif choice == "9":
            self._handle_log_analysis()
        elif choice == "10":
            print("Exiting...")
            return
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")

    def _handle_kernel_recreation(self, environments: List[Dict[str, str]]):
        """Handle kernel recreation with options for all or selected environments"""
        print(f"\n{Fore.CYAN}=== Recreate Jupyter Kernels ==={Style.RESET_ALL}")
        print("1. Recreate kernels for all environments")
        print("2. Select specific environments")
        print("3. Back to main menu")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            self.recreate_jupyter_kernels()
        elif choice == "2":
            # Show environments with Python/R
            valid_envs = []
            print(f"\n{Fore.CYAN}Environments with Python or R:{Style.RESET_ALL}")
            for i, env in enumerate(environments, 1):
                if env['name'] in ['base', 'root']:
                    continue
                    
                has_python = self._environment_has_python(env['path'])
                has_r = self._environment_has_r(env['path'])
                
                if has_python or has_r:
                    valid_envs.append(env)
                    kernels = []
                    if has_python:
                        kernels.append("Python")
                    if has_r:
                        kernels.append("R")
                    print(f"{len(valid_envs):2}. {env['name']} ({', '.join(kernels)})")
            
            if not valid_envs:
                print(f"{Fore.YELLOW}No environments with Python or R kernels found{Style.RESET_ALL}")
                return
            
            try:
                selection = input(f"\nEnter environment numbers to process (e.g., 1,3-5 or 'all'): ").strip()
                
                if selection.lower() == 'all':
                    selected_envs = [env['name'] for env in valid_envs]
                else:
                    indices = self._parse_selection(selection, len(valid_envs))
                    selected_envs = [valid_envs[i-1]['name'] for i in indices]
                
                self.recreate_jupyter_kernels(selected_envs)
                
            except (ValueError, IndexError) as e:
                print(f"{Fore.RED}Invalid selection: {e}{Style.RESET_ALL}")
        elif choice == "3":
            return
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")

    def _handle_yaml_analysis(self):
        """Handle YAML analysis menu"""
        print(f"\n{Fore.CYAN}=== YAML File Analysis ==={Style.RESET_ALL}")
        self.analyze_and_cleanup_yaml_files("analyze")

    def _handle_yaml_cleanup(self):
        """Handle YAML cleanup with options"""
        print(f"\n{Fore.CYAN}=== YAML File Cleanup ==={Style.RESET_ALL}")
        print("1. Analyze files first (recommended)")
        print("2. Clean up duplicates (keep newest)")
        print("3. Clean up environment duplicates (keep latest per environment)")
        print("4. Remove all YAML files")
        print("5. Back to main menu")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            self.analyze_and_cleanup_yaml_files("analyze")
        elif choice == "2":
            self.analyze_and_cleanup_yaml_files("cleanup_duplicates")
        elif choice == "3":
            self.analyze_and_cleanup_yaml_files("cleanup_env_duplicates")
        elif choice == "4":
            self.analyze_and_cleanup_yaml_files("cleanup_all")
        elif choice == "5":
            return
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
    
    def _preview_changes(self, environments: List[Dict[str, str]]):
        """Preview what changes would be made without actually processing"""
        print(f"\n{Fore.CYAN}=== Preview Mode - No Changes Will Be Made ==={Style.RESET_ALL}")
        
        existing_names = [env['name'].lower() for env in environments]
        
        print(f"\nAnalyzing {len(environments)} environments:\n")
        
        unchanged = 0
        renamed = 0
        conflicts = 0
        
        for env in environments:
            env_name = env['name']
            
            # Export temporarily for package version detection in preview
            exported_result = self.export_environment(env_name)
            temp_yaml = None
            
            if exported_result == "EMPTY":
                print(f"📁 {env_name} (EMPTY - will be removed)")
                continue
            elif isinstance(exported_result, Path):
                temp_yaml = exported_result
            
            new_name = self.generate_new_name(
                env_name, 
                env['python_version'], 
                env['r_version'], 
                existing_names,
                temp_yaml
            )
            
            print(f"📁 {env_name}")
            
            # Show version info
            py_ver = env['python_version'] or 'Not detected'
            r_ver = env['r_version'] or 'Not detected'
            print(f"   Python: {py_ver}, R: {r_ver}")
            
            # Show package versions if detected
            if temp_yaml and isinstance(temp_yaml, Path):
                package_versions = self._extract_package_versions_from_yaml(temp_yaml, env_name)
                if package_versions:
                    pkg_info = ', '.join([f"{pkg}={ver}" for pkg, ver in package_versions.items()])
                    print(f"   📦 Packages: {pkg_info}")
            
            # Show cleaning info
            cleaned_base = self._clean_existing_versions(env_name.lower())
            if cleaned_base != env_name.lower():
                print(f"   🧹 Will clean: {env_name} → {cleaned_base}")
            
            # Show final result
            if new_name == env_name.lower():
                print(f"   ✅ No change needed")
                unchanged += 1
            else:
                print(f"   ➡️  Will rename to: {new_name}")
                renamed += 1
                
                if '_v' in new_name.split('_')[-1]:
                    print(f"   ⚠️  Conflict resolved with version suffix")
                    conflicts += 1
            
            print()
        
        # Summary
        print(f"{Fore.CYAN}=== Preview Summary ==={Style.RESET_ALL}")
        print(f"Total environments: {len(environments)}")
        print(f"No changes needed: {unchanged}")
        print(f"Will be renamed: {renamed}")
        print(f"Conflicts resolved: {conflicts}")
        
        if renamed > 0:
            print(f"\n{Fore.YELLOW}Would you like to proceed with processing? (y/n): {Style.RESET_ALL}", end="")
            confirm = input().strip().lower()
            if confirm in ['y', 'yes']:
                print("\nChoose processing mode:")
                print("1. Process all")
                print("2. Select specific environments")
                
                mode_choice = input("Enter choice (1-2): ").strip()
                if mode_choice == "1":
                    self._process_all_environments(environments)
                elif mode_choice == "2":
                    self._process_selected_environments(environments)
            else:
                print("Preview completed. No changes made.")
    
    def _process_all_environments(self, environments: List[Dict[str, str]]):
        """Process all environments"""
        print(f"\n{Fore.YELLOW}Processing all {len(environments)} environments...{Style.RESET_ALL}")
        
        successful = 0
        failed = 0
        
        for env in environments:
            if self.process_environment(env, environments):
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
                if self.process_environment(env, environments):
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

    def analyze_and_cleanup_yaml_files(self, action: str = "analyze") -> bool:
        """
        Analyze YAML files and optionally clean them up
        
        Args:
            action: What to do - "analyze", "cleanup_duplicates", "cleanup_env_duplicates", "cleanup_all"
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            analyzer = YAMLAnalyzer(self.export_dir)
            analysis = analyzer.analyze_yaml_files()
            
            if analysis['total_files'] == 0:
                print(f"{Fore.YELLOW}No YAML files found in {self.export_dir}{Style.RESET_ALL}")
                return True
            
            # Always show the analysis first
            analyzer.print_analysis_report(analysis)
            
            if action == "analyze":
                return True
            elif action == "cleanup_duplicates":
                if analysis['duplicates']:
                    removed = analyzer.cleanup_duplicates(analysis, "keep_newest")
                    print(f"{Fore.GREEN}✅ Removed {removed} duplicate files{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}No duplicate files found{Style.RESET_ALL}")
                return True
            elif action == "cleanup_env_duplicates":
                removed = analyzer.cleanup_by_environment(analysis, keep_latest=True)
                if removed > 0:
                    print(f"{Fore.GREEN}✅ Removed {removed} environment duplicate files{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}No environment duplicates found{Style.RESET_ALL}")
                return True
            elif action == "cleanup_all":
                removed = analyzer.cleanup_all_files(confirm=True)
                print(f"{Fore.GREEN}✅ Removed {removed} files{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Unknown action: {action}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error during YAML analysis: {e}{Style.RESET_ALL}")
            self.logger.error(f"Error during YAML analysis: {e}")
            return False

    def cleanup_exported_yaml_files(self, confirm: bool = True) -> bool:
        """
        Legacy function - now redirects to the YAML analyzer
        
        Args:
            confirm: Whether to ask for confirmation before deletion
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            analyzer = YAMLAnalyzer(self.export_dir)
            removed = analyzer.cleanup_all_files(confirm=confirm)
            self.logger.info(f"Cleanup completed: deleted {removed} YAML files")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error during cleanup: {e}{Style.RESET_ALL}")
            self.logger.error(f"Error during YAML cleanup: {e}")
            return False

    def recreate_jupyter_kernels(self, target_envs: Optional[List[str]] = None) -> bool:
        """
        Recreate Jupyter kernels for environments that have Python or R
        
        Args:
            target_envs: List of specific environment names to process (None for all)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"\n🔬 Recreating Jupyter kernels for environments...")
            
            # Get all environments
            environments = self.list_environments()
            if target_envs:
                environments = [env for env in environments if env['name'] in target_envs]
            
            success_count = 0
            total_count = 0
            
            for env_info in environments:
                env_name = env_info['name']
                env_path = env_info['path']
                
                # Skip base environment
                if env_name in ['base', 'root']:
                    continue
                
                # Check if environment has Python or R
                has_python = self._environment_has_python(env_path)
                has_r = self._environment_has_r(env_path)
                
                if not has_python and not has_r:
                    continue
                
                total_count += 1
                print(f"\n📦 Processing environment: {env_name}")
                
                # Handle Python kernel
                if has_python:
                    if self._recreate_python_kernel(env_name, env_path):
                        print(f"  ✅ Python kernel recreated for {env_name}")
                        success_count += 1
                    else:
                        print(f"  ❌ Failed to recreate Python kernel for {env_name}")
                
                # Handle R kernel  
                if has_r:
                    if self._recreate_r_kernel(env_name, env_path):
                        print(f"  ✅ R kernel recreated for {env_name}")
                        success_count += 1
                    else:
                        print(f"  ❌ Failed to recreate R kernel for {env_name}")
            
            if total_count == 0:
                print(f"{Fore.YELLOW}No environments with Python or R kernels found{Style.RESET_ALL}")
                return True
            
            print(f"\n{Fore.GREEN}✅ Kernel recreation completed: {success_count}/{total_count} successful{Style.RESET_ALL}")
            self.logger.info(f"Kernel recreation completed: {success_count}/{total_count} successful")
            return success_count > 0
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error recreating kernels: {e}{Style.RESET_ALL}")
            self.logger.error(f"Error recreating kernels: {e}")
            return False

    def _environment_has_python(self, env_path: str) -> bool:
        """Check if environment has Python installed"""
        python_paths = [
            Path(env_path) / "bin" / "python",
            Path(env_path) / "bin" / "python3",
            Path(env_path) / "Scripts" / "python.exe",  # Windows
        ]
        return any(path.exists() for path in python_paths)

    def _environment_has_r(self, env_path: str) -> bool:
        """Check if environment has R installed"""
        r_paths = [
            Path(env_path) / "bin" / "R",
            Path(env_path) / "Scripts" / "R.exe",  # Windows
        ]
        return any(path.exists() for path in r_paths)

    def _recreate_python_kernel(self, env_name: str, env_path: str) -> bool:
        """Recreate Python kernel for an environment"""
        try:
            # Find Python executable
            python_paths = [
                Path(env_path) / "bin" / "python",
                Path(env_path) / "bin" / "python3",
                Path(env_path) / "Scripts" / "python.exe",  # Windows
            ]
            
            python_exe = None
            for path in python_paths:
                if path.exists():
                    python_exe = str(path)
                    break
            
            if not python_exe:
                self.logger.error(f"No Python executable found in {env_path}")
                return False
            
            # Get kernel directory
            kernel_dir = self._get_kernel_dir(env_name)
            
            # Check if kernel already exists and read existing config
            kernel_json_path = kernel_dir / "kernel.json"
            existing_config = {}
            
            if kernel_json_path.exists():
                try:
                    with open(kernel_json_path, 'r') as f:
                        existing_config = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Could not read existing kernel config: {e}")
            
            # Create kernel directory
            kernel_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare kernel configuration, preserving existing settings but updating path
            kernel_config = {
                "argv": [python_exe, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": existing_config.get("display_name", f"Python ({env_name})"),
                "language": "python",
                "metadata": existing_config.get("metadata", {"debugger": True})
            }
            
            # Preserve any additional fields from existing config
            for key, value in existing_config.items():
                if key not in kernel_config:
                    kernel_config[key] = value
            
            # Write kernel configuration
            with open(kernel_json_path, 'w') as f:
                json.dump(kernel_config, f, indent=2)
            
            self.logger.info(f"Recreated Python kernel for {env_name} at {kernel_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recreating Python kernel for {env_name}: {e}")
            return False

    def _recreate_r_kernel(self, env_name: str, env_path: str) -> bool:
        """Recreate R kernel for an environment"""
        try:
            # Find R executable
            r_paths = [
                Path(env_path) / "bin" / "R",
                Path(env_path) / "Scripts" / "R.exe",  # Windows
            ]
            
            r_exe = None
            for path in r_paths:
                if path.exists():
                    r_exe = str(path)
                    break
            
            if not r_exe:
                self.logger.error(f"No R executable found in {env_path}")
                return False
            
            # Get kernel directory
            kernel_dir = self._get_kernel_dir(f"ir_{env_name}")
            
            # Check if kernel already exists and read existing config
            kernel_json_path = kernel_dir / "kernel.json"
            existing_config = {}
            
            if kernel_json_path.exists():
                try:
                    with open(kernel_json_path, 'r') as f:
                        existing_config = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Could not read existing kernel config: {e}")
            
            # Create kernel directory
            kernel_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare kernel configuration, preserving existing settings but updating path
            kernel_config = {
                "argv": [r_exe, "--slave", "-e", "IRkernel::main()", "--args", "{connection_file}"],
                "display_name": existing_config.get("display_name", f"R ({env_name})"),
                "language": "R",
                "metadata": existing_config.get("metadata", {})
            }
            
            # Preserve any additional fields from existing config
            for key, value in existing_config.items():
                if key not in kernel_config:
                    kernel_config[key] = value
            
            # Write kernel configuration
            with open(kernel_json_path, 'w') as f:
                json.dump(kernel_config, f, indent=2)
            
            self.logger.info(f"Recreated R kernel for {env_name} at {kernel_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recreating R kernel for {env_name}: {e}")
            return False

    def _get_kernel_dir(self, kernel_name: str) -> Path:
        """Get the kernel directory path for a given kernel name"""
        # Try different possible kernel directories
        possible_dirs = [
            Path.home() / ".local" / "share" / "jupyter" / "kernels" / kernel_name,
            Path.home() / "Library" / "Jupyter" / "kernels" / kernel_name,  # macOS
            Path("/usr/local/share/jupyter/kernels") / kernel_name,
        ]
        
        # Use the first existing parent directory, or default to user local
        for directory in possible_dirs:
            if directory.parent.exists():
                return directory
        
        # Default to user local directory
        return possible_dirs[0]

    def _handle_environment_cloning(self, environments: List[Dict[str, str]]):
        """Handle environment cloning with conda-pack or YAML"""
        if EnvironmentCloner is None:
            print(f"{Fore.RED}Environment cloner not available. Check utils/environment_cloner.py{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}=== Clone Environment ==={Style.RESET_ALL}")
        
        # Show available environments
        print("Available environments:")
        for i, env in enumerate(environments, 1):
            print(f"{i:2}. {env['name']} (Python: {env['python_version'] or 'Unknown'})")
        
        # Get user input
        try:
            choice = input("\nEnter environment number to clone: ").strip()
            env_index = int(choice) - 1
            
            if env_index < 0 or env_index >= len(environments):
                print(f"{Fore.RED}Invalid selection!{Style.RESET_ALL}")
                return
            
            source_env = environments[env_index]['name']
            
        except ValueError:
            # Maybe they entered an environment name directly
            source_env = choice
            if not any(env['name'] == source_env for env in environments):
                print(f"{Fore.RED}Environment '{source_env}' not found!{Style.RESET_ALL}")
                return
        
        # Get new name
        new_name = input(f"Enter new environment name (or 'auto' for smart naming): ").strip()
        if not new_name:
            new_name = "auto"
        
        # Choose method
        print("\nCloning methods:")
        print("1. conda-pack (recommended - exact replication)")
        print("2. YAML export/import (cross-platform compatible)")
        print("3. Auto (conda-pack if available, otherwise YAML)")
        
        method_choice = input("Choose method (1-3): ").strip()
        method_map = {"1": "conda-pack", "2": "yaml", "3": "auto"}
        method = method_map.get(method_choice, "auto")
        
        try:
            cloner = EnvironmentCloner()
            result = cloner.clone_environment(source_env, new_name, method)
            print(f"{Fore.GREEN}✅ Clone completed: {result}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Clone failed: {e}{Style.RESET_ALL}")
            self.logger.error(f"Environment clone failed: {e}")

    def _handle_environment_debugging(self):
        """Handle environment-specific debugging"""
        if debug_environment_failure is None:
            print(f"{Fore.RED}Debug function not available. Check utils/simple_log_analyzer.py{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}=== Debug Environment Failures ==={Style.RESET_ALL}")
        
        env_name = input("Enter environment name to debug: ").strip()
        if not env_name:
            print(f"{Fore.RED}Please enter an environment name{Style.RESET_ALL}")
            return
        
        try:
            debug_environment_failure(env_name, self.log_file)
        except Exception as e:
            print(f"{Fore.RED}❌ Debug failed: {e}{Style.RESET_ALL}")

    def _handle_log_analysis(self):
        """Handle general log analysis"""
        if analyze_failures is None:
            print(f"{Fore.RED}Analysis function not available. Check utils/simple_log_analyzer.py{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}=== Analyze All Log Failures ==={Style.RESET_ALL}")
        
        try:
            analyze_failures(self.log_file)
        except Exception as e:
            print(f"{Fore.RED}❌ Analysis failed: {e}{Style.RESET_ALL}")


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
