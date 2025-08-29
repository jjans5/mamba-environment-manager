#!/usr/bin/env python3
"""
Demo script for testing the enhanced environment deletion feature
"""

import subprocess
import sys

def demo_environment_deletion():
    """Demonstrate the enhanced environment deletion with list input"""
    
    print("=== Demo: Enhanced Environment Deletion with List Input ===\n")
    
    # Show the menu flow
    print("1. Starting environment manager...")
    print("2. Selecting option 8 (DELETE)")
    print("3. Shows environments with safety warnings")
    print("4. Example inputs: [1,3,5] or [2,4-6] or [1,2-4,7]")
    print("5. Double confirmation required for safety")
    
    # Simulate the interaction (but don't actually delete)
    inputs = [
        "8",      # Select DELETE option
        "",       # Empty input to cancel
        "11"      # Exit
    ]
    
    input_string = "\n".join(inputs) + "\n"
    
    try:
        print(f"\n🧪 Running with inputs (safe demo - no deletion): {inputs}")
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
        
        if "No input provided - cancelling deletion" in output:
            print("\n✅ Demo completed successfully - deletion safely cancelled!")
        else:
            print("\n⚠️  Demo completed - check output for details")
            
    except subprocess.TimeoutExpired:
        print("\n⏱️  Demo timed out - environment manager may be waiting for input")
        proc.kill()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

def show_feature_summary():
    """Show summary of the enhanced environment deletion features"""
    
    print("\n🎯 Enhanced Environment Deletion Features:")
    print("=" * 50)
    
    features = [
        "✅ List input format: [1,3,5] or [2,4-6]",
        "✅ Range support: [1,3-5,7] expands to [1,3,4,5,7]",
        "✅ Safety protections: base/root environments excluded",
        "✅ Clear warnings about permanent deletion",
        "✅ Double confirmation required (type 'DELETE' + 'yes')",
        "✅ Shows environment paths and Python versions",
        "✅ Comprehensive error handling and validation"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📝 Usage Examples:")
    print("  [1,3,5]     - Delete environments 1, 3, and 5")
    print("  [2,4-7]     - Delete environment 2 and range 4-7") 
    print("  [1,3-5,8]   - Delete 1, range 3-5, and 8")
    print("  1,3,5       - Same as [1,3,5] (brackets optional)")
    
    print("\n🛡️  Safety Features:")
    print("  • Base/root environments are protected")
    print("  • Double confirmation required")
    print("  • Clear warnings about permanent deletion")
    print("  • Shows full environment paths")
    print("  • Empty input cancels operation")
    
    print("\n⚠️  WARNING:")
    print("  Environment deletion is PERMANENT and cannot be undone!")
    print("  Always ensure you have backups of important environments.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_environment_deletion()
    else:
        show_feature_summary()
        print(f"\nTo run the safe demo: python {sys.argv[0]} --demo")
