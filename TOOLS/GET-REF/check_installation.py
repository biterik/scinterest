#!/usr/bin/env python3
"""
check_installation.py - Verify scinterest installation and dependencies

Run this to diagnose issues with your setup.
"""

import sys
import os

print("="*70)
print("SCINTEREST INSTALLATION CHECK")
print("="*70)
print()

# Check Python version
print("Python Version:")
print(f"  {sys.version}")
print()

# Check required modules
print("Checking required packages...")
print()

modules_to_check = [
    ('pybliometrics', 'pybliometrics'),
    ('pandas', 'pandas'),
]

all_ok = True

for module_name, import_name in modules_to_check:
    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {module_name:20s} {version}")
    except ImportError as e:
        print(f"✗ {module_name:20s} NOT INSTALLED")
        all_ok = False

print()

# Check pybliometrics structure
print("Checking pybliometrics structure...")
try:
    from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
    print("✓ Core imports work")
    
    # Check for old exception module
    try:
        from pybliometrics.scopus.exception import Scopus404Error
        print("✓ Old exception module found (pybliometrics < 4.0)")
    except (ImportError, ModuleNotFoundError):
        print("✓ New pybliometrics version (no exception module)")
    
    # Check utils
    try:
        from pybliometrics.scopus.utils import config
        print("✓ Config utils available (pybliometrics < 4.0)")
    except (ImportError, ModuleNotFoundError):
        print("✓ No config utils (pybliometrics 4.x - uses environment variables)")
        
except ImportError as e:
    print(f"✗ pybliometrics import failed: {e}")
    all_ok = False

print()

# Check API key
print("Checking API key configuration...")
api_key = os.environ.get('SCOPUS_API_KEY') or os.environ.get('ELSEVIER_API_KEY')

if api_key:
    print(f"✓ API key found in environment (length: {len(api_key)})")
else:
    print("✗ No API key found in environment")
    print("  Set: export SCOPUS_API_KEY='your_key_here'")
    all_ok = False

print()

# Check if pybliometrics is configured (only for older versions)
try:
    from pybliometrics.scopus.utils import config
    try:
        existing_key = config.get('Authentication', 'APIKey')
        if existing_key:
            print(f"✓ API key also configured in pybliometrics config")
    except:
        print("ℹ No API key in pybliometrics config (environment variable will be used)")
except:
    print("ℹ pybliometrics 4.x uses environment variables directly")

print()

# Check scripts
print("Checking scripts...")
scripts = ['getref.py', 'analyze_refs.py']
for script in scripts:
    if os.path.exists(script):
        is_executable = os.access(script, os.X_OK)
        if is_executable:
            print(f"✓ {script:20s} exists and is executable")
        else:
            print(f"⚠ {script:20s} exists but not executable (run: chmod +x {script})")
    else:
        print(f"✗ {script:20s} not found")

print()

# Check if pybliometrics is initialized (for 4.x)
print("Checking pybliometrics initialization...")
try:
    # Try to test if it's initialized by attempting a basic operation
    from pybliometrics.scopus import init
    
    # Check if config file exists
    import pathlib
    config_file = pathlib.Path.home() / '.config' / 'pybliometrics.cfg'
    
    if config_file.exists():
        print("✓ Pybliometrics is initialized (config file exists)")
    else:
        print("⚠ Pybliometrics config file not found")
        print("  Run: ./init_pybliometrics.py")
        all_ok = False
except (ImportError, ModuleNotFoundError):
    print("ℹ Old pybliometrics version (no init required)")

print()

# Summary
print("="*70)
if all_ok:
    print("✓ ALL CHECKS PASSED")
    print()
    print("You're ready to use scinterest!")
    print("Try: ./getref.py -name \"Einstein, Albert\" -limit 5")
else:
    print("✗ SOME CHECKS FAILED")
    print()
    print("Please fix the issues above before using scinterest.")
    print()
    print("Common fixes:")
    print("  - Install missing packages: pip install pybliometrics pandas")
    print("  - Set API key: export SCOPUS_API_KEY='your_key_here'")
    print("  - Make scripts executable: chmod +x getref.py analyze_refs.py")
print("="*70)
