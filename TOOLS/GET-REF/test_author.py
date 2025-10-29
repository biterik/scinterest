#!/usr/bin/env python3
"""
test_author.py - Test different author name formats for Scopus

Usage: ./test_author.py "Bitzek, Erik"
"""

import sys
import os

if len(sys.argv) < 2:
    print("Usage: ./test_author.py \"LastName, FirstName\"")
    sys.exit(1)

author = sys.argv[1]

# Set up API key
api_key = os.environ.get('SCOPUS_API_KEY')
if not api_key:
    print("ERROR: No SCOPUS_API_KEY in environment")
    sys.exit(1)

os.environ['SCOPUS_API_KEY'] = api_key

# Initialize if needed
try:
    from pybliometrics.scopus import init
    try:
        init(keys=[api_key])
    except:
        pass
except ImportError:
    pass

from pybliometrics.scopus import ScopusSearch

print("="*70)
print(f"Testing author: {author}")
print("="*70)
print()

# Parse the name
if ',' in author:
    parts = [p.strip() for p in author.split(',')]
    last = parts[0]
    first = parts[1] if len(parts) > 1 else ""
else:
    parts = author.split()
    last = parts[-1]
    first = ' '.join(parts[:-1])

# Try different formats
formats_to_try = [
    (f'{last}, {first}', f'AUTHOR-NAME({last}, {first})'),
    (f'{last}, {first[0]}.', f'AUTHOR-NAME({last}, {first[0]}.)'),
    (f'{last}, {first[0]}', f'AUTHOR-NAME({last}, {first[0]})'),
    (f'{last}', f'AUTHOR-NAME({last})'),
]

results_found = []

for name_format, query in formats_to_try:
    print(f"Trying: {name_format}")
    print(f"Query:  {query}")
    
    try:
        search = ScopusSearch(query, view='COMPLETE')
        results = search.results
        
        if results:
            count = len(results)
            print(f"✓ Found {count} publications")
            results_found.append((name_format, query, count))
            
            # Show first result
            if results:
                r = results[0]
                print(f"  First result: {r.title[:60]}...")
        else:
            print("✗ No results")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

print("="*70)
print("SUMMARY")
print("="*70)
print()

if results_found:
    print("Working formats:")
    for name_format, query, count in results_found:
        print(f"  {name_format:30s} → {count:4d} publications")
    
    print()
    print("✓ Use this with getref.py:")
    best_format, best_query, best_count = results_found[0]
    print(f'  ./getref.py -name "{best_format}" -start 2000')
else:
    print("✗ No publications found with any format")
    print()
    print("Possible issues:")
    print("  - Author name spelling")
    print("  - Author not in Scopus database")
    print("  - API key issues")
    print()
    print("Try searching on scopus.com first to verify the author exists")
