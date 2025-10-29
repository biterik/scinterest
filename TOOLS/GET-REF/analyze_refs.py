#!/usr/bin/env python3
"""
analyze_refs.py - Analyze publications from getref.py JSON output

Usage:
    analyze_refs.py publications.json
    analyze_refs.py publications.json -keywords
    analyze_refs.py publications.json -dois
    analyze_refs.py publications.json -summary
"""

import json
import sys
import argparse
from collections import Counter
from datetime import datetime


def load_publications(filename):
    """Load publications from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}", file=sys.stderr)
        sys.exit(1)


def print_summary(data):
    """Print summary statistics"""
    metadata = data['metadata']
    publications = data['publications']
    
    print("=" * 60)
    print("PUBLICATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal publications: {metadata['total_publications']}")
    print(f"Retrieved: {metadata['retrieved_at']}")
    
    # Year distribution
    years = [p['year'] for p in publications if p['year']]
    if years:
        year_counts = Counter(years)
        print(f"\nYear range: {min(years)} - {max(years)}")
        print("\nPublications by year:")
        for year in sorted(year_counts.keys()):
            print(f"  {year}: {year_counts[year]}")
    
    # Citation statistics
    citations = [p['citation_count'] for p in publications if p['citation_count'] is not None]
    if citations:
        print(f"\nCitation statistics:")
        print(f"  Total citations: {sum(citations)}")
        print(f"  Average per paper: {sum(citations)/len(citations):.1f}")
        print(f"  Most cited: {max(citations)}")
        print(f"  Median: {sorted(citations)[len(citations)//2]}")
    
    # Data completeness
    with_doi = sum(1 for p in publications if p['doi'])
    with_abstract = sum(1 for p in publications if p['abstract'])
    with_keywords = sum(1 for p in publications if p['keywords'])
    
    print(f"\nData completeness:")
    print(f"  With DOI: {with_doi}/{len(publications)} ({100*with_doi/len(publications):.1f}%)")
    print(f"  With abstract: {with_abstract}/{len(publications)} ({100*with_abstract/len(publications):.1f}%)")
    print(f"  With keywords: {with_keywords}/{len(publications)} ({100*with_keywords/len(publications):.1f}%)")
    
    # Document types
    doc_types = Counter(p['document_type'] for p in publications if p['document_type'])
    if doc_types:
        print(f"\nDocument types:")
        for dtype, count in doc_types.most_common():
            print(f"  {dtype}: {count}")
    
    # Top journals
    journals = Counter(p['journal'] for p in publications if p['journal'])
    if journals:
        print(f"\nTop journals:")
        for journal, count in journals.most_common(10):
            print(f"  {journal}: {count}")


def print_dois(publications):
    """Print all DOIs"""
    print("DOIs:")
    print("-" * 60)
    for pub in publications:
        if pub['doi']:
            print(pub['doi'])


def print_doi_urls(publications):
    """Print all DOI URLs"""
    print("DOI URLs:")
    print("-" * 60)
    for pub in publications:
        if pub['doi']:
            print(f"https://doi.org/{pub['doi']}")


def print_keywords(publications):
    """Print keyword analysis"""
    all_keywords = []
    for pub in publications:
        if pub['keywords']:
            all_keywords.extend(pub['keywords'])
    
    if not all_keywords:
        print("No keywords found")
        return
    
    keyword_counts = Counter(all_keywords)
    
    print(f"Keyword Analysis:")
    print("-" * 60)
    print(f"Total keywords: {len(all_keywords)}")
    print(f"Unique keywords: {len(keyword_counts)}")
    print(f"\nMost common keywords:")
    for keyword, count in keyword_counts.most_common(20):
        print(f"  {count:3d}  {keyword}")


def print_highly_cited(publications, threshold=10):
    """Print highly cited papers"""
    highly_cited = [p for p in publications if p['citation_count'] >= threshold]
    highly_cited.sort(key=lambda x: x['citation_count'], reverse=True)
    
    print(f"Highly Cited Papers (≥{threshold} citations):")
    print("-" * 60)
    for pub in highly_cited:
        print(f"\n[{pub['citation_count']} citations] {pub['title']}")
        print(f"  {pub['journal']}, {pub['year']}")
        if pub['doi']:
            print(f"  https://doi.org/{pub['doi']}")


def export_bibtex(publications, output_file=None):
    """Export to BibTeX format"""
    output = []
    
    for i, pub in enumerate(publications, 1):
        # Generate citation key
        first_author = pub['authors'][0]['surname'] if pub['authors'] else 'Unknown'
        year = pub['year'] if pub['year'] else 'nd'
        key = f"{first_author}{year}"
        
        # Determine entry type
        doc_type = pub['document_type'].lower() if pub['document_type'] else 'article'
        if 'conference' in doc_type:
            entry_type = 'inproceedings'
        elif 'book' in doc_type:
            entry_type = 'book'
        else:
            entry_type = 'article'
        
        # Build BibTeX entry
        bibtex = f"@{entry_type}{{{key}{i},\n"
        
        if pub['title']:
            bibtex += f"  title = {{{pub['title']}}},\n"
        
        if pub['authors']:
            authors_str = ' and '.join(a['name'] for a in pub['authors'])
            bibtex += f"  author = {{{authors_str}}},\n"
        
        if pub['journal']:
            bibtex += f"  journal = {{{pub['journal']}}},\n"
        
        if pub['year']:
            bibtex += f"  year = {{{pub['year']}}},\n"
        
        if pub['volume']:
            bibtex += f"  volume = {{{pub['volume']}}},\n"
        
        if pub['issue']:
            bibtex += f"  number = {{{pub['issue']}}},\n"
        
        if pub['pages']:
            bibtex += f"  pages = {{{pub['pages']}}},\n"
        
        if pub['doi']:
            bibtex += f"  doi = {{{pub['doi']}}},\n"
        
        bibtex += "}\n"
        output.append(bibtex)
    
    result = '\n'.join(output)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Exported {len(publications)} entries to {output_file}")
    else:
        print(result)


def list_publications(publications, format='simple'):
    """List all publications"""
    print("Publications:")
    print("=" * 60)
    
    for i, pub in enumerate(publications, 1):
        if format == 'simple':
            authors = ', '.join(a['name'] for a in pub['authors'][:3])
            if len(pub['authors']) > 3:
                authors += ' et al.'
            print(f"\n{i}. {pub['title']}")
            print(f"   {authors}")
            print(f"   {pub['journal']}, {pub['year']}")
            if pub['doi']:
                print(f"   DOI: {pub['doi']}")
        
        elif format == 'detailed':
            print(f"\n{'='*60}")
            print(f"[{i}] {pub['title']}")
            print(f"{'='*60}")
            
            authors = ', '.join(a['name'] for a in pub['authors'])
            print(f"Authors: {authors}")
            print(f"Journal: {pub['journal']}")
            print(f"Year: {pub['year']}")
            print(f"Citations: {pub['citation_count']}")
            
            if pub['keywords']:
                print(f"Keywords: {', '.join(pub['keywords'])}")
            
            if pub['doi']:
                print(f"DOI: https://doi.org/{pub['doi']}")
            
            if pub['abstract']:
                abstract = pub['abstract'][:200] + '...' if len(pub['abstract']) > 200 else pub['abstract']
                print(f"\nAbstract: {abstract}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze publications from getref.py JSON output',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', help='JSON file from getref.py')
    
    # Analysis options
    parser.add_argument('-s', '--summary', action='store_true',
                       help='Show summary statistics (default)')
    parser.add_argument('-k', '--keywords', action='store_true',
                       help='Show keyword analysis')
    parser.add_argument('-d', '--dois', action='store_true',
                       help='List all DOIs')
    parser.add_argument('-u', '--urls', action='store_true',
                       help='List all DOI URLs')
    parser.add_argument('-c', '--highly-cited', type=int, metavar='N',
                       help='Show papers with N or more citations')
    parser.add_argument('-l', '--list', choices=['simple', 'detailed'],
                       help='List all publications')
    parser.add_argument('-b', '--bibtex', metavar='OUTPUT',
                       help='Export to BibTeX format')
    
    args = parser.parse_args()
    
    # Load data
    data = load_publications(args.file)
    publications = data['publications']
    
    # Execute requested analysis
    if args.keywords:
        print_keywords(publications)
    elif args.dois:
        print_dois(publications)
    elif args.urls:
        print_doi_urls(publications)
    elif args.highly_cited:
        print_highly_cited(publications, args.highly_cited)
    elif args.list:
        list_publications(publications, args.list)
    elif args.bibtex:
        export_bibtex(publications, args.bibtex)
    else:
        # Default: show summary
        print_summary(data)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
