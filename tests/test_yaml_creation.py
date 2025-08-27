#!/usr/bin/env python3
"""
Test YAML environment creation with -y flag
"""

from pathlib import Path
import tempfile
import yaml
from environment_manager import EnvironmentManager

def test_yaml_environment_creation():
    """Test creating environment from YAML file with proper -y flag"""
    
    print("🧪 Testing YAML environment creation with -y flag...\n")
    
    manager = EnvironmentManager(use_mamba=False)
    
    # Create a temporary YAML file
    test_yaml_content = {
        'name': 'test_yaml_env',
        'channels': ['defaults'],
        'dependencies': [
            'python=3.9',
            'numpy'
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(test_yaml_content, f, default_flow_style=False)
        yaml_file = Path(f.name)
    
    try:
        print(f"Created test YAML file: {yaml_file}")
        print("Testing environment creation from YAML...")
        
        # Test the create_environment_from_yaml method
        success = manager.create_environment_from_yaml(yaml_file, "test_yaml_env_new")
        
        if success:
            print("✅ Environment creation successful!")
            
            # Clean up the test environment
            print("Cleaning up test environment...")
            cleanup_success = manager.remove_environment("test_yaml_env_new")
            if cleanup_success:
                print("✅ Cleanup successful!")
            else:
                print("⚠️  Cleanup failed, but main test passed")
            
            return True
        else:
            print("❌ Environment creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up the temporary YAML file
        if yaml_file.exists():
            yaml_file.unlink()

if __name__ == "__main__":
    success = test_yaml_environment_creation()
    if success:
        print("\n🎉 YAML environment creation with -y flag working correctly!")
    else:
        print("\n❌ YAML environment creation test failed!")
