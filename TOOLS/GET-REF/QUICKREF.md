# Quick Reference Card

## getref.py - Download Publications

```bash
# By author name
./getref.py -name "John A. Smith" -start 2020 -end 2025

# By ORCID
./getref.py -orcid "0000-0002-1825-0097" -start 2020

# By institution
./getref.py -institution "MPI SusMat" -limit 100

# Custom output filename
./getref.py -name "Smith, John" -output my_pubs.json

# Quiet mode (no progress)
./getref.py -institution "MIT" -quiet
```

## analyze_refs.py - Analyze Results

```bash
# Summary statistics (default)
./analyze_refs.py John_A_Smith_2020-2025.json

# List all publications
./analyze_refs.py publications.json -list simple
./analyze_refs.py publications.json -list detailed

# Keyword analysis
./analyze_refs.py publications.json -keywords

# Extract DOIs
./analyze_refs.py publications.json -dois

# DOI URLs (clickable links)
./analyze_refs.py publications.json -urls

# Highly cited papers (10+ citations)
./analyze_refs.py publications.json -highly-cited 10

# Export to BibTeX
./analyze_refs.py publications.json -bibtex output.bib
```

## Python Quick Access

```python
import json

# Load publications
with open('publications.json', 'r') as f:
    data = json.load(f)

pubs = data['publications']

# Extract DOIs
dois = [p['doi'] for p in pubs if p['doi']]

# Get all keywords
keywords = []
for p in pubs:
    keywords.extend(p.get('keywords', []))

# Filter by year
recent = [p for p in pubs if p['year'] >= 2023]

# Most cited
top_cited = sorted(pubs, key=lambda x: x['citation_count'], reverse=True)[:10]

# Search by keyword
ml_papers = [p for p in pubs 
             if any('machine learning' in kw.lower() for kw in p.get('keywords', []))]
```

## Using jq (Command-line JSON processor)

```bash
# Extract all DOIs
cat publications.json | jq -r '.publications[].doi' | grep -v null

# Count by year
cat publications.json | jq '.publications | group_by(.year) | map({year: .[0].year, count: length})'

# Top 5 cited papers
cat publications.json | jq '.publications | sort_by(-.citation_count) | .[0:5] | .[] | {title, citations: .citation_count}'

# All unique keywords
cat publications.json | jq -r '.publications[].keywords[]' | sort -u

# Papers from specific journal
cat publications.json | jq '.publications[] | select(.journal | contains("Nature"))'

# Export titles and years to CSV
cat publications.json | jq -r '.publications[] | [.year, .title] | @csv' > titles.csv
```

## Setup Checklist

- [ ] Install dependencies: `pip install pybliometrics pandas`
- [ ] Get Scopus API key from https://dev.elsevier.com/
- [ ] Add to ~/.zshrc: `export SCOPUS_API_KEY="your_key_here"`
- [ ] Reload shell: `source ~/.zshrc`
- [ ] Make scripts executable: `chmod +x getref.py analyze_refs.py`
- [ ] Test: `./getref.py -name "Einstein, Albert" -limit 5`

## Common Workflows

### Download and analyze
```bash
./getref.py -name "Smith, John" -start 2020
./analyze_refs.py John_Smith_2020-present.json
```

### Export DOIs to file
```bash
./getref.py -orcid "0000-0002-1825-0097" -start 2020
./analyze_refs.py ORCID_*.json -urls > dois.txt
```

### Get BibTeX for citations
```bash
./getref.py -institution "Stanford" -start 2023 -limit 50
./analyze_refs.py Stanford_*.json -bibtex references.bib
```

### Keyword research
```bash
./getref.py -name "Your Name" -start 2020
./analyze_refs.py Your_Name_*.json -keywords > keywords.txt
```

## File Locations

- **getref.py** - Main download script
- **analyze_refs.py** - Analysis utility
- **USAGE.md** - Detailed documentation
- **SETUP.md** - API key setup guide
- **requirements.txt** - Python dependencies

## JSON Structure

```json
{
  "metadata": {
    "retrieved_at": "ISO timestamp",
    "total_publications": 42
  },
  "publications": [
    {
      "eid": "Scopus ID",
      "doi": "10.xxxx/xxxxx",
      "title": "Paper title",
      "abstract": "Full text...",
      "journal": "Journal name",
      "year": 2024,
      "authors": [{"name": "...", "given_name": "...", "surname": "..."}],
      "keywords": ["keyword1", "keyword2"],
      "citation_count": 15,
      "url": "https://doi.org/..."
    }
  ]
}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No API key found | Set `SCOPUS_API_KEY` in ~/.zshrc |
| No results | Check spelling, try broader terms |
| Permission denied | Run `chmod +x getref.py` |
| Module not found | Run `pip install pybliometrics pandas` |

## Pro Tips

💡 Use `-limit 10` to test searches before downloading everything  
💡 Both "John Smith" and "Smith, John" name formats work  
💡 JSON format is perfect for LLM processing and data analysis  
💡 Use `-quiet` in scripts to suppress progress messages  
💡 Auto-generated filenames include search parameters
