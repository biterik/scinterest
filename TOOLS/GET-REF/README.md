# Scopus Publication Downloader Suite

A complete command-line toolkit for downloading and analyzing publication data from the Scopus API.

## 🎯 What You Get

- **getref.py** - Download publications with a simple command
- **analyze_refs.py** - Analyze, filter, and export your data
- **JSON output** - Perfect for LLMs, data analysis, and automation
- **Auto-generated filenames** - Based on your search parameters

## 🚀 Quick Start

### 1. Install Dependencies

**Option A: Using Conda (Recommended)**
```bash
# Automated setup with conda-forge
./setup_conda.sh

# Or manually:
conda env create -f environment.yml
conda activate scinterest
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

### 2. Setup API Key

Add to your `~/.zshrc`:
```bash
export SCOPUS_API_KEY="your_key_here"
```

Get your key from: https://dev.elsevier.com/

Reload your shell:
```bash
source ~/.zshrc
```

### 3. Make Scripts Executable

```bash
chmod +x getref.py analyze_refs.py
```

### 4. Download Publications

```bash
# Activate environment first (if using conda)
conda activate scinterest

# By author name
./getref.py -name "John A. Smith" -start 2020 -end 2025

# By ORCID
./getref.py -orcid "0000-0002-1825-0097" -start 2020

# By institution
./getref.py -institution "MPI SusMat" -limit 100
```

Output filename: `John_A_Smith_2020-2025.json`

### 5. Analyze Results

```bash
# Summary statistics
./analyze_refs.py John_A_Smith_2020-2025.json

# Keyword analysis
./analyze_refs.py John_A_Smith_2020-2025.json -keywords

# Extract DOIs
./analyze_refs.py John_A_Smith_2020-2025.json -dois

# Export to BibTeX
./analyze_refs.py John_A_Smith_2020-2025.json -bibtex refs.bib
```

## 📁 Files Included

| File | Purpose |
|------|---------|
| `getref.py` | Main download script (executable) |
| `analyze_refs.py` | Analysis utility (executable) |
| `requirements.txt` | Python dependencies (pip) |
| `environment.yml` | Conda environment specification |
| `setup_conda.sh` | Automated conda setup |
| `USAGE.md` | Detailed usage documentation |
| `SETUP.md` | Step-by-step API key setup |
| `CONDA_INSTALL.md` | Conda-specific installation guide |
| `QUICKREF.md` | Quick reference card |
| `conda_commands.sh` | Conda commands cheatsheet |
| `demo.sh` | Example commands |

## 💡 Examples

### Download Your Publications

```bash
# Using your name
./getref.py -name "Smith, John" -start 2020

# Using your ORCID (recommended)
./getref.py -orcid "0000-0002-1825-0097" -start 2020
```

### Department/Group Publications

```bash
./getref.py -institution "MPI SusMat" -start 2020 -end 2025
```

### Test Before Full Download

```bash
# Limit to 10 papers for testing
./getref.py -name "Einstein, Albert" -limit 10
```

### Analyze Keywords in Your Field

```bash
./getref.py -institution "Your Department" -start 2020
./analyze_refs.py Your_Department_*.json -keywords
```

### Generate Bibliography

```bash
./getref.py -name "Your Name" -start 2020
./analyze_refs.py Your_Name_*.json -bibtex my_publications.bib
```

## 📊 JSON Output Structure

```json
{
  "metadata": {
    "retrieved_at": "2025-10-29T10:30:00",
    "total_publications": 42,
    "source": "Scopus API via pybliometrics"
  },
  "publications": [
    {
      "eid": "2-s2.0-85123456789",
      "doi": "10.1016/j.example.2024.01.001",
      "title": "Your Paper Title",
      "abstract": "Full abstract text...",
      "journal": "Journal Name",
      "year": 2024,
      "authors": [
        {
          "name": "John Smith",
          "surname": "Smith",
          "given_name": "John",
          "author_id": "12345678900"
        }
      ],
      "keywords": ["keyword1", "keyword2"],
      "citation_count": 15,
      "url": "https://doi.org/10.1016/j.example.2024.01.001"
    }
  ]
}
```

## 🔧 Advanced Usage

### Python Integration

```python
import json

# Load your data
with open('publications.json', 'r') as f:
    data = json.load(f)

pubs = data['publications']

# Extract all DOIs
dois = [p['doi'] for p in pubs if p['doi']]

# Get unique keywords
keywords = set()
for p in pubs:
    keywords.update(p.get('keywords', []))

