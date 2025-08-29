#!/usr/bin/env python3
"""
YAML Conflict Solver

Analyzes conda environment YAML files and creates more flexible versions
to resolve dependency conflicts during environment recreation.
"""

import os
import sys
import re
import argparse
from pathlib import Path

def analyze_yaml_conflicts(yaml_file):
    """Analyze a YAML file for potential conflict sources."""
    print(f"\n🔍 Analyzing YAML file: {yaml_file}")
    
    with open(yaml_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Count dependencies
    deps = []
    pip_deps = []
    system_deps = []
    
    in_deps = False
    in_pip = False
    
    for line in lines:
        line = line.strip()
        
        if line == 'dependencies:':
            in_deps = True
            continue
        elif line.startswith('- pip:'):
            in_pip = True
            continue
        elif in_deps and line.startswith('- ') and not in_pip:
            if line.startswith('- pip'):
                in_pip = True
                continue
            
            pkg_spec = line[2:]  # Remove '- '
            deps.append(pkg_spec)
            
            # Identify potentially problematic system packages
            system_packages = ['libgcc-ng', 'libstdcxx-ng', '_libgcc_mutex', '_openmp_mutex', 
                             'ld_impl_linux-64', 'libgomp', 'libgcc', 'glibc', 'krb5', 'openssl', 'libpq']
            
            if any(sys_pkg in pkg_spec.lower() for sys_pkg in system_packages):
                system_deps.append(pkg_spec)
        elif in_pip and line.startswith('  - '):
            pip_deps.append(line[4:])  # Remove '  - '
        elif line and not line.startswith(' ') and not line.startswith('-'):
            in_deps = False
            in_pip = False
    
    print(f"📊 Analysis Results:")
    print(f"  Total conda dependencies: {len(deps)}")
    print(f"  Total pip dependencies: {len(pip_deps)}")
    print(f"  Potentially problematic system packages: {len(system_deps)}")
    
    if system_deps:
        print(f"\n⚠️  Problematic system packages found:")
        for pkg in system_deps[:5]:  # Show first 5
            print(f"    {pkg}")
        if len(system_deps) > 5:
            print(f"    ... and {len(system_deps) - 5} more")
    
    return deps, pip_deps, system_deps

def create_flexible_yaml(input_yaml, output_yaml=None):
    """Create a more flexible version of the YAML with relaxed constraints."""
    if output_yaml is None:
        base = Path(input_yaml).stem
        dir_path = Path(input_yaml).parent
        output_yaml = dir_path / f"{base}_flexible.yml"
    
    print(f"\n🔧 Creating flexible YAML: {output_yaml}")
    
    with open(input_yaml, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    flexible_lines = []
    removed_packages = []
    relaxed_packages = []
    
    for line in lines:
        # Copy header sections as-is
        if (line.startswith('name:') or line.startswith('channels:') or 
            line.startswith('dependencies:') or line.startswith('prefix:') or 
            not line.strip() or line.strip().startswith('#')):
            flexible_lines.append(line)
            continue
        
        # Handle pip section
        if line.strip().startswith('- pip:') or (len(flexible_lines) > 0 and 
            any('- pip:' in prev_line for prev_line in flexible_lines[-5:]) and 
            line.startswith('  ')):
            flexible_lines.append(line)
            continue
        
        # Process conda dependency lines
        if line.strip().startswith('- ') and '=' in line:
            package_spec = line.strip()[2:]  # Remove '- '
            
            # Skip problematic system packages
            skip_packages = ['libgcc-ng', 'libstdcxx-ng', '_libgcc_mutex', '_openmp_mutex', 
                           'ld_impl_linux-64', 'libgomp', 'libgcc', 'glibc']
            
            if any(skip_pkg in package_spec for skip_pkg in skip_packages):
                removed_packages.append(package_spec)
                flexible_lines.append(f"# REMOVED: {line}")
                continue
            
            # Relax version constraints for other packages
            if '=' in package_spec:
                package_name = package_spec.split('=')[0]
                version_part = package_spec.split('=')[1]
                
                # Special handling for known problematic packages
                if package_name in ['krb5', 'openssl', 'libpq']:
                    # Use looser constraints
                    if '.' in version_part:
                        major = version_part.split('.')[0]
                        flexible_spec = f"  - {package_name}>={major}"
                        relaxed_packages.append(f"{package_name}: {version_part} -> >={major}")
                    else:
                        flexible_spec = f"  - {package_name}"
                        relaxed_packages.append(f"{package_name}: {version_part} -> any")
                    flexible_lines.append(flexible_spec)
                else:
                    # For regular packages, use major.minor constraints
                    if '.' in version_part:
                        major_minor = '.'.join(version_part.split('.')[0:2])
                        major = version_part.split('.')[0]
                        try:
                            next_major = str(int(major) + 1)
                            flexible_spec = f"  - {package_name}>={major_minor},<{next_major}.0"
                            relaxed_packages.append(f"{package_name}: ={version_part} -> >={major_minor},<{next_major}.0")
                        except ValueError:
                            flexible_spec = f"  - {package_name}>={major_minor}"
                            relaxed_packages.append(f"{package_name}: ={version_part} -> >={major_minor}")
                    else:
                        flexible_spec = f"  - {package_name}>={version_part}"
                        relaxed_packages.append(f"{package_name}: ={version_part} -> >={version_part}")
                    
                    flexible_lines.append(flexible_spec)
            else:
                # No version specified, keep as-is
                flexible_lines.append(line)
        else:
            # Copy other lines as-is
            flexible_lines.append(line)
    
    # Write flexible YAML
    with open(output_yaml, 'w') as f:
        f.write('\n'.join(flexible_lines))
    
    print(f"✅ Flexible YAML created successfully!")
    print(f"📋 Changes made:")
    print(f"  Removed {len(removed_packages)} problematic system packages")
    print(f"  Relaxed {len(relaxed_packages)} package constraints")
    
    if removed_packages:
        print(f"\n🗑️  Removed packages:")
        for pkg in removed_packages[:3]:
            print(f"    {pkg}")
        if len(removed_packages) > 3:
            print(f"    ... and {len(removed_packages) - 3} more")
    
    if relaxed_packages:
        print(f"\n🔄 Relaxed constraints:")
        for pkg in relaxed_packages[:3]:
            print(f"    {pkg}")
        if len(relaxed_packages) > 3:
            print(f"    ... and {len(relaxed_packages) - 3} more")
    
    return output_yaml

def main():
    parser = argparse.ArgumentParser(
        description="Analyze and fix conda environment YAML conflicts"
    )
    parser.add_argument('yaml_file', help='Input YAML file to analyze')
    parser.add_argument('--output', '-o', help='Output flexible YAML file')
    parser.add_argument('--analyze-only', '-a', action='store_true', 
                       help='Only analyze, do not create flexible YAML')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.yaml_file):
        print(f"❌ Error: YAML file not found: {args.yaml_file}")
        sys.exit(1)
    
    # Analyze the YAML file
    deps, pip_deps, system_deps = analyze_yaml_conflicts(args.yaml_file)
    
    # Create flexible version unless analyze-only
    if not args.analyze_only:
        flexible_yaml = create_flexible_yaml(args.yaml_file, args.output)
        
        print(f"\n🚀 Next Steps:")
        print(f"  1. Try creating environment with flexible YAML:")
        print(f"     mamba env create -f {flexible_yaml}")
        print(f"  2. If conflicts persist, manually edit {flexible_yaml}")
        print(f"     - Remove additional problematic packages")
        print(f"     - Further relax version constraints")
        print(f"  3. Consider using conda-forge channel only")
        print(f"  4. Update conda/mamba: conda update conda")

if __name__ == "__main__":
    main()
