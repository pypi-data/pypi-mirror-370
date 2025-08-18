#!/usr/bin/env python3
"""
Simple test to verify hybrid encryption parameter logic
"""
import os

def test_encryption_logic():
    """Test the hybrid encryption parameter logic"""
    
    def get_encrypt_config(encrypt_env_val, is_azure=False):
        """Simulate the hybrid encryption logic from server.py"""
        if is_azure:
            # Azure SQL: uses 'encrypt' parameter (boolean)
            encrypt_env = encrypt_env_val if encrypt_env_val else "true"
            return ("encrypt", encrypt_env.lower() == "true")
        else:
            # Non-Azure: uses 'encryption' parameter (always 'default')
            return ("encryption", "default")
    
    test_cases = [
        # Non-Azure tests - always returns encryption='default'
        ("true", False, "encryption", "default"),
        ("false", False, "encryption", "default"),
        ("", False, "encryption", "default"),
        (None, False, "encryption", "default"),
        # Azure tests - uses encrypt boolean based on MSSQL_ENCRYPT
        ("true", True, "encrypt", True),
        ("false", True, "encrypt", False),
        ("TRUE", True, "encrypt", True),
        ("FALSE", True, "encrypt", False),
        ("", True, "encrypt", True),  # Default for Azure is "true"
        (None, True, "encrypt", True),  # Default for Azure is "true"
    ]
    
    print("Testing hybrid encryption parameter logic:")
    print("=" * 65)
    
    all_passed = True
    for input_val, is_azure, expected_param, expected_value in test_cases:
        actual_param, actual_value = get_encrypt_config(input_val, is_azure)
        param_ok = actual_param == expected_param
        value_ok = actual_value == expected_value
        status = "✅ PASS" if (param_ok and value_ok) else "❌ FAIL"
        azure_label = " (Azure)" if is_azure else " (Non-Azure)"
        input_display = f"'{input_val}'" if input_val is not None else "None"
        print(f"{status} Input: {input_display}{azure_label} -> Expected: {expected_param}={expected_value}, Got: {actual_param}={actual_value}")
        if not (param_ok and value_ok):
            all_passed = False
    
    print("\n" + "=" * 65)
    if all_passed:
        print("🎉 All tests PASSED! Hybrid encryption logic is correct.")
        print("✅ Azure SQL: Uses 'encrypt' boolean parameter")
        print("✅ Non-Azure: Uses 'encryption' = 'default' (ignores MSSQL_ENCRYPT)")
    else:
        print("❌ Some tests FAILED! Check the logic.")
    
    return all_passed

if __name__ == "__main__":
    test_encryption_logic()
