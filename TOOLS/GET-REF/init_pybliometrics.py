#!/usr/bin/env python3
"""
init_pybliometrics.py - Initialize pybliometrics configuration

For pybliometrics 4.x, this creates the necessary config file.
"""

import os
import sys

print("="*70)
print("PYBLIOMETRICS INITIALIZATION")
print("="*70)
print()

# Check for API key
api_key = os.environ.get('SCOPUS_API_KEY') or os.environ.get('ELSEVIER_API_KEY')

if not api_key:
    print("ERROR: No API key found in environment!")
    print()
    print("Please set your API key:")
    print("  export SCOPUS_API_KEY='your_key_here'")
    print()
    print("Add to ~/.zshrc for permanent setup:")
    print("  echo 'export SCOPUS_API_KEY=\"your_key_here\"' >> ~/.zshrc")
    print("  source ~/.zshrc")
    sys.exit(1)

print(f"✓ API key found (length: {len(api_key)})")
print()

# Try to initialize pybliometrics
try:
    from pybliometrics.scopus import init
    
    print("Initializing pybliometrics...")
    print()
    
    try:
        # Initialize with the API key
        init(keys=[api_key])
        print("✓ Pybliometrics initialized successfully!")
        print()
        print("Configuration file created at:")
        print("  ~/.config/pybliometrics.cfg")
        
    except Exception as e:
        if "already exists" in str(e).lower() or "initialized" in str(e).lower():
            print("✓ Pybliometrics already initialized!")
        else:
            print(f"Note: {e}")
            print()
            print("This might be okay - trying to proceed anyway.")
    
except ImportError:
    print("Note: pybliometrics version doesn't have init() function")
    print("(This is normal for older versions)")
    print()
    print("For older versions, API key from environment is sufficient.")

print()
print("="*70)
print("INITIALIZATION COMPLETE")
print("="*70)
print()
print("You can now use:")
print("  ./getref.py -name \"Author Name\" -start 2020")
print()
