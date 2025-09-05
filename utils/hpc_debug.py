#!/usr/bin/env python3
"""
HPC Environment Detection Debug Script

This script helps debug conda/mamba detection issues on HPC systems.
"""

import os
import subprocess
import sys

def test_direct_commands():
    """Test if mamba/conda work directly"""
    print("=== Testing Direct Commands ===")
    
    for cmd in ["mamba", "conda"]:
        try:
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ {cmd} works directly: {result.stdout.strip()}")
        except FileNotFoundError:
            print(f"❌ {cmd} not found in PATH")
        except subprocess.CalledProcessError as e:
            print(f"❌ {cmd} failed: {e}")

def test_shell_commands():
    """Test if mamba/conda work with shell=True"""
    print("\n=== Testing Shell Commands ===")
    
    for cmd in ["mamba", "conda"]:
        try:
            result = subprocess.run(f"{cmd} --version", 
                                  capture_output=True, text=True, check=True, shell=True)
            print(f"✅ {cmd} works with shell: {result.stdout.strip()}")
        except FileNotFoundError:
            print(f"❌ {cmd} not found via shell")
        except subprocess.CalledProcessError as e:
            print(f"❌ {cmd} failed via shell: {e}")

def check_environment_variables():
    """Check relevant environment variables"""
    print("\n=== Environment Variables ===")
    
    env_vars = [
        "CONDA_EXE", "MAMBA_EXE", "CONDA_PREFIX", "CONDA_DEFAULT_ENV",
        "PATH", "CONDA_PYTHON_EXE", "CONDA_ENVS_PATH"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "NOT SET")
        if var == "PATH":
            # Show only conda/mamba related paths
            paths = value.split(":")
            conda_paths = [p for p in paths if any(x in p.lower() for x in ["conda", "mamba", "miniforge"])]
            if conda_paths:
                print(f"{var} (conda-related): {':'.join(conda_paths)}")
            else:
                print(f"{var}: No conda/mamba paths found")
        else:
            print(f"{var}: {value}")

def check_common_paths():
    """Check common installation paths"""
    print("\n=== Common Installation Paths ===")
    
    import glob
    
    common_patterns = [
        "/opt/conda/bin/conda",
        "/opt/miniconda/bin/conda",
        "/cluster/*/conda/bin/conda",
        "/cluster/*/miniforge*/bin/conda", 
        "/cluster/*/miniforge*/bin/mamba",
        "~/miniconda*/bin/conda",
        "~/miniforge*/bin/conda",
        "~/miniforge*/bin/mamba"
    ]
    
    for pattern in common_patterns:
        try:
            expanded = glob.glob(os.path.expanduser(pattern))
            for path in expanded:
                if os.path.exists(path):
                    try:
                        result = subprocess.run([path, "--version"], 
                                              capture_output=True, text=True, check=True)
                        print(f"✅ Found working: {path} -> {result.stdout.strip()}")
                    except:
                        print(f"❓ Found but not working: {path}")
        except Exception as e:
            print(f"❌ Error checking {pattern}: {e}")

if __name__ == "__main__":
    print("HPC Conda/Mamba Detection Debug Tool")
    print("=" * 50)
    
    test_direct_commands()
    test_shell_commands() 
    check_environment_variables()
    check_common_paths()
    
    print("\n=== Testing Environment Manager ===")
    try:
        sys.path.insert(0, '.')
        from environment_manager import EnvironmentManager
        manager = EnvironmentManager()
        print(f"✅ Environment Manager initialized successfully!")
        print(f"   Using: {manager.cmd_base}")
        print(f"   Is mamba: {manager.use_mamba}")
    except Exception as e:
        print(f"❌ Environment Manager failed: {e}")
        import traceback
        traceback.print_exc()
