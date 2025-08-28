#!/usr/bin/env python3
"""
Environment Cloner Tool

Clones conda environments using conda-pack for portable deployment or YAML export.
Supports both direct cloning and YAML-based recreation with smart naming.
"""

import os
import sys
import json
import subprocess
import tarfile
import tempfile
import shutil
import re
from pathlib import Path

class EnvironmentCloner:
    def __init__(self):
        self.conda_cmd = self._detect_conda_command()
        self.conda_pack_available = self._check_conda_pack()
    
    def _detect_conda_command(self):
        """Detect available conda command (mamba preferred)."""
        for cmd in ['mamba', 'conda']:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        raise RuntimeError("Neither mamba nor conda found in PATH")
    
    def _check_conda_pack(self):
        """Check if conda-pack is available."""
        try:
            result = subprocess.run([self.conda_cmd, 'list', 'conda-pack'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and 'conda-pack' in result.stdout:
                return True
            else:
                print("[WARNING] conda-pack not found. Install with: conda install conda-pack")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARNING] conda-pack not found. Install with: conda install conda-pack")
            return False
    
    def _get_environment_info(self, env_identifier):
        """Get environment information (name, path, python version, packages)."""
        # Check if it's a path or name
        if os.path.exists(env_identifier):
            env_path = env_identifier
            env_name = os.path.basename(env_path)
        else:
            env_name = env_identifier
            # Get environment path
            try:
                result = subprocess.run([self.conda_cmd, 'env', 'list', '--json'], 
                                      capture_output=True, text=True, check=True)
                env_data = json.loads(result.stdout)
                
                env_path = None
                for path in env_data['envs']:
                    if os.path.basename(path) == env_name:
                        env_path = path
                        break
                
                if not env_path:
                    raise ValueError(f"Environment '{env_name}' not found")
                    
            except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
                raise ValueError(f"Failed to get environment info: {e}")
        
        # Validate environment exists
        if not os.path.exists(env_path):
            raise ValueError(f"Environment path does not exist: {env_path}")
        
        # Get package list for version detection
        try:
            result = subprocess.run(
                [self.conda_cmd, 'list', '-p', env_path],
                capture_output=True, text=True, check=True
            )
            packages = result.stdout
        except subprocess.CalledProcessError:
            packages = ""
        
        # Detect Python version
        python_version = None
        r_version = None
        
        for line in packages.split('\n'):
            if line.startswith('python '):
                match = re.search(r'python\s+(\d+\.\d+)', line)
                if match:
                    python_version = match.group(1)
            elif line.startswith('r-base '):
                match = re.search(r'r-base\s+(\d+\.\d+)', line)
                if match:
                    r_version = match.group(1)
        
        return {
            'name': env_name,
            'path': env_path,
            'python_version': python_version,
            'r_version': r_version,
            'packages': packages
        }
    
    def _generate_new_name(self, old_name, new_name_input):
        """Generate new environment name using naming scheme."""
        if new_name_input and new_name_input != "auto":
            return new_name_input
        
        # Auto-generate name with lowercase and version suffix
        base_name = old_name.lower()
        
        # Get environment info to detect versions
        try:
            env_info = self._get_environment_info(old_name)
            
            # Add version suffixes
            if env_info['python_version']:
                py_ver = env_info['python_version'].replace('.', '')
                base_name += f"_py{py_ver}"
            
            if env_info['r_version']:
                r_ver = env_info['r_version'].split('.')[0]  # Major version only
                base_name += f"_r{r_ver}"
            
        except Exception:
            # If we can't get version info, just use the base name
            pass
        
        return base_name
    
    def _get_conda_envs_directory(self):
        """Get the conda/mamba environments directory using multiple detection methods."""
        
        # Method 1: Try to get from conda info (most reliable)
        try:
            result = subprocess.run([self.conda_cmd, 'info', '--json'], 
                                  capture_output=True, text=True, check=True)
            info_data = json.loads(result.stdout)
            
            # Get the first environment directory that exists
            for envs_dir in info_data.get('envs_dirs', []):
                if os.path.exists(envs_dir):
                    return envs_dir
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            pass  # Silent fallback to next method
        
        # Method 2: Get from existing environments list
        try:
            result = subprocess.run([self.conda_cmd, 'env', 'list', '--json'], 
                                  capture_output=True, text=True, check=True)
            env_data = json.loads(result.stdout)
            
            # Find the common parent directory of all environments
            if env_data.get('envs'):
                # Look for environments that end with /envs/<name> pattern
                for env_path in env_data['envs']:
                    if '/envs/' in env_path:
                        # Extract the envs directory
                        envs_dir = env_path.split('/envs/')[0] + '/envs'
                        if os.path.exists(envs_dir):
                            return envs_dir
                
                # Fallback: use parent of first environment
                first_env = env_data['envs'][0]
                if os.path.basename(os.path.dirname(first_env)) == 'envs':
                    envs_dir = os.path.dirname(first_env)
                    return envs_dir
                else:
                    # Create envs subdirectory in the conda root
                    conda_root = os.path.dirname(first_env)
                    envs_dir = os.path.join(conda_root, 'envs')
                    os.makedirs(envs_dir, exist_ok=True)
                    return envs_dir
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            pass  # Silent fallback to next method
        
        # Method 3: Use CONDA_PREFIX environment variable
        try:
            conda_prefix = os.environ.get('CONDA_PREFIX')
            if conda_prefix:
                # If we're in base environment, envs should be in conda_prefix/envs
                if conda_prefix.endswith('/base') or os.path.basename(conda_prefix) == 'miniforge3':
                    envs_dir = os.path.join(conda_prefix, 'envs')
                else:
                    # We're in a specific environment, go up to find envs
                    if '/envs/' in conda_prefix:
                        envs_dir = conda_prefix.split('/envs/')[0] + '/envs'
                    else:
                        envs_dir = os.path.join(os.path.dirname(conda_prefix), 'envs')
                
                if os.path.exists(envs_dir):
                    return envs_dir
                else:
                    os.makedirs(envs_dir, exist_ok=True)
                    return envs_dir
                    
        except Exception as e:
            pass  # Silent fallback to next method
        
        # Method 4: Last resort - use current directory
        fallback_dir = os.path.join(os.getcwd(), 'envs')
        print(f"[WARNING] Could not detect conda envs directory, using fallback: {fallback_dir}")
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir
    
    def clone_with_conda_pack(self, old_env, new_name="auto", output_dir="./cloned_environments"):
        """Clone environment using conda-pack (recommended for exact replication)."""
        
        if not self.conda_pack_available:
            raise RuntimeError("conda-pack is required for this method. Install with: conda install conda-pack")
        
        print("[INFO] Cloning environment with conda-pack...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info['name'], new_name)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        archive_path = os.path.join(output_dir, f"{final_name}.tar.gz")
        
        print(f"[PACK] Packing {env_info['name']} -> {archive_path}")
        
        # Pack the environment
        try:
            subprocess.run([
                'conda', 'pack',
                '-p', env_info['path'],
                '-o', archive_path
            ], check=True)
            
            print("[SUCCESS] Environment packed successfully!")
            print(f"[FILE] Archive: {archive_path}")
            
            # Ask user if they want to unpack it now
            unpack_now = input(f"\n[?] Unpack environment '{final_name}' to conda environments now? (Y/n): ").strip().lower()
            
            if unpack_now in ['', 'y', 'yes']:
                print(f"[UNPACK] Unpacking environment to conda environments...")
                
                # Get conda environments directory using robust method
                try:
                    envs_dir = self._get_conda_envs_directory()
                    print(f"[INFO] Installing to conda envs directory: {envs_dir}")
                    
                    # Create target environment directory
                    target_env_path = os.path.join(envs_dir, final_name)
                    os.makedirs(target_env_path, exist_ok=True)
                    
                    # Unpack the archive
                    with tarfile.open(archive_path, 'r:gz') as tar:
                        tar.extractall(path=target_env_path)
                    
                    print(f"[SUCCESS] Environment unpacked to: {target_env_path}")
                    
                    # Run conda-unpack to finalize the environment
                    print("[FINALIZE] Running conda-unpack...")
                    conda_unpack_path = os.path.join(target_env_path, 'bin', 'conda-unpack')
                    if os.path.exists(conda_unpack_path):
                        subprocess.run([conda_unpack_path], check=True, cwd=target_env_path)
                        print(f"[SUCCESS] Environment '{final_name}' ready for use!")
                        print(f"[ACTIVATE] conda activate {final_name}")
                    else:
                        print("[WARNING] conda-unpack not found in environment, but unpacking completed")
                    
                    return target_env_path
                    
                except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, tarfile.TarError) as e:
                    print(f"[WARNING] Failed to unpack automatically: {e}")
                    print(f"[TIP] You can manually unpack with:")
                    print(f"   mkdir -p <conda_envs>/{final_name}")
                    print(f"   tar -xzf {archive_path} -C <conda_envs>/{final_name}")
                    print(f"   <conda_envs>/{final_name}/bin/conda-unpack")
                    return archive_path
            else:
                print(f"\n[TIP] To deploy manually:")
                print(f"   mkdir -p <target_path>/{final_name}")
                print(f"   tar -xzf {archive_path} -C <target_path>/{final_name}")
                print(f"   <target_path>/{final_name}/bin/conda-unpack")
                print(f"   conda activate {final_name}")
            
            return archive_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"conda-pack failed: {e}")
    
    def clone_with_yaml(self, old_env, new_name="auto", output_dir="./exported_environments"):
        """Clone environment using YAML export/import (cross-platform compatible)."""
        
        print(f"[YAML] Cloning environment with YAML...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info['name'], new_name)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, f"{final_name}.yml")
        
        print(f"[EXPORT] Exporting {env_info['name']} -> {yaml_path}")
        
        # Export environment to YAML
        try:
            with open(yaml_path, 'w') as f:
                subprocess.run([
                    self.conda_cmd, 'env', 'export',
                    '-p', env_info['path'],
                    '--no-builds'  # Remove build strings for better compatibility
                ], stdout=f, check=True)
            
            # Update name in YAML file
            with open(yaml_path, 'r') as f:
                content = f.read()
            
            content = re.sub(r'^name:.*$', f'name: {final_name}', content, flags=re.MULTILINE)
            
            with open(yaml_path, 'w') as f:
                f.write(content)
            
            print("[SUCCESS] YAML exported successfully!")
            print(f"[FILE] YAML file: {yaml_path}")
            
            # Optionally create the environment immediately
            create_now = input(f"\n[?] Create environment '{final_name}' now? (y/N): ").strip().lower()
            
            if create_now == 'y':
                print(f"[CREATE] Creating environment {final_name}...")
                try:
                    subprocess.run([
                        self.conda_cmd, 'env', 'create',
                        '-f', yaml_path
                    ], check=True)
                    print(f"[SUCCESS] Environment '{final_name}' created successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"[FAIL] Failed to create environment: {e}")
                    print(f"[TIP] You can try later with: {self.conda_cmd} env create -f {yaml_path}")
            
            return yaml_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"YAML export failed: {e}")
    
    def clone_environment(self, old_env, new_name="auto", method="auto", output_dir=None):
        """
        Clone an environment using the best available method.
        
        Args:
            old_env: Environment name or path
            new_name: New environment name ("auto" for smart naming)
            method: "conda-pack", "yaml", or "auto"
            output_dir: Output directory (method-specific default if None)
        """
        
        print(f"[ANALYZE] Analyzing environment: {old_env}")
        
        # Validate environment exists
        try:
            env_info = self._get_environment_info(old_env)
            print(f"[SUCCESS] Found environment: {env_info['name']}")
            if env_info['python_version']:
                print(f"[PYTHON] Python: {env_info['python_version']}")
            if env_info['r_version']:
                print(f"[R] R: {env_info['r_version']}")
        except Exception as e:
            raise RuntimeError(f"Environment validation failed: {e}")
        
        # Determine method
        if method == "auto":
            method = "conda-pack" if self.conda_pack_available else "yaml"
            print(f"[AUTO] Auto-selected method: {method}")
        
        # Set default output directory
        if output_dir is None:
            output_dir = "./cloned_environments" if method == "conda-pack" else "./exported_environments"
        
        # Execute cloning
        if method == "conda-pack":
            return self.clone_with_conda_pack(old_env, new_name, output_dir)
        elif method == "yaml":
            return self.clone_with_yaml(old_env, new_name, output_dir)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def unpack_archive(self, archive_path, new_name="auto"):
        """Unpack a conda-pack archive to the conda environments directory with smart naming."""
        
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        # Extract the original environment name from archive filename
        archive_basename = os.path.splitext(os.path.splitext(os.path.basename(archive_path))[0])[0]
        
        # Try to extract environment info from the archive for smart naming
        print(f"[ANALYZE] Analyzing archive: {archive_path}")
        
        # Create a temporary environment info structure for naming
        env_info = {
            'name': archive_basename,
            'python_version': None,
            'r_version': None,
            'path': archive_path  # Using archive path as reference
        }
        
        # Try to detect Python/R versions from the archive name or contents
        try:
            # Look for version patterns in the filename
            if '_py' in archive_basename:
                # Extract Python version (e.g., py311 -> 3.11)
                py_match = re.search(r'_py(\d+)', archive_basename)
                if py_match:
                    py_digits = py_match.group(1)
                    if len(py_digits) >= 3:
                        major = py_digits[0]
                        minor = py_digits[1:]
                        env_info['python_version'] = f"{major}.{minor}"
            
            if '_r' in archive_basename:
                # Extract R version
                r_match = re.search(r'_r(\d+)', archive_basename)
                if r_match:
                    env_info['r_version'] = r_match.group(1)
            
        except Exception:
            pass  # If version detection fails, continue without versions
        
        # Generate final name using the same logic as other methods
        final_name = self._generate_new_name(env_info['name'], new_name)
        
        print(f"[UNPACK] Unpacking {archive_path} as '{final_name}'...")
        if env_info['python_version']:
            print(f"[PYTHON] Detected Python: {env_info['python_version']}")
        if env_info['r_version']:
            print(f"[R] Detected R: {env_info['r_version']}")
        
        try:
            # Get conda environments directory using multiple methods
            envs_dir = self._get_conda_envs_directory()
            
            print(f"[INFO] Installing to conda envs directory: {envs_dir}")
            
            # Create target environment directory
            target_env_path = os.path.join(envs_dir, final_name)
            
            # Check if environment already exists
            if os.path.exists(target_env_path):
                overwrite = input(f"[WARNING] Environment '{final_name}' already exists. Overwrite? (y/N): ").strip().lower()
                if overwrite not in ['y', 'yes']:
                    print("[CANCELLED] Unpacking cancelled.")
                    return None
                
                # Remove existing environment
                import shutil
                shutil.rmtree(target_env_path)
            
            os.makedirs(target_env_path, exist_ok=True)
            
            # Unpack the archive
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=target_env_path)
            
            print(f"[SUCCESS] Environment unpacked to: {target_env_path}")
            
            # Run conda-unpack to finalize the environment
            print("[FINALIZE] Running conda-unpack...")
            conda_unpack_path = os.path.join(target_env_path, 'bin', 'conda-unpack')
            if os.path.exists(conda_unpack_path):
                subprocess.run([conda_unpack_path], check=True, cwd=target_env_path)
                print(f"[SUCCESS] Environment '{final_name}' ready for use!")
                print(f"[ACTIVATE] conda activate {final_name}")
            else:
                print("[WARNING] conda-unpack not found in environment, but unpacking completed")
            
            return target_env_path
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, tarfile.TarError) as e:
            raise RuntimeError(f"Failed to unpack archive: {e}")
    
    def list_archives(self, directory="./cloned_environments"):
        """List available conda-pack archives."""
        if not os.path.exists(directory):
            print(f"[INFO] Directory not found: {directory}")
            return []
        
        archives = []
        for file in os.listdir(directory):
            if file.endswith('.tar.gz'):
                archives.append(os.path.join(directory, file))
        
        if archives:
            print(f"[FOUND] Available archives in {directory}:")
            for i, archive in enumerate(archives, 1):
                basename = os.path.basename(archive)
                print(f"   {i}. {basename}")
        else:
            print(f"[INFO] No archives found in {directory}")
        
        return archives

