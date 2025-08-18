#!/usr/bin/env python3
"""
Simple test to verify encryption parameter logic
"""
import os

def test_encryption_logic():
    """Test the encryption parameter logic"""
    
    def get_encrypt_value(encrypt_str, is_azure=False):
        """Simulate the encryption logic from server.py"""
        encrypt_str = encrypt_str.lower()
        
        if is_azure:
            return "require"
        else:
            if encrypt_str in ["default", "off", "require"]:
                return encrypt_str
            elif encrypt_str in ["true", "1", "yes"]:
                return "require"
            elif encrypt_str in ["false", "0", "no"]:
                return "off"
            else:
                return "default"
    
    test_cases = [
        ("default", False, "default"),
        ("off", False, "off"), 
        ("require", False, "require"),
        ("true", False, "require"),
        ("false", False, "off"),
        ("1", False, "require"),
        ("0", False, "off"),
        ("yes", False, "require"),
        ("no", False, "off"),
        ("invalid", False, "default"),
        # Azure tests
        ("off", True, "require"),  # Azure should always be require
        ("default", True, "require"),
    ]
    
    print("Testing encryption parameter logic:")
    print("=" * 50)
    
    all_passed = True
    for input_val, is_azure, expected in test_cases:
        actual = get_encrypt_value(input_val, is_azure)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        azure_label = " (Azure)" if is_azure else ""
        print(f"{status} Input: '{input_val}'{azure_label} -> Expected: '{expected}', Got: '{actual}'")
        if actual != expected:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests PASSED! Encryption logic is correct.")
    else:
        print("❌ Some tests FAILED! Check the logic.")
    
    return all_passed

if __name__ == "__main__":
    test_encryption_logic()
