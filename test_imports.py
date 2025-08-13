#!/usr/bin/env python3
"""
Test script to verify all imports work for automation_manager.py
This helps debug GitHub Actions environment issues.
"""

import sys

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        package = package_name or module_name
        print(f"❌ {module_name} - MISSING (install: pip install {package})")
        print(f"   Error: {e}")
        return False

def main():
    print("Testing imports for automation_manager.py...")
    print("=" * 50)
    
    # Core imports
    modules_to_test = [
        ("yaml", "PyYAML"),
        ("schedule", "schedule"),
        ("rich", "rich"),
        ("questionary", "questionary"),
        ("feedparser", "feedparser"),
        ("bs4", "beautifulsoup4"),
        ("lxml", "lxml"),
        ("requests", "requests"),
    ]
    
    failed_imports = []
    
    for module, package in modules_to_test:
        if not test_import(module, package):
            failed_imports.append((module, package))
    
    print("=" * 50)
    
    if failed_imports:
        print(f"❌ {len(failed_imports)} imports failed:")
        for module, package in failed_imports:
            print(f"   - {module} (pip install {package})")
        return 1
    else:
        print("✅ All imports successful!")
        return 0

if __name__ == "__main__":
    sys.exit(main())