def main():
    """CLI interface for environment cloner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clone conda environments using conda-pack or YAML export"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone an environment")
    clone_parser.add_argument("old_env", help="Source environment name or path")
    clone_parser.add_argument("new_name", nargs="?", default="auto", 
                             help="New environment name (default: auto-generated)")
    clone_parser.add_argument("--method", choices=["conda-pack", "yaml", "auto"], 
                             default="auto", help="Cloning method")
    clone_parser.add_argument("--output-dir", help="Output directory")
    
    # Unpack command
    unpack_parser = subparsers.add_parser("unpack", help="Unpack a conda-pack archive")
    unpack_parser.add_argument("archive", help="Path to .tar.gz archive")
    unpack_parser.add_argument("new_name", nargs="?", default="auto", 
                             help="New environment name (default: auto-generated with version suffixes)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available archives")
    list_parser.add_argument("--directory", default="./cloned_environments", 
                            help="Directory to search for archives")
    
    args = parser.parse_args()
    
    # Handle no command (backward compatibility)
    if not args.command:
        # Old style arguments for backward compatibility
        if len(sys.argv) >= 2:
            # Treat as clone command
            old_env = sys.argv[1]
            new_name = sys.argv[2] if len(sys.argv) > 2 else "auto"
            method = "auto"
            output_dir = None
            
            try:
                cloner = EnvironmentCloner()
                result = cloner.clone_environment(old_env, new_name, method, output_dir)
                print(f"\n[COMPLETE] Clone operation completed: {result}")
            except Exception as e:
                print(f"[FAIL] Error: {e}")
                sys.exit(1)
        else:
            parser.print_help()
        return
    
    try:
        cloner = EnvironmentCloner()
        
        if args.command == "clone":
            result = cloner.clone_environment(
                args.old_env, 
                args.new_name, 
                args.method, 
                args.output_dir
            )
            print(f"\n[COMPLETE] Clone operation completed: {result}")
            
        elif args.command == "unpack":
            result = cloner.unpack_archive(args.archive, args.new_name)
            if result:
                print(f"\n[COMPLETE] Unpack operation completed: {result}")
            
        elif args.command == "list":
            archives = cloner.list_archives(args.directory)
            if archives:
                # Interactive selection
                try:
                    choice = input(f"\n[?] Unpack an archive? Enter number (1-{len(archives)}) or 'n' to skip: ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(archives):
                        selected_archive = archives[int(choice) - 1]
                        result = cloner.unpack_archive(selected_archive)
                        if result:
                            print(f"\n[COMPLETE] Unpack operation completed: {result}")
                except KeyboardInterrupt:
                    print("\n[CANCELLED] Operation cancelled.")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
