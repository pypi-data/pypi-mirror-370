#!/usr/bin/env python3
"""
Test script to verify encryption parameter handling
"""
import os
import sys
sys.path.insert(0, 'src')

def test_encryption_values():
    """Test different encryption values"""
    from mssql_mcp_server_ishaan.server import get_connection_config
    
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
    
    # Set basic required env vars
    os.environ["MSSQL_SERVER"] = "test-server"
    os.environ["MSSQL_DATABASE"] = "test-db"
    os.environ["MSSQL_USERNAME"] = "test-user"
    os.environ["MSSQL_PASSWORD"] = "test-pass"
    
    print("Testing encryption parameter handling:")
    print("=" * 50)
    
    for input_val, expected in test_cases:
        os.environ["MSSQL_ENCRYPT"] = input_val
        try:
            config = get_connection_config()
            actual = config.get("encrypt", "NOT_SET")
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            print(f"{status} Input: '{input_val}' -> Expected: '{expected}', Got: '{actual}'")
        except Exception as e:
            print(f"❌ ERROR Input: '{input_val}' -> Exception: {e}")
    
    # Test Azure SQL (should always be 'require')
    print("\nTesting Azure SQL encryption:")
    print("=" * 30)
    os.environ["MSSQL_SERVER"] = "test.database.windows.net"
    os.environ["MSSQL_ENCRYPT"] = "off"  # Should be overridden
    
    try:
        config = get_connection_config()
        actual = config.get("encrypt", "NOT_SET")
        expected = "require"
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{status} Azure SQL -> Expected: '{expected}', Got: '{actual}'")
        
        # Check TDS version is set
        tds_version = config.get("tds_version", "NOT_SET")
        tds_expected = "7.4"
        tds_status = "✅ PASS" if tds_version == tds_expected else "❌ FAIL"
        print(f"{tds_status} Azure TDS Version -> Expected: '{tds_expected}', Got: '{tds_version}'")
        
    except Exception as e:
        print(f"❌ ERROR Azure SQL test -> Exception: {e}")

if __name__ == "__main__":
    test_encryption_values()
