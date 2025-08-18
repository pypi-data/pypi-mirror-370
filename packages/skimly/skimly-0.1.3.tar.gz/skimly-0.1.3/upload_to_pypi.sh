#!/bin/bash

# Skimly Python Package Upload Script
# This script builds and uploads the package to PyPI

echo "🚀 Building Skimly Python package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

echo "✅ Package built successfully!"

# Check package validity
echo "🔍 Checking package validity..."
python -m twine check dist/*

if [ $? -eq 0 ]; then
    echo "✅ Package validation passed!"
    
    # Upload to PyPI
    echo "📤 Uploading to PyPI..."
    python -m twine upload dist/*
    
    if [ $? -eq 0 ]; then
        echo "🎉 Successfully uploaded to PyPI!"
        echo "📦 Package: skimly-0.1.1"
        echo "🌐 View at: https://pypi.org/project/skimly/"
    else
        echo "❌ Upload failed. Check your PyPI credentials in .pypirc"
        echo "💡 Get your API token from: https://pypi.org/manage/account/token/"
    fi
else
    echo "❌ Package validation failed!"
    exit 1
fi
