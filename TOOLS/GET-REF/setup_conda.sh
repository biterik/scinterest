#!/bin/bash
# setup_conda.sh - Setup scinterest conda environment

echo "======================================================================"
echo "Setting up 'scinterest' conda environment"
echo "======================================================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install conda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Step 1: Configuring conda to use ONLY conda-forge..."
# Remove defaults channel if present
conda config --remove channels defaults 2>/dev/null || true
# Add conda-forge as the only channel
conda config --add channels conda-forge
conda config --set channel_priority strict

echo "✓ conda-forge configured as the only channel"
echo ""

echo "Step 2: Creating 'scinterest' environment from environment.yml..."
if conda env list | grep -q "scinterest"; then
    echo "WARNING: Environment 'scinterest' already exists!"
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n scinterest
    else
        echo "Keeping existing environment. Skipping creation."
        echo ""
        echo "To activate: conda activate scinterest"
        exit 0
    fi
fi

conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Environment 'scinterest' created successfully!"
    echo ""
    echo "======================================================================"
    echo "Next steps:"
    echo "======================================================================"
    echo ""
    echo "1. Activate the environment:"
    echo "   conda activate scinterest"
    echo ""
    echo "2. Set your Scopus API key (if not already done):"
    echo "   Add to ~/.zshrc:  export SCOPUS_API_KEY='your_key_here'"
    echo "   Then run:         source ~/.zshrc"
    echo ""
    echo "3. Make scripts executable:"
    echo "   chmod +x getref.py analyze_refs.py"
    echo ""
    echo "4. Test the installation:"
    echo "   ./getref.py --help"
    echo ""
    echo "======================================================================"
else
    echo ""
    echo "ERROR: Failed to create environment"
    exit 1
fi
