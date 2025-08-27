#!/usr/bin/env python3
"""
Test processing of the problematic anaconda3 environment
"""

from environment_manager import EnvironmentManager

def test_anaconda3_processing():
    """Test processing the problematic anaconda3 environment"""
    
    # Create manager
    manager = EnvironmentManager(use_mamba=False)  # Use conda since mamba not available
    
    # Get environment list
    environments = manager.list_environments()
    
    # Find anaconda3 environment
    anaconda3_env = None
    for env in environments:
        if env['name'] == 'anaconda3':
            anaconda3_env = env
            break
    
    if not anaconda3_env:
        print("anaconda3 environment not found")
        return False
        
    print(f"Found anaconda3 environment: {anaconda3_env}")
    
    # Test processing
    print("Processing anaconda3 environment...")
    result = manager.process_environment(anaconda3_env, environments)
    
    if result:
        print("✓ anaconda3 environment processed successfully")
        
        # Check if it's a base environment
        env_path = anaconda3_env.get('path', '')
        if manager._is_base_environment(env_path, 'anaconda3'):
            print("✓ anaconda3 is correctly identified as a base environment (not removed)")
            return True
        else:
            # Check if it's been removed
            new_environments = manager.list_environments()
            if not any(env['name'] == 'anaconda3' for env in new_environments):
                print("✓ anaconda3 environment was successfully removed")
                return True
            else:
                print("✗ anaconda3 environment still exists")
                return False
    else:
        print("✗ Processing failed")
        return False

if __name__ == "__main__":
    success = test_anaconda3_processing()
    if success:
        print("\n✅ anaconda3 empty environment handling successful!")
    else:
        print("\n❌ anaconda3 empty environment handling failed!")
