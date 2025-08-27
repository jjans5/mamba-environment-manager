#!/usr/bin/env python3
"""
Test YAML export and validate the generated files
"""

from environment_manager import EnvironmentManager
import yaml
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG)

def test_yaml_export_validation():
    print("=== Testing YAML Export and Validation ===\n")
    
    manager = EnvironmentManager()
    
    # Try to export a simple environment that should exist
    test_env = "cellxgene"  # Based on previous conda env list
    
    print(f"Testing export and validation of environment: {test_env}")
    
    # Export the environment
    result = manager.export_environment(test_env)
    
    if result and result.exists():
        print(f"✅ Export successful: {result}")
        print(f"File size: {result.stat().st_size} bytes")
        
        # Read and validate the YAML
        try:
            print("\n📄 Raw file content (first 10 lines):")
            with open(result, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10], 1):
                    print(f"{i:2d}: {line.rstrip()}")
            
            print(f"\n📄 Total lines: {len(lines)}")
            
            # Try to parse the YAML
            print("\n🔍 Parsing YAML...")
            with open(result, 'r') as f:
                env_data = yaml.safe_load(f)
            
            if env_data:
                print("✅ YAML parsing successful")
                print(f"Environment name: {env_data.get('name', 'NOT FOUND')}")
                print(f"Channels: {env_data.get('channels', 'NOT FOUND')}")
                print(f"Dependencies type: {type(env_data.get('dependencies', 'NOT FOUND'))}")
                
                deps = env_data.get('dependencies', [])
                if deps:
                    print(f"Number of dependencies: {len(deps)}")
                    print("First few dependencies:")
                    for dep in deps[:5]:
                        print(f"  - {dep} ({type(dep)})")
                
            else:
                print("❌ YAML parsing returned None")
                
        except yaml.YAMLError as e:
            print(f"❌ YAML parsing failed: {e}")
            
            # Show the problematic area
            print("\nContent around the error:")
            with open(result, 'r') as f:
                content = f.read()
                print(repr(content[:200]))  # Show raw content
                
        except Exception as e:
            print(f"❌ Other error: {e}")
        
        # Test the package extraction function
        print(f"\n🧪 Testing package extraction...")
        try:
            detected = manager._extract_package_versions_from_yaml(result, test_env)
            print(f"✅ Package extraction successful: {detected}")
        except Exception as e:
            print(f"❌ Package extraction failed: {e}")
        
        # Clean up
        result.unlink()
        print(f"\n🧹 Cleaned up {result}")
        
    else:
        print("❌ Export failed or file not found")

if __name__ == "__main__":
    test_yaml_export_validation()
