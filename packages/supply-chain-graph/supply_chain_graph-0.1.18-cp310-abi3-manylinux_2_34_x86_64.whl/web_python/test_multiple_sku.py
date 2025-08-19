#!/usr/bin/env python3

import sys
import os

# Add the parent directory to the path to import supply
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import supply
    print("✅ Successfully imported supply module")
    
    # Test the function directly
    print("Testing get_multiple_sku_daily_measures function...")
    
    # Test with empty list first
    try:
        result = supply.get_multiple_sku_daily_measures([], "2024-01-01", None)
        print(f"✅ Empty list test passed: {result}")
    except Exception as e:
        print(f"❌ Empty list test failed: {e}")
    
    # Test with non-existent SKU
    try:
        result = supply.get_multiple_sku_daily_measures(["non_existent_sku"], "2024-01-01", None)
        print(f"✅ Non-existent SKU test passed: {result}")
    except Exception as e:
        print(f"❌ Non-existent SKU test failed: {e}")
    
    # Test with None values
    try:
        result = supply.get_multiple_sku_daily_measures(None, "2024-01-01", None)
        print(f"✅ None values test passed: {result}")
    except Exception as e:
        print(f"❌ None values test failed: {e}")
        
except ImportError as e:
    print(f"❌ Failed to import supply module: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc() 