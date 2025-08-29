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
import importlib.util
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
        
        # Detect Python version and extract package list
        python_version = None
        r_version = None
        package_list = []
        
        for line in packages.split('\n'):
            if line.strip() and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2:
                    pkg_name = parts[0]
                    pkg_version = parts[1]
                    
                    # Check for Python version
                    if pkg_name == 'python':
                        match = re.search(r'(\d+\.\d+)', pkg_version)
                        if match:
                            python_version = match.group(1)
                    
                    # Check for R version
                    elif pkg_name == 'r-base':
                        match = re.search(r'(\d+\.\d+)', pkg_version)
                        if match:
                            r_version = match.group(1)
                    
                    # Add to package list
                    package_list.append(f"{pkg_name}={pkg_version}")
        
        return {
            'name': env_name,
            'path': env_path,
            'python_version': python_version,
            'r_version': r_version,
            'packages': package_list
        }
    
    def _generate_new_name(self, env_info, new_name_input, interactive=False):
        """Generate new environment name using naming scheme with package detection.
        
        Args:
            env_info (dict): Environment information with versions and packages
            new_name_input (str): User input for naming ('auto', 'original', or custom name)
            interactive (bool): Whether to show interactive naming options
        """
        if new_name_input and new_name_input not in ["auto", "original"]:
            return new_name_input
        
        if new_name_input == "original":
            return env_info['name']
        
        # Auto-generate name with lowercase base
        base_name = env_info['name'].lower()
        
        # Remove common suffixes that shouldn't be in the final name
        suffixes_to_remove = ['_yaml', '_yml', '_export', '_backup', '_clone', '_copy']
        for suffix in suffixes_to_remove:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        
        # Detect key packages for enhanced naming
        key_packages, package_versions = self._detect_key_packages(env_info)
        
        # Build version and package suffixes
        name_parts = [base_name]
        
        # Add Python version
        if env_info.get('python_version'):
            py_ver = env_info['python_version'].replace('.', '')
            version_part = f"py{py_ver}"
            if version_part not in name_parts:
                name_parts.append(version_part)
        
        # Add R version
        if env_info.get('r_version'):
            r_ver = env_info['r_version'].split('.')[0]  # Major version only
            version_part = f"r{r_ver}"
            if version_part not in name_parts:
                name_parts.append(version_part)
        
        # Add key package indicators (avoid duplicates)
        for pkg in key_packages[:2]:  # Limit to top 2 packages to keep name reasonable
            if pkg not in base_name.lower() and pkg not in name_parts:
                name_parts.append(pkg)
        
        auto_name = '_'.join(name_parts)
        
        if interactive:
            # Show detected information and allow modification
            print(f"\n[SMART NAMING] Environment analysis:")
            if env_info.get('python_version'):
                print(f"  Python: {env_info['python_version']}")
            if env_info.get('r_version'):
                print(f"  R: {env_info['r_version']}")
            if package_versions:
                print(f"  Key packages detected:")
                for pkg, version in list(package_versions.items())[:3]:  # Show top 3
                    print(f"    - {pkg}: {version}")
            
            print(f"  Auto-generated name: {auto_name}")
            
            modify = input(f"Use auto-generated name '{auto_name}'? (y/n/edit): ").strip().lower()
            
            if modify == 'n':
                custom_name = input("Enter custom environment name: ").strip()
                return custom_name if custom_name else auto_name
            elif modify == 'edit':
                edited_name = input(f"Edit name (current: {auto_name}): ").strip()
                return edited_name if edited_name else auto_name
        
        return auto_name
    
    def _detect_key_packages(self, env_info):
        """Detect key/important packages in the environment for naming with version support."""
        key_packages = []
        package_versions = {}  # Store original version info for display
        
        # Load user-configurable package indicators
        package_indicators = self._load_package_config()
        
        # Get package list from environment info
        packages = env_info.get('packages', [])
        
        # Parse packages into name-version pairs
        package_dict = {}
        for pkg in packages:
            if '=' in pkg:
                name, version = pkg.split('=', 1)
                package_dict[name.lower().strip()] = version.strip()
            else:
                package_dict[pkg.lower().strip()] = None
        
        # Find matching key packages with version info
        for indicator, config in package_indicators.items():
            pkg_list = config.get('packages', [])
            include_version = config.get('include_version', False)
            version_format = config.get('version_format', 'major.minor')
            
            for pkg in pkg_list:
                if pkg.lower() in package_dict:
                    version = package_dict[pkg.lower()]
                    
                    if include_version and version:
                        formatted_version = self._format_version(version, version_format)
                        if formatted_version:
                            # Store original version for display
                            package_versions[indicator] = version
                            # Use cleaner version format for naming
                            clean_version = formatted_version.replace('.', '')
                            # Handle special cases for cleaner names
                            if clean_version.startswith('00'):
                                # For 0.0.x versions, use the patch number
                                if '.' in formatted_version and formatted_version.count('.') == 2:
                                    patch_version = formatted_version.split('.')[-1]
                                    clean_version = f"0{patch_version}"
                            key_packages.append(f"{indicator}{clean_version}")
                        else:
                            key_packages.append(indicator)
                    else:
                        # Store that package exists but no version included
                        if version:
                            package_versions[indicator] = version
                        key_packages.append(indicator)
                    break
        
        return key_packages, package_versions
    
    def _load_package_config(self):
        """Load package configuration from config file or use defaults."""
        try:
            # Try to load from package_config.py in the parent directory
            import sys
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'package_config.py')
            
            if os.path.exists(config_path):
                # Load the config file
                spec = importlib.util.spec_from_file_location("package_config", config_path)
                if spec and spec.loader:
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    return config_module.package_indicators
        except Exception as e:
            print(f"[DEBUG] Could not load package config: {e}")
        
        # Fallback to default configuration
        return self._get_default_package_config()
    
    def _get_default_package_config(self):
        """Get default package configuration if config file is not available."""
        return {
            'harmony': {
                'packages': ['harmonypy', 'harmony-pytorch', 'harmony'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'scanpy': {
                'packages': ['scanpy'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'seurat': {
                'packages': ['seurat', 'seuratobject'],
                'include_version': True,
                'version_format': 'major'
            },
            'pytorch': {
                'packages': ['torch', 'pytorch'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'tensorflow': {
                'packages': ['tensorflow', 'tensorflow-gpu'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'sklearn': {
                'packages': ['scikit-learn', 'sklearn'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'jupyter': {
                'packages': ['jupyter', 'jupyterlab'],
                'include_version': False,
                'version_format': 'major'
            },
            'pandas': {
                'packages': ['pandas'],
                'include_version': False,
                'version_format': 'major'
            },
            'numpy': {
                'packages': ['numpy'],
                'include_version': False,
                'version_format': 'major'
            },
            'plotly': {
                'packages': ['plotly'],
                'include_version': False,
                'version_format': 'major'
            },
            'streamlit': {
                'packages': ['streamlit'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'dash': {
                'packages': ['dash'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'flask': {
                'packages': ['flask'],
                'include_version': False,
                'version_format': 'major'
            },
            'django': {
                'packages': ['django'],
                'include_version': True,
                'version_format': 'major.minor'
            },
            'fastapi': {
                'packages': ['fastapi'],
                'include_version': True,
                'version_format': 'major.minor'
            },
        }
    
    def _format_version(self, version, version_format):
        """Format version string according to specified format."""
        try:
            # Remove any build information (e.g., "1.8.2+cuda111" -> "1.8.2")
            clean_version = version.split('+')[0].split('-')[0]
            
            # Split version into components
            parts = clean_version.split('.')
            
            if version_format == 'major' and len(parts) >= 1:
                return parts[0]
            elif version_format == 'major.minor' and len(parts) >= 2:
                # Handle special case for 0.0.x versions - use 0.0.patch format
                if parts[0] == '0' and parts[1] == '0' and len(parts) >= 3:
                    return f"0.0.{parts[2]}"
                return f"{parts[0]}.{parts[1]}"
            elif version_format == 'full':
                return clean_version
            else:
                # Default to major.minor if available
                if len(parts) >= 2:
                    # Handle special case for 0.0.x versions
                    if parts[0] == '0' and parts[1] == '0' and len(parts) >= 3:
                        return f"0.0.{parts[2]}"
                    return f"{parts[0]}.{parts[1]}"
                elif len(parts) >= 1:
                    return parts[0]
                
        except Exception:
            pass
        
        return None
    
    def _get_conda_envs_directory(self):
        """Get the conda/mamba environments directory from the active installation."""
        
        # Method 1: Use conda info --json (most reliable)
        try:
            result = subprocess.run([self.conda_cmd, 'info', '--json'], 
                                  capture_output=True, text=True, check=True)
            info_data = json.loads(result.stdout)
            
            # Get envs_dirs from conda info (this shows all configured envs directories)
            envs_dirs = info_data.get('envs_dirs', [])
            if envs_dirs:
                # Use the first (primary) envs directory
                primary_envs_dir = envs_dirs[0]
                if os.path.exists(primary_envs_dir):
                    print(f"[INFO] Using primary envs directory: {primary_envs_dir}")
                    return primary_envs_dir
                else:
                    # Create it if it doesn't exist
                    os.makedirs(primary_envs_dir, exist_ok=True)
                    print(f"[INFO] Created envs directory: {primary_envs_dir}")
                    return primary_envs_dir
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            print(f"[DEBUG] conda info --json method failed: {e}")
        
        # Method 2: Parse conda info text output (fallback)
        try:
            result = subprocess.run([self.conda_cmd, 'info'], 
                                  capture_output=True, text=True, check=True)
            
            # Parse the text output for 'envs directories'
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('envs directories :') or line.startswith('envs directories:'):
                    # Extract the directory path after the colon
                    envs_dir = line.split(':', 1)[1].strip()
                    if envs_dir and os.path.exists(envs_dir):
                        print(f"[INFO] Found envs directory from text output: {envs_dir}")
                        return envs_dir
                    elif envs_dir:
                        os.makedirs(envs_dir, exist_ok=True)
                        print(f"[INFO] Created envs directory from text output: {envs_dir}")
                        return envs_dir
                        
        except subprocess.CalledProcessError as e:
            print(f"[DEBUG] conda info text method failed: {e}")
        
        # Method 3: Use CONDA_PREFIX or MAMBA_PREFIX environment variable
        for prefix_var in ['CONDA_PREFIX', 'MAMBA_PREFIX']:
            conda_prefix = os.environ.get(prefix_var)
            if conda_prefix:
                # If we're in an environment, get the base installation
                if '/envs/' in conda_prefix:
                    base_prefix = conda_prefix.split('/envs/')[0]
                else:
                    base_prefix = conda_prefix
                    
                envs_dir = os.path.join(base_prefix, 'envs')
                if os.path.exists(envs_dir) or base_prefix:
                    os.makedirs(envs_dir, exist_ok=True)
                    print(f"[INFO] Using {prefix_var} based directory: {envs_dir}")
                    return envs_dir
        
        # Method 4: Analyze existing environments to find active installation
        try:
            result = subprocess.run([self.conda_cmd, 'env', 'list'], 
                                  capture_output=True, text=True, check=True)
            
            # Count environments per base installation
            env_bases = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '/envs/' in line:
                    # Extract path from the line (usually the last column)
                    parts = line.split()
                    if len(parts) >= 2:
                        env_path = parts[-1]  # Last part is usually the path
                        if '/envs/' in env_path:
                            base_path = env_path.split('/envs/')[0]
                            env_bases[base_path] = env_bases.get(base_path, 0) + 1
            
            if env_bases:
                # Use the installation with the most environments
                main_base = max(env_bases.items(), key=lambda x: x[1])[0]
                envs_dir = os.path.join(main_base, 'envs')
                print(f"[INFO] Detected active installation: {main_base} ({env_bases[main_base]} environments)")
                os.makedirs(envs_dir, exist_ok=True)
                return envs_dir
                
        except subprocess.CalledProcessError as e:
            print(f"[DEBUG] Environment list analysis failed: {e}")
        
        # Method 5: Final fallback - use current working directory
        fallback_dir = os.path.join(os.getcwd(), 'envs')
        print(f"[WARNING] Could not detect conda envs directory, using fallback: {fallback_dir}")
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir
    
    def clone_with_conda_pack(self, old_env, new_name="auto", output_dir="./cloned_environments", interactive=True):
        """Clone environment using conda-pack (recommended for exact replication)."""
        
        if not self.conda_pack_available:
            raise RuntimeError("conda-pack is required for this method. Install with: conda install conda-pack")
        
        print("[INFO] Cloning environment with conda-pack...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info, new_name, interactive=interactive)
        
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
    
    def clone_with_yaml(self, old_env, new_name="auto", output_dir="./exported_environments", interactive=True):
        """Clone environment using YAML export/import (cross-platform compatible)."""
        
        print(f"[YAML] Cloning environment with YAML...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info, new_name, interactive=interactive)
        
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
            
            # Update name in YAML file and make it more flexible
            with open(yaml_path, 'r') as f:
                content = f.read()
            
            content = re.sub(r'^name:.*$', f'name: {final_name}', content, flags=re.MULTILINE)
            
            # Create a more flexible version of the YAML by relaxing constraints
            flexible_yaml_path = yaml_path.replace('.yml', '_flexible.yml')
            self._create_flexible_yaml(yaml_path, flexible_yaml_path)
            
            with open(yaml_path, 'w') as f:
                f.write(content)
            
            print("[SUCCESS] YAML exported successfully!")
            print(f"[FILE] YAML file: {yaml_path}")
            print(f"[FILE] Flexible YAML: {flexible_yaml_path}")
            
            # Optionally create the environment immediately
            create_now = input(f"\n[?] Create environment '{final_name}' now? (y/N): ").strip().lower()
            
            if create_now == 'y':
                print(f"[CREATE] Creating environment {final_name}...")
                success = False
                
                # Try original YAML first
                try:
                    subprocess.run([
                        self.conda_cmd, 'env', 'create',
                        '-f', yaml_path
                    ], check=True)
                    print(f"[SUCCESS] Environment '{final_name}' created successfully!")
                    success = True
                except subprocess.CalledProcessError as e:
                    print(f"[WARN] Original YAML failed: {e}")
                    print("[INFO] Trying with flexible dependency versions...")
                    
                    # Try flexible version
                    try:
                        subprocess.run([
                            self.conda_cmd, 'env', 'create',
                            '-f', flexible_yaml_path
                        ], check=True)
                        print(f"[SUCCESS] Environment '{final_name}' created with flexible dependencies!")
                        success = True
                    except subprocess.CalledProcessError as e2:
                        print(f"[FAIL] Both attempts failed: {e2}")
                        print(f"[TIP] You can manually edit and try: {self.conda_cmd} env create -f {flexible_yaml_path}")
                        print("[TIP] Consider removing problematic packages or updating dependency versions")
            
            return yaml_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"YAML export failed: {e}")
    
    def _create_flexible_yaml(self, original_yaml, flexible_yaml):
        """Create a more flexible version of the YAML file with relaxed dependencies."""
        try:
            # Extract the target environment name from the flexible_yaml filename
            # flexible_yaml is like "/path/to/env_name_flexible.yml" 
            flexible_basename = os.path.basename(flexible_yaml)
            if flexible_basename.endswith('_flexible.yml'):
                target_env_name = flexible_basename[:-13]  # Remove '_flexible.yml'
            else:
                target_env_name = flexible_basename.replace('.yml', '')
            
            with open(original_yaml, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            flexible_lines = []
            
            for line in lines:
                # Handle name line specially - use target environment name
                if line.startswith('name:'):
                    flexible_lines.append(f'name: {target_env_name}')
                    continue
                # Copy other header sections as-is
                elif line.startswith('channels:') or line.startswith('dependencies:') or line.startswith('prefix:') or not line.strip():
                    flexible_lines.append(line)
                    continue
                
                # Process dependency lines
                if line.strip().startswith('- ') and '=' in line:
                    # Extract package name and relax version constraints
                    package_spec = line.strip()[2:]  # Remove '- '
                    
                    # Handle pip dependencies differently
                    if package_spec.startswith('pip:'):
                        flexible_lines.append(line)
                        continue
                    
                    # For conda packages, relax version constraints
                    if '=' in package_spec:
                        package_name = package_spec.split('=')[0]
                        version_part = package_spec.split('=')[1]
                        
                        # Skip these problematic system packages that often cause conflicts
                        skip_packages = ['libgcc-ng', 'libstdcxx-ng', '_libgcc_mutex', '_openmp_mutex', 
                                       'ld_impl_linux-64', 'libgomp', 'libgcc', 'glibc']
                        
                        if any(skip_pkg in package_name for skip_pkg in skip_packages):
                            continue
                        
                        # For other packages, try to relax version constraints
                        if '.' in version_part:
                            # For version like 1.2.3, use >=1.2,<2.0
                            major_minor = '.'.join(version_part.split('.')[0:2])
                            major = version_part.split('.')[0]
                            try:
                                next_major = str(int(major) + 1)
                                flexible_spec = f"- {package_name}>={major_minor},<{next_major}.0"
                            except ValueError:
                                # If major version is not numeric, just use major.minor
                                flexible_spec = f"- {package_name}>={major_minor}"
                        else:
                            # Single version number, just use >= constraint
                            flexible_spec = f"- {package_name}>={version_part}"
                        
                        flexible_lines.append(flexible_spec)
                    else:
                        # No version specified, keep as-is
                        flexible_lines.append(line)
                else:
                    # Copy other lines as-is
                    flexible_lines.append(line)
            
            # Write flexible YAML
            with open(flexible_yaml, 'w') as f:
                f.write('\n'.join(flexible_lines))
                
        except Exception as e:
            print(f"[WARN] Could not create flexible YAML: {e}")
            # If flexible YAML creation fails, just copy the original
            shutil.copy2(original_yaml, flexible_yaml)
    
    def clone_environment(self, old_env, new_name="auto", method="auto", output_dir=None, interactive=True):
        """
        Clone an environment using the best available method.
        
        Args:
            old_env: Environment name or path
            new_name: New environment name ("auto" for smart naming)
            method: "conda-pack", "yaml", or "auto"
            output_dir: Output directory (None for default)
            interactive: Whether to show interactive naming options (default: True)
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
            return self.clone_with_conda_pack(old_env, new_name, output_dir, interactive)
        elif method == "yaml":
            return self.clone_with_yaml(old_env, new_name, output_dir, interactive)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def unpack_archive(self, archive_path, new_name="auto", target_envs_dir=None, extract_method="system"):
        """
        Unpack a conda-pack archive to the conda environments directory with smart naming.
        
        Args:
            archive_path (str): Path to the .tar.gz archive file
            new_name (str): Environment name ('auto' for smart generation, or custom name)
            target_envs_dir (str): Optional override for envs directory (default: auto-detect)
            extract_method (str): Extraction method ('system' or 'python')
        
        Returns:
            str: Path to the unpacked environment directory
        """
        
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        # Extract the original environment name from archive filename
        archive_basename = os.path.splitext(os.path.splitext(os.path.basename(archive_path))[0])[0]
        
        # Remove common suffixes that we don't want in the environment name
        suffixes_to_remove = ['_yaml', '_yml', '_export', '_backup']
        for suffix in suffixes_to_remove:
            if archive_basename.endswith(suffix):
                archive_basename = archive_basename[:-len(suffix)]
                break
        
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
        final_name = self._generate_new_name(env_info, new_name, interactive=False)
        
        print(f"[UNPACK] Unpacking {archive_path} as '{final_name}'...")
        if env_info['python_version']:
            print(f"[PYTHON] Detected Python: {env_info['python_version']}")
        if env_info['r_version']:
            print(f"[R] Detected R: {env_info['r_version']}")
        
        try:
            # Get conda environments directory
            if target_envs_dir:
                envs_dir = target_envs_dir
                print(f"[OVERRIDE] Using specified envs directory: {envs_dir}")
            else:
                envs_dir = self._get_conda_envs_directory()
            
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
            
            # Choose extraction method based on parameter
            if extract_method == "system":
                # Try to use system tar command first (often much faster)
                try:
                    print("[EXTRACT] Attempting fast extraction using system tar...")
                    import subprocess
                    
                    # Use system tar command for faster extraction
                    result = subprocess.run([
                        'tar', '-xzf', archive_path, '-C', target_env_path, '--strip-components=0'
                    ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout
                    
                    if result.returncode == 0:
                        print("[SUCCESS] Fast extraction completed")
                    else:
                        raise subprocess.CalledProcessError(result.returncode, 'tar')
                        
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    # Fallback to Python tarfile with progress feedback
                    print("[FALLBACK] System tar failed, using Python tarfile extraction...")
                    extract_method = "python"  # Switch to python method for fallback
            
            if extract_method == "python":
                # Use Python tarfile with progress feedback
                print("[EXTRACT] Using Python tarfile extraction with progress tracking...")
                
                with tarfile.open(archive_path, 'r:gz') as tar:
                    # Get total number of members for progress tracking
                    members = tar.getmembers()
                    total_members = len(members)
                    
                    # Extract with progress feedback every 1000 files
                    for i, member in enumerate(members):
                        if i % 1000 == 0 and i > 0:
                            progress = (i / total_members) * 100
                            print(f"[PROGRESS] Extracted {i}/{total_members} files ({progress:.1f}%)")
                        
                        try:
                            tar.extract(member, path=target_env_path)
                        except Exception as e:
                            # Skip problematic files but continue
                            print(f"[WARNING] Skipped problematic file: {member.name} ({e})")
                            continue
                    
                    print(f"[COMPLETE] Extracted {total_members} files")
            
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
    clone_parser.add_argument("--non-interactive", action="store_true",
                             help="Disable interactive naming (use auto-generated names)")
    
    # Unpack command
    unpack_parser = subparsers.add_parser("unpack", help="Unpack a conda-pack archive")
    unpack_parser.add_argument("archive", help="Path to .tar.gz archive")
    unpack_parser.add_argument("new_name", nargs="?", default="auto", 
                             help="New environment name (default: auto-generated with version suffixes)")
    unpack_parser.add_argument("--target-envs-dir", help="Target envs directory (overrides auto-detection)")
    unpack_parser.add_argument("--extract-method", choices=["system", "python"], default="system",
                             help="Extraction method: 'system' (fast, uses tar command) or 'python' (slower, pure Python)")
    
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
                args.output_dir,
                interactive=not args.non_interactive
            )
            print(f"\n[COMPLETE] Clone operation completed: {result}")
            
        elif args.command == "unpack":
            result = cloner.unpack_archive(
                args.archive, 
                args.new_name, 
                target_envs_dir=args.target_envs_dir,
                extract_method=args.extract_method
            )
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
