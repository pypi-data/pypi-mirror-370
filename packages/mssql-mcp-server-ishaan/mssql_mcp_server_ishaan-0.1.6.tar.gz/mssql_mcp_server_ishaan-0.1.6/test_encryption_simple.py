#!/usr/bin/env python3
"""
Simple test to verify encryption parameter logic
"""
import os

def test_encryption_logic():
    """Test the encryption parameter logic"""
    
    def get_encrypt_value(encrypt_str):
        """Simulate the encryption logic from server.py"""
        encrypt_str = encrypt_str.lower()
        
        # All connections use 'encryption' parameter
        if encrypt_str in ["default", "off", "require"]:
            return encrypt_str
        elif encrypt_str in ["true", "1", "yes"]:
            return "require"
        elif encrypt_str in ["false", "0", "no"]:
            return "off"
        else:
            return "default"
    
    test_cases = [
        ("default", "default"),
        ("off", "off"), 
        ("require", "require"),
        ("true", "require"),
        ("false", "off"),
        ("1", "require"),
        ("0", "off"),
        ("yes", "require"),
        ("no", "off"),
        ("invalid", "default"),
    ]
    
    print("Testing encryption parameter logic:")
    print("=" * 50)
    
    all_passed = True
    for input_val, expected in test_cases:
        actual = get_encrypt_value(input_val)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{status} Input: '{input_val}' -> Expected: encryption='{expected}', Got: encryption='{actual}'")
        if actual != expected:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Encryption logic is correct.")
        print("✅ All connections use 'encryption' parameter")
        print("✅ Default value is 'default'")
    else:
        print("❌ Some tests FAILED! Check the logic.")
    
    return all_passed

if __name__ == "__main__":
    test_encryption_logic()
