#!/usr/bin/env python3
"""
getref.py - IMPROVED VERSION with 404 fallback

This version uses search result data when AbstractRetrieval returns 404,
ensuring you get ALL publications found, not just the ones with full details available.

Changes from original:
- Extracts data from search results directly
- Falls back to search data when AbstractRetrieval fails (404)
- Gets abstracts/keywords when available, but doesn't lose publications when unavailable
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval

# Handle different pybliometrics versions for exception handling
try:
    from pybliometrics.scopus.exception import Scopus404Error
except (ImportError, ModuleNotFoundError):
    Scopus404Error = Exception

# Handle config for different pybliometrics versions
try:
    from pybliometrics.scopus.utils import config
    HAS_CONFIG = True
except (ImportError, ModuleNotFoundError):
    HAS_CONFIG = False
    config = None


def setup_api_key():
    """Setup Scopus API key and initialize pybliometrics"""
    api_key = os.environ.get('SCOPUS_API_KEY') or os.environ.get('ELSEVIER_API_KEY')
    
    if not api_key:
        if HAS_CONFIG and config:
            try:
                existing_key = config.get('Authentication', 'APIKey')
                if existing_key and existing_key != '':
                    api_key = existing_key
            except:
                pass
    
    if not api_key:
        print("ERROR: No Scopus API key found!", file=sys.stderr)
        print("Please set SCOPUS_API_KEY in your environment:", file=sys.stderr)
        print("  export SCOPUS_API_KEY='your_key_here'", file=sys.stderr)
        sys.exit(1)
    
    os.environ['SCOPUS_API_KEY'] = api_key
    
    # For pybliometrics 4.x, initialize the library
    try:
        from pybliometrics.scopus import init
        try:
            init(keys=[api_key])
        except Exception as e:
            pass
    except (ImportError, ModuleNotFoundError):
        if HAS_CONFIG and config:
            try:
                config['Authentication']['APIKey'] = api_key
            except:
                pass
    
    return True


def build_query(name=None, orcid=None, institution=None, start_year=None, end_year=None):
    """Build Scopus search query from parameters"""
    if orcid:
        query = f'ORCID({orcid})'
    elif name:
        if ',' not in name:
            parts = name.strip().split()
            if len(parts) >= 2:
                last = parts[-1]
                first = ' '.join(parts[:-1])
                name = f"{last}, {first}"
        query = f'AUTHOR-NAME({name})'
    elif institution:
        query = f'AFFIL({institution})'
    else:
        raise ValueError("Must specify -name, -orcid, or -institution")
    
    if start_year and end_year:
        query += f' AND PUBYEAR > {start_year - 1} AND PUBYEAR < {end_year + 1}'
    elif start_year:
        query += f' AND PUBYEAR > {start_year - 1}'
    elif end_year:
        query += f' AND PUBYEAR < {end_year + 1}'
    
    return query


def generate_filename(name=None, orcid=None, institution=None, start_year=None, end_year=None):
    """Generate output filename based on search parameters"""
    if orcid:
        base = f"ORCID_{orcid.replace('-', '_')}"
    elif name:
        base = name.replace(',', '').replace('.', '').replace(' ', '_')
        while '__' in base:
            base = base.replace('__', '_')
        base = base.strip('_')
    elif institution:
        base = institution.replace(' ', '_').replace('.', '')
    else:
        base = "publications"
    
    if start_year and end_year:
        base += f"_{start_year}-{end_year}"
    elif start_year:
        base += f"_{start_year}-present"
    elif end_year:
        base += f"_until-{end_year}"
    
    return base


def extract_from_search_result(result):
    """
    Extract publication data from search result (fallback when AbstractRetrieval fails)
    """
    try:
        record = {
            'eid': result.eid if hasattr(result, 'eid') else None,
            'doi': result.doi if hasattr(result, 'doi') else None,
            'title': result.title if hasattr(result, 'title') else None,
            'abstract': None,  # Not in search results
            'journal': result.publicationName if hasattr(result, 'publicationName') else None,
            'year': int(result.coverDate.split('-')[0]) if hasattr(result, 'coverDate') and result.coverDate else None,
            'date': result.coverDate if hasattr(result, 'coverDate') else None,
            'volume': result.volume if hasattr(result, 'volume') else None,
            'issue': result.issueIdentifier if hasattr(result, 'issueIdentifier') else None,
            'pages': result.pageRange if hasattr(result, 'pageRange') else None,
            'citation_count': int(result.citedby_count) if hasattr(result, 'citedby_count') and result.citedby_count else 0,
            'document_type': result.aggregationType if hasattr(result, 'aggregationType') else None,
            'issn': result.issn if hasattr(result, 'issn') else None,
            'isbn': None,
            'publisher': None,
            'source_id': result.source_id if hasattr(result, 'source_id') else None,
            'keywords': [],  # Not in search results
        }
        
        # Extract authors
        authors = []
        if hasattr(result, 'author_names') and result.author_names:
            for author_name in result.author_names.split(';'):
                author_name = author_name.strip()
                if ',' in author_name:
                    parts = author_name.split(',')
                    surname = parts[0].strip()
                    given = parts[1].strip() if len(parts) > 1 else ''
                else:
                    parts = author_name.split()
                    surname = parts[-1] if parts else author_name
                    given = ' '.join(parts[:-1]) if len(parts) > 1 else ''
                
                authors.append({
                    'name': author_name,
                    'surname': surname,
                    'given_name': given,
                    'author_id': None,
                    'affiliation': None
                })
        
        record['authors'] = authors
        
        # Build URL
        if record['doi']:
            record['url'] = f"https://doi.org/{record['doi']}"
        else:
            record['url'] = f"https://www.scopus.com/record/display.uri?eid={record['eid']}&origin=resultslist"
        
        return record
        
    except Exception as e:
        return None


def get_full_details(eid):
    """
    Try to get full details with AbstractRetrieval (includes abstract, keywords)
    Returns None if fails (404)
    """
    try:
        time.sleep(0.1)  # Rate limiting
        abstract = AbstractRetrieval(eid, view='FULL')
        
        # Extract authors
        authors = []
        if abstract.authors:
            for author in abstract.authors:
                authors.append({
                    'name': f"{author.given_name} {author.surname}" if author.given_name else author.surname,
                    'surname': author.surname,
                    'given_name': author.given_name,
                    'author_id': author.auid if hasattr(author, 'auid') else None,
                    'affiliation': author.affiliation if hasattr(author, 'affiliation') else None
                })
        
        # Extract keywords
        keywords = []
        if abstract.authkeywords:
            keywords = [kw.strip() for kw in abstract.authkeywords.split(' | ')]
        
        record = {
            'eid': eid,
            'doi': abstract.doi if abstract.doi else None,
            'title': abstract.title,
            'abstract': abstract.abstract if abstract.abstract else None,
            'journal': abstract.publicationName if abstract.publicationName else None,
            'year': int(abstract.coverDate.split('-')[0]) if abstract.coverDate else None,
            'date': abstract.coverDate if abstract.coverDate else None,
            'volume': abstract.volume if abstract.volume else None,
            'issue': abstract.issueIdentifier if abstract.issueIdentifier else None,
            'pages': abstract.pageRange if abstract.pageRange else None,
            'authors': authors,
            'keywords': keywords,
            'citation_count': int(abstract.citedby_count) if abstract.citedby_count else 0,
            'document_type': abstract.aggregationType if abstract.aggregationType else None,
            'issn': abstract.issn if abstract.issn else None,
            'isbn': abstract.isbn if abstract.isbn else None,
            'publisher': abstract.publisher if abstract.publisher else None,
            'source_id': abstract.source_id if abstract.source_id else None,
            'url': f"https://doi.org/{abstract.doi}" if abstract.doi else f"https://www.scopus.com/record/display.uri?eid={eid}&origin=resultslist"
        }
        
        return record
        
    except:
        return None  # Fall back to search result data


def search_and_download(query, limit=None, verbose=False):
    """Search Scopus and download publications with 404 fallback"""
    print(f"Searching with query: {query}", file=sys.stderr)
    
    try:
        search = ScopusSearch(query, view='COMPLETE', download=True)
        results = search.results
        
        if not results:
            print("No publications found", file=sys.stderr)
            return []
        
        total = len(results)
        if limit:
            results = results[:limit]
        
        print(f"Found {total} publications, retrieving details...", file=sys.stderr)
        
        publications = []
        full_details_count = 0
        search_only_count = 0
        failed_count = 0
        
        for i, result in enumerate(results, 1):
            print(f"  [{i}/{total}] Processing...", file=sys.stderr, end='\r')
            
            # Try to get full details first
            details = get_full_details(result.eid)
            
            # If that fails, use search result data
            if details is None:
                details = extract_from_search_result(result)
                if details:
                    search_only_count += 1
                else:
                    failed_count += 1
            else:
                full_details_count += 1
            
            if details:
                publications.append(details)
        
        print(f"\n✓ Retrieved {len(publications)}/{total} publications", file=sys.stderr)
        print(f"  • {full_details_count} with full details (abstract + keywords)", file=sys.stderr)
        print(f"  • {search_only_count} with basic info (no abstract/keywords)", file=sys.stderr)
        if failed_count > 0:
            print(f"  • {failed_count} could not be retrieved", file=sys.stderr)
        
        return publications
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []


def save_json(publications, filename):
    """Save publications to JSON"""
    if not filename.endswith('.json'):
        filename += '.json'
    
    output = {
        'metadata': {
            'retrieved_at': datetime.now().isoformat(),
            'total_publications': len(publications),
            'source': 'Scopus API via pybliometrics',
            'format_version': '1.0'
        },
        'publications': publications
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return filename


def main():
    parser = argparse.ArgumentParser(description='Download publications from Scopus API')
    
    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument('-name', '--name', help='Author name')
    search_group.add_argument('-orcid', '--orcid', help='ORCID identifier')
    search_group.add_argument('-institution', '--institution', '--affiliation', help='Institution name')
    
    parser.add_argument('-start', '--start-year', type=int, help='Start year')
    parser.add_argument('-end', '--end-year', type=int, help='End year')
    parser.add_argument('-output', '-o', '--output', help='Output filename')
    parser.add_argument('-limit', '--limit', type=int, help='Max results')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    
    args = parser.parse_args()
    
    setup_api_key()
    
    try:
        query = build_query(args.name, args.orcid, args.institution, args.start_year, args.end_year)
    except ValueError as e:
        parser.error(str(e))
    
    filename = args.output if args.output else generate_filename(
        args.name, args.orcid, args.institution, args.start_year, args.end_year
    )
    
    publications = search_and_download(query, args.limit, args.verbose and not args.quiet)
    
    if not publications:
        print("No publications retrieved", file=sys.stderr)
        sys.exit(1)
    
    output_file = save_json(publications, filename)
    
    if not args.quiet:
        print(f"\n✓ Saved {len(publications)} publications to: {output_file}", file=sys.stderr)
        
        years = [p['year'] for p in publications if p['year']]
        if years:
            print(f"Year range: {min(years)} - {max(years)}", file=sys.stderr)
        
        with_doi = sum(1 for p in publications if p['doi'])
        print(f"Publications with DOI: {with_doi}/{len(publications)}", file=sys.stderr)
        
        with_abstract = sum(1 for p in publications if p['abstract'])
        print(f"Publications with abstract: {with_abstract}/{len(publications)}", file=sys.stderr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
