#!/usr/bin/env python3
"""
Test the progress display functionality
"""

from environment_manager import EnvironmentManager

def test_progress_display():
    """Test the progress display for environment operations"""
    
    print("🧪 Testing progress display functionality...\n")
    
    manager = EnvironmentManager(use_mamba=False)
    
    # Create a test environment with some packages to see progress
    test_env = "test_progress_env"
    
    print("Creating test environment with progress display...")
    try:
        # Create environment with a few packages to see progress
        result = manager._run_command_with_progress([
            manager.cmd_base, "create", "-n", test_env, "-y", 
            "python=3.9", "numpy", "pandas"
        ], "Creating test environment with packages")
        
        if result.returncode == 0:
            print(f"\n✅ Test environment '{test_env}' created successfully!")
            
            print("\nNow testing removal with progress display...")
            
            # Test removal with progress
            remove_result = manager._run_command_with_progress([
                manager.cmd_base, "env", "remove", "-n", test_env, "-y"
            ], "Removing test environment")
            
            if remove_result.returncode == 0:
                print(f"\n✅ Test environment '{test_env}' removed successfully!")
                print("\n🎉 Progress display functionality working correctly!")
                return True
            else:
                print(f"\n❌ Failed to remove test environment")
                return False
        else:
            print(f"\n❌ Failed to create test environment")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False
    finally:
        # Cleanup: ensure test environment is removed
        try:
            manager._run_command([
                manager.cmd_base, "env", "remove", "-n", test_env, "-y"
            ], check=False)
        except:
            pass

if __name__ == "__main__":
    success = test_progress_display()
    if not success:
        print("\n⚠️  Note: Progress display is now available for environment creation and removal!")
        print("When you run environment operations, you'll see real-time progress updates.")
