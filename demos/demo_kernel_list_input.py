#!/usr/bin/env python3
"""
Demo script for testing the enhanced kernel creation feature
"""

import subprocess
import sys

def demo_kernel_list_input():
    """Demonstrate the enhanced kernel creation with list input"""
    
    print("=== Demo: Enhanced Kernel Creation with List Input ===\n")
    
    # Show the menu flow
    print("1. Starting environment manager...")
    print("2. Selecting option 7 (KERNEL)")
    print("3. Selecting option 3 (List Input)")
    print("4. Example inputs: [1,3,5] or [2,4-6] or [1,2-4,7]")
    
    # Simulate the interaction
    inputs = [
        "7",      # Select KERNEL option
        "3",      # Select list input option  
        "[1,3,6]", # Select environments 1, 3, and 6
        "1",      # Python kernels only
        "y",      # Confirm
        "10"      # Exit
    ]
    
    input_string = "\n".join(inputs) + "\n"
    
    try:
        print(f"\n🧪 Running with inputs: {inputs}")
        proc = subprocess.Popen(
            ['python', 'environment_manager.py'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            cwd='/Users/jjanssens/Postdoc/conda_environments'
        )
        
        output, _ = proc.communicate(input_string, timeout=30)
        
        print("\n📊 Output:")
        print("=" * 60)
        print(output)
        print("=" * 60)
        
        if "Kernel creation completed" in output:
            print("\n✅ Demo completed successfully!")
        else:
            print("\n⚠️  Demo completed - check output for details")
            
    except subprocess.TimeoutExpired:
        print("\n⏱️  Demo timed out - environment manager may be waiting for input")
        proc.kill()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

def show_feature_summary():
    """Show summary of the enhanced kernel creation features"""
    
    print("\n🎯 Enhanced Kernel Creation Features:")
    print("=" * 50)
    
    features = [
        "✅ List input format: [1,3,5] or [2,4-6]",
        "✅ Range support: [1,3-5,7] expands to [1,3,4,5,7]",
        "✅ Kernel type selection (Python/R/Both)",
        "✅ Environment compatibility checking",
        "✅ Preview before creation",
        "✅ Integration with existing kernel creation system"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📝 Usage Examples:")
    print("  [1,3,5]     - Select environments 1, 3, and 5")
    print("  [2,4-7]     - Select environment 2 and range 4-7") 
    print("  [1,3-5,8]   - Select 1, range 3-5, and 8")
    print("  1,3,5       - Same as [1,3,5] (brackets optional)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_kernel_list_input()
    else:
        show_feature_summary()
        print(f"\nTo run the interactive demo: python {sys.argv[0]} --demo")
