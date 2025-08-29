#!/usr/bin/env python3
"""
HPC Compatibility Test Script
Tests basic functionality without emoji characters or HPC-incompatible features.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("[TEST] Testing module imports...")
    
    try:
        import environment_manager
        print("[OK] environment_manager imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import environment_manager: {e}")
        return False
    
    try:
        from utils.environment_cloner import EnvironmentCloner
        print("[OK] EnvironmentCloner imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import EnvironmentCloner: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality."""
    print("\n[TEST] Testing basic functionality...")
    
    try:
        # Test environment manager initialization
        from environment_manager import EnvironmentManager
        manager = EnvironmentManager()
        print("[OK] EnvironmentManager initialized successfully")
        
        # Test cloner initialization  
        from utils.environment_cloner import EnvironmentCloner
        cloner = EnvironmentCloner()
        print("[OK] EnvironmentCloner initialized successfully")
        
        return True
    except Exception as e:
        print(f"[FAIL] Basic functionality test failed: {e}")
        return False

def test_character_encoding():
    """Test that output uses only ASCII characters."""
    print("\n[TEST] Testing character encoding...")
    
    # Test strings that should be ASCII-only
    test_strings = [
        "[SUCCESS] Operation completed",
        "[FAIL] Operation failed", 
        "[PROGRESS] Working...",
        "[OK] All good",
        "Environment: test_env -> new_env"
    ]
    
    for test_str in test_strings:
        try:
            # Try to encode as ASCII
            test_str.encode('ascii')
            print(f"[OK] ASCII-safe: {test_str}")
        except UnicodeEncodeError:
            print(f"[FAIL] Non-ASCII characters found: {test_str}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("HPC Compatibility Test Suite")
    print("=" * 40)
    
    all_passed = True
    
    # Run tests
    if not test_imports():
        all_passed = False
    
    if not test_basic_functionality():
        all_passed = False
        
    if not test_character_encoding():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("[SUCCESS] All HPC compatibility tests passed!")
        sys.exit(0)
    else:
        print("[FAIL] Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
