#!/usr/bin/env python3
"""
Environment Cloner Tool

Clones conda environments using conda-pack for portable deployment or YAML export.
Supports both direct cloning and YAML-based recreation with smart naming.
"""

import os
import sys
import subprocess
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
            subprocess.run(['conda', 'pack', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  conda-pack not found. Install with: conda install conda-pack")
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
                result = subprocess.run(
                    [self.conda_cmd, 'info', '--envs'],
                    capture_output=True, text=True, check=True
                )
                for line in result.stdout.split('\n'):
                    if env_name in line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            env_path = parts[-1]
                            break
                else:
                    raise ValueError(f"Environment '{env_name}' not found")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to get environment info: {e}")
        
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
    
    def clone_with_conda_pack(self, old_env, new_name="auto", output_dir="./cloned_environments"):
        """Clone environment using conda-pack (recommended for exact replication)."""
        
        if not self.conda_pack_available:
            raise RuntimeError("conda-pack is required for this method. Install with: conda install conda-pack")
        
        print(f"🔄 Cloning environment with conda-pack...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info['name'], new_name)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        archive_path = os.path.join(output_dir, f"{final_name}.tar.gz")
        
        print(f"📦 Packing {env_info['name']} → {archive_path}")
        
        # Pack the environment
        try:
            subprocess.run([
                'conda', 'pack',
                '-p', env_info['path'],
                '-o', archive_path
            ], check=True)
            
            print(f"✅ Environment packed successfully!")
            print(f"📁 Archive: {archive_path}")
            print(f"\n💡 To deploy on target machine:")
            print(f"   mkdir -p {final_name}")
            print(f"   tar -xzf {archive_path} -C {final_name}")
            print(f"   source {final_name}/bin/activate")
            print(f"   conda-unpack")
            
            return archive_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"conda-pack failed: {e}")
    
    def clone_with_yaml(self, old_env, new_name="auto", output_dir="./exported_environments"):
        """Clone environment using YAML export/import (cross-platform compatible)."""
        
        print(f"📄 Cloning environment with YAML...")
        
        # Get environment info
        env_info = self._get_environment_info(old_env)
        final_name = self._generate_new_name(env_info['name'], new_name)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        yaml_path = os.path.join(output_dir, f"{final_name}.yml")
        
        print(f"📤 Exporting {env_info['name']} → {yaml_path}")
        
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
            
            print(f"✅ YAML exported successfully!")
            print(f"📁 YAML file: {yaml_path}")
            
            # Optionally create the environment immediately
            create_now = input(f"\n❓ Create environment '{final_name}' now? (y/N): ").strip().lower()
            
            if create_now == 'y':
                print(f"🔨 Creating environment {final_name}...")
                try:
                    subprocess.run([
                        self.conda_cmd, 'env', 'create',
                        '-f', yaml_path
                    ], check=True)
                    print(f"✅ Environment '{final_name}' created successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to create environment: {e}")
                    print(f"💡 You can try later with: {self.conda_cmd} env create -f {yaml_path}")
            
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
        
        print(f"🔍 Analyzing environment: {old_env}")
        
        # Validate environment exists
        try:
            env_info = self._get_environment_info(old_env)
            print(f"✅ Found environment: {env_info['name']}")
            if env_info['python_version']:
                print(f"🐍 Python: {env_info['python_version']}")
            if env_info['r_version']:
                print(f"📊 R: {env_info['r_version']}")
        except Exception as e:
            raise RuntimeError(f"Environment validation failed: {e}")
        
        # Determine method
        if method == "auto":
            method = "conda-pack" if self.conda_pack_available else "yaml"
            print(f"🎯 Auto-selected method: {method}")
        
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

def main():
    """CLI interface for environment cloner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clone conda environments using conda-pack or YAML export"
    )
    parser.add_argument("old_env", help="Source environment name or path")
    parser.add_argument("new_name", nargs="?", default="auto", 
                       help="New environment name (default: auto-generated)")
    parser.add_argument("--method", choices=["conda-pack", "yaml", "auto"], 
                       default="auto", help="Cloning method")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        cloner = EnvironmentCloner()
        result = cloner.clone_environment(
            args.old_env, 
            args.new_name, 
            args.method, 
            args.output_dir
        )
        print(f"\n🎉 Clone operation completed: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
