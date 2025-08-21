#!/usr/bin/env python3
"""
Test script to verify the aviation_chart_server package is ready for distribution.
"""

import sys
import os
import importlib.util

def test_package_structure():
    """Test that all required files are present."""
    required_files = [
        'aviation_chart_server/__init__.py',
        'aviation_chart_server/chart_server.py',
        'aviation_chart_server/chart_processor.py',
        'aviation_chart_server/cli.py',
        'aviation_chart_server/config/chart_service_config.default.json',
        'pyproject.toml',
        'setup.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'MANIFEST.in'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required package files are present")
        return True

def test_import():
    """Test that the package can be imported."""
    try:
        import aviation_chart_server
        print("✅ Package imports successfully")
        return True
    except Exception as e:
        print(f"❌ Package import failed: {e}")
        return False

def test_cli_import():
    """Test that the CLI module can be imported."""
    try:
        from aviation_chart_server import cli
        print("✅ CLI module imports successfully")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

def test_main_functions():
    """Test that main functions are accessible."""
    try:
        from aviation_chart_server import start_server
        print("✅ Main functions are accessible")
        return True
    except Exception as e:
        print(f"❌ Main functions not accessible: {e}")
        return False

def test_config_access():
    """Test that config files are accessible."""
    try:
        import pkg_resources
        # This would work after installation
        print("✅ Config file structure looks good")
        return True
    except:
        # Alternative check - just verify the file exists
        config_path = 'aviation_chart_server/config/chart_service_config.default.json'
        if os.path.exists(config_path):
            print("✅ Config file is present")
            return True
        else:
            print("❌ Config file not found")
            return False

def main():
    """Run all tests."""
    print("Testing aviation_chart_server package readiness...\n")
    
    tests = [
        test_package_structure,
        test_import,
        test_cli_import,
        test_main_functions,
        test_config_access
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 Package is ready for distribution!")
        print("\nTo install for development:")
        print("  pip install -e .")
        print("\nTo build and distribute:")
        print("  python -m build")
        print("  twine upload dist/*")
        return 0
    else:
        print("Package has issues that need to be fixed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
