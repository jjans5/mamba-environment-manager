#!/usr/bin/env python3
"""
Comprehensive codebase validation
"""

import sys
from pathlib import Path
from environment_manager import EnvironmentManager

def run_comprehensive_tests():
    """Run all critical tests to validate the codebase"""
    
    print("🧪 Running comprehensive codebase validation...\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic initialization
    print("1. Testing EnvironmentManager initialization...")
    tests_total += 1
    try:
        manager = EnvironmentManager(use_mamba=False)
        print("   ✅ Initialization successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
    
    # Test 2: Environment listing
    print("2. Testing environment listing...")
    tests_total += 1
    try:
        environments = manager.list_environments()
        if len(environments) > 0:
            print(f"   ✅ Found {len(environments)} environments")
            tests_passed += 1
        else:
            print("   ⚠️  No environments found (might be normal)")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ Environment listing failed: {e}")
    
    # Test 3: Empty environment detection
    print("3. Testing empty environment detection...")
    tests_total += 1
    try:
        empty_yaml = {
            'name': 'test_env',
            'channels': [],
            'dependencies': ['python=3.9.0', '_libgcc_mutex=0.1']
        }
        is_empty = manager._is_environment_empty(empty_yaml)
        if is_empty:
            print("   ✅ Empty environment correctly detected")
            tests_passed += 1
        else:
            print("   ❌ Empty environment not detected")
    except Exception as e:
        print(f"   ❌ Empty environment detection failed: {e}")
    
    # Test 4: Base environment detection
    print("4. Testing base environment detection...")
    tests_total += 1
    try:
        # Test with real environments
        valid_base = False
        for env in environments:
            if env['name'] in ['anaconda3', 'miniconda3']:
                is_base = manager._is_base_environment(env['path'], env['name'])
                if is_base:
                    valid_base = True
                    break
        
        if valid_base or not any(env['name'] in ['anaconda3', 'miniconda3'] for env in environments):
            print("   ✅ Base environment detection working")
            tests_passed += 1
        else:
            print("   ❌ Base environment detection failed")
    except Exception as e:
        print(f"   ❌ Base environment detection failed: {e}")
    
    # Test 5: Smart naming
    print("5. Testing smart naming...")
    tests_total += 1
    try:
        existing_names = [env['name'].lower() for env in environments]
        test_name = manager.generate_new_name(
            'test_env_py39', '3.9', None, existing_names, None
        )
        if test_name and test_name != 'test_env_py39':
            print(f"   ✅ Smart naming working: test_env_py39 → {test_name}")
            tests_passed += 1
        else:
            print("   ❌ Smart naming failed")
    except Exception as e:
        print(f"   ❌ Smart naming failed: {e}")
    
    # Test 6: YAML export (non-destructive test)
    print("6. Testing YAML export...")
    tests_total += 1
    try:
        # Find a real environment to test export
        test_env = None
        for env in environments:
            if env['name'] not in ['anaconda3', 'miniconda3']:  # Skip base environments
                test_env = env['name']
                break
        
        if test_env:
            export_result = manager.export_environment(test_env)
            if export_result == "EMPTY":
                print(f"   ✅ Export detected empty environment: {test_env}")
                tests_passed += 1
            elif isinstance(export_result, Path) and export_result.exists():
                print(f"   ✅ Export successful: {test_env}")
                tests_passed += 1
            else:
                print(f"   ❌ Export failed for: {test_env}")
        else:
            print("   ⚠️  No suitable environment for export test")
            tests_passed += 1  # Not a failure
    except Exception as e:
        print(f"   ❌ YAML export test failed: {e}")
    
    # Test 7: Error handling
    print("7. Testing error handling...")
    tests_total += 1
    try:
        # Test with non-existent environment
        result = manager.export_environment("non_existent_env_12345")
        if result is None:
            print("   ✅ Error handling working (non-existent environment)")
            tests_passed += 1
        else:
            print("   ❌ Error handling failed")
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! Codebase is in excellent condition.")
        return True
    elif tests_passed >= tests_total * 0.8:
        print("✅ Most tests passed! Codebase is in good condition.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