# Filter by citations
highly_cited = [p for p in pubs if p['citation_count'] > 10]

# Recent papers
from datetime import datetime
recent = [p for p in pubs if p['year'] >= 2023]
```

### Using with jq

```bash
# Extract DOIs
cat publications.json | jq -r '.publications[].doi'

# Count by year
cat publications.json | jq '.publications | group_by(.year)'

# Most cited papers
cat publications.json | jq '.publications | sort_by(-.citation_count) | .[0:5]'
```

### Batch Processing

```bash
#!/bin/bash
# Download for multiple authors

authors=(
    "Smith, John"
    "Doe, Jane"
    "Johnson, Bob"
)

for author in "${authors[@]}"; do
    ./getref.py -name "$author" -start 2020 -quiet
done
```

## 🎓 Why JSON Format?

JSON was chosen for optimal compatibility and usability:

✅ **LLM-Friendly**: Easily processed by AI models  
✅ **Programmatic**: Simple parsing in any language  
✅ **Structured**: Preserves nested data (authors, keywords)  
✅ **Standard**: Works with countless tools and libraries  
✅ **Human-Readable**: Pretty-printed for inspection  
✅ **DOI Access**: Easy extraction for downloading papers  

## 📝 Command-Line Arguments

### getref.py

```
Search options (choose one):
  -name "Author Name"         Author search
  -orcid "0000-0002-1825-0097"  ORCID search  
  -institution "University"    Affiliation search

Filters:
  -start YEAR                 Start year (inclusive)
  -end YEAR                   End year (inclusive)
  -limit N                    Max results

Output:
  -output FILE                Custom filename
  -quiet                      No progress messages
  -verbose                    Detailed progress
```

### analyze_refs.py

```
Analysis options:
  -summary                    Summary statistics (default)
  -keywords                   Keyword analysis
  -dois                       List DOIs
  -urls                       List DOI URLs
  -highly-cited N            Papers with N+ citations
  -list simple|detailed       List publications
  -bibtex FILE               Export to BibTeX
```

## 🔍 Common Workflows

### 1. Track Your Publications
```bash
./getref.py -orcid "YOUR-ORCID" -start 2020
./analyze_refs.py ORCID_*.json
```

### 2. Research Collaboration Opportunities
```bash
./getref.py -institution "Target University" -start 2023
./analyze_refs.py Target_University_*.json -keywords
```

### 3. Literature Review
```bash
./getref.py -name "Leading Researcher" -start 2020
./analyze_refs.py Leading_Researcher_*.json -highly-cited 20
```

### 4. Grant/CV Preparation
```bash
./getref.py -name "Your Name" -start 2020
./analyze_refs.py Your_Name_*.json -bibtex cv_publications.bib
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `No API key found` | Set `SCOPUS_API_KEY` in `~/.zshrc` |
| `Permission denied` | Run `chmod +x getref.py` |
| `Module not found` | Run `pip install pybliometrics pandas` |
| `No results found` | Check spelling, try broader terms |
| `401 Unauthorized` | Verify API key is correct and active |

## 📚 Documentation

- **USAGE.md** - Complete usage guide with examples
- **SETUP.md** - Detailed API key configuration
- **QUICKREF.md** - Quick reference card
- **demo.sh** - Executable examples

## ⚡ Pro Tips

1. Use `-limit 10` to test searches quickly
2. Both "John Smith" and "Smith, John" formats work
3. ORCID searches are more reliable than name searches
4. JSON format is perfect for feeding to LLMs
5. Use `-quiet` in automated scripts
6. Check `--help` for any command to see all options

## 🔐 Security Note

Never commit your API key to version control. Keep `SCOPUS_API_KEY` in your environment variables only.

## 📄 License

This tool is for academic and research purposes. Ensure compliance with Scopus API terms of service and your institution's license agreement.

## 🆘 Getting Help

1. Check the documentation files (USAGE.md, SETUP.md)
2. Run `./getref.py --help` or `./analyze_refs.py --help`
3. Test with `-limit 5` before large downloads
4. Use `-verbose` to see detailed progress

## 🎉 You're Ready!

```bash
# Quick test:
./getref.py -name "Einstein, Albert" -limit 5
./analyze_refs.py Einstein_Albert.json

# Your publications:
./getref.py -orcid "YOUR-ORCID-HERE" -start 2020
./analyze_refs.py ORCID_*.json -keywords
```

Happy researching! 🔬📚
