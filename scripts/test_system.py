#!/usr/bin/env python3
"""
Simple test script to validate core system structure without external dependencies
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Test that all required directories and files exist."""
    print("🧪 Testing project structure...")
    
    required_dirs = [
        ".vscode",
        "core/data_acquisition",
        "core/processing", 
        "core/models",
        "core/analysis",
        "core/utils",
        "sports/mlb",
        "sports/nfl",
        "sports/nba",
        "sports/nhl",
        "sports/soccer",
        "sports/tennis",
        "sports/golf",
        "sports/mma",
        "google_apps_script",
        "api",
        "scripts",
        "tests"
    ]
    
    required_files = [
        ".vscode/settings.json",
        ".vscode/tasks.json",
        ".vscode/launch.json",
        ".vscode/extensions.json",
        "core/utils/logger.py",
        "core/utils/rate_limiter.py",
        "core/data_acquisition/api_manager.py",
        "core/processing/data_processor.py",
        "core/analysis/base_analyzer.py",
        "core/analysis/ev_calculator.py",
        "core/models/base_model.py",
        "sports/mlb/mlb_analyzer.py",
        "sports/nfl/nfl_analyzer.py",
        "google_apps_script/ultra_system_multi_sport.js",
        "api/main.py",
        "scripts/setup.py",
        "scripts/data_refresh.py",
        "scripts/create_sport_module.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Check directories
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    # Check files
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required directories and files exist")
    return True

def test_python_syntax():
    """Test that all Python files have valid syntax."""
    print("🧪 Testing Python syntax...")
    
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip virtual environment and cache directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            # Skip encoding or other non-syntax errors
            pass
    
    if syntax_errors:
        print(f"❌ Syntax errors found:")
        for error in syntax_errors:
            print(f"   {error}")
        return False
    
    print(f"✅ All {len(python_files)} Python files have valid syntax")
    return True

def test_vscode_configuration():
    """Test VS Code configuration files."""
    print("🧪 Testing VS Code configuration...")
    
    import json
    
    config_files = [
        (".vscode/settings.json", "VS Code settings"),
        (".vscode/tasks.json", "VS Code tasks"),
        (".vscode/launch.json", "VS Code launch config"),
        (".vscode/extensions.json", "VS Code extensions"),
        (".vscode/snippets/python.json", "Python snippets"),
        (".vscode/snippets/javascript.json", "JavaScript snippets")
    ]
    
    for file_path, description in config_files:
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ {description} is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ {description} has invalid JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {description} not found: {file_path}")
            return False
    
    return True

def test_google_apps_script():
    """Test Google Apps Script file."""
    print("🧪 Testing Google Apps Script...")
    
    gas_file = "google_apps_script/ultra_system_multi_sport.js"
    
    if not Path(gas_file).exists():
        print(f"❌ Google Apps Script file not found: {gas_file}")
        return False
    
    with open(gas_file, 'r') as f:
        content = f.read()
    
    # Check for key functions
    required_functions = [
        "initializeUltraSystem",
        "refreshAllSportsData", 
        "refreshSportData",
        "makeApiRequest",
        "setupAllTriggers"
    ]
    
    missing_functions = []
    for func in required_functions:
        if f"function {func}" not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ Missing Google Apps Script functions: {missing_functions}")
        return False
    
    print("✅ Google Apps Script file contains all required functions")
    return True

def test_documentation():
    """Test documentation completeness."""
    print("🧪 Testing documentation...")
    
    readme_path = "README.md"
    if not Path(readme_path).exists():
        print(f"❌ README.md not found")
        return False
    
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    required_sections = [
        "# Ultra Sports Betting System",
        "## 🏆 Features",
        "## 🚀 Quick Start", 
        "## 📁 Project Structure",
        "## 🎯 Core Components",
        "## 📊 Google Apps Script Integration",
        "## 🏈 Sport-Specific Features",
        "## 📈 API Endpoints"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in readme_content:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Missing README sections: {missing_sections}")
        return False
    
    print("✅ README.md contains all required sections")
    return True

def main():
    """Run all tests."""
    print("🚀 Running Ultra Sports Betting System Tests\n")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Python Syntax", test_python_syntax),
        ("VS Code Configuration", test_vscode_configuration),
        ("Google Apps Script", test_google_apps_script),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())