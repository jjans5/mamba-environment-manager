#!/usr/bin/env python3
"""
Test script to demonstrate the new interactive menu options
"""

from environment_manager import EnvironmentManager

def test_interactive_menu():
    """Test the new menu options"""
    print("🧪 Testing interactive menu with new options...")
    
    manager = EnvironmentManager()
    
    # Test the new functions directly
    print("\n1. Testing cleanup function...")
    # Create a test YAML file first
    test_yaml = manager.export_dir / "test_cleanup.yml"
    test_yaml.write_text("name: test\nchannels:\n  - defaults\ndependencies:\n  - python\n")
    
    print(f"Created test YAML file: {test_yaml}")
    success = manager.cleanup_exported_yaml_files(confirm=False)
    print(f"Cleanup result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n2. Testing kernel recreation...")
    # Test with specific environments
    result = manager.recreate_jupyter_kernels(['cellxgene'])  # Test with one environment
    print(f"Kernel recreation result: {'✅ Success' if result else '❌ Failed'}")
    
    print("\n✅ All interactive features tested!")

if __name__ == "__main__":
    test_interactive_menu()
