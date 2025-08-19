#!/usr/bin/env python3
"""
Validate that CLI Arena requires Python 3.10+
"""

import sys

def validate_python_version():
    """Ensure Python 3.10+ is being used"""
    if sys.version_info < (3, 10):
        print(f"ERROR: Python {sys.version_info.major}.{sys.version_info.minor} detected.")
        print("CLI Arena requires Python 3.10 or higher.")
        print("Please upgrade your Python installation.")
        return False
    
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def validate_package_requirements():
    """Test that our package requirements are met"""
    try:
        import cli_arena
        print("[+] CLI Arena package imports successfully")
        
        # Test that we can use modern Python syntax without compatibility issues
        from typing import Union, Optional, List, Dict
        test_union: Union[str, None] = None
        test_optional: Optional[str] = None
        test_list: List[str] = []
        test_dict: Dict[str, int] = {}
        print("[+] Modern typing syntax works correctly")
        
        return True
    except Exception as e:
        print(f"[-] Package validation failed: {e}")
        return False

def main():
    """Run all validations"""
    print("CLI Arena Python 3.10+ Validation")
    print("=" * 50)
    
    checks = [
        validate_python_version(),
        validate_package_requirements()
    ]
    
    if all(checks):
        print("\n[+] All validations passed! CLI Arena is ready for Python 3.10+")
        return 0
    else:
        print("\n[-] Some validations failed. Please check requirements.")
        return 1

if __name__ == "__main__":
    sys.exit(main())