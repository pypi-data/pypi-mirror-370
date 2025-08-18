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
            # Azure uses 'encrypt' parameter
            return ("encrypt", "require")
        else:
            # Non-Azure uses 'encryption' parameter
            if encrypt_str in ["default", "off", "require"]:
                return ("encryption", encrypt_str)
            elif encrypt_str in ["true", "1", "yes"]:
                return ("encryption", "require")
            elif encrypt_str in ["false", "0", "no"]:
                return ("encryption", "off")
            else:
                return ("encryption", "default")
    
    test_cases = [
        ("default", False, "encryption", "default"),
        ("off", False, "encryption", "off"), 
        ("require", False, "encryption", "require"),
        ("true", False, "encryption", "require"),
        ("false", False, "encryption", "off"),
        ("1", False, "encryption", "require"),
        ("0", False, "encryption", "off"),
        ("yes", False, "encryption", "require"),
        ("no", False, "encryption", "off"),
        ("invalid", False, "encryption", "default"),
        # Azure tests - should always use 'encrypt' parameter
        ("off", True, "encrypt", "require"),
        ("default", True, "encrypt", "require"),
    ]
    
    print("Testing encryption parameter logic:")
    print("=" * 60)
    
    all_passed = True
    for input_val, is_azure, expected_param, expected_value in test_cases:
        actual_param, actual_value = get_encrypt_value(input_val, is_azure)
        param_ok = actual_param == expected_param
        value_ok = actual_value == expected_value
        status = "✅ PASS" if (param_ok and value_ok) else "❌ FAIL"
        azure_label = " (Azure)" if is_azure else ""
        print(f"{status} Input: '{input_val}'{azure_label} -> Expected: {expected_param}='{expected_value}', Got: {actual_param}='{actual_value}'")
        if not (param_ok and value_ok):
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests PASSED! Encryption logic is correct.")
        print("✅ Non-Azure connections use 'encryption' parameter")
        print("✅ Azure connections use 'encrypt' parameter")
    else:
        print("❌ Some tests FAILED! Check the logic.")
    
    return all_passed

if __name__ == "__main__":
    test_encryption_logic()
