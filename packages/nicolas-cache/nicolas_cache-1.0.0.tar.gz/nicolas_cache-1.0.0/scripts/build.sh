#!/bin/bash

# Build script for nicolas-cache package
# This script demonstrates the build process used in CI/CD

set -e

echo "=== Nicolas Cache Package Build ==="
echo

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Show current git status
echo "Git status:"
git status --porcelain
echo

# Show current version from setuptools-scm
echo "Current version from git tags:"
python -m setuptools_scm
echo

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/
echo

# Install build dependencies
echo "Installing build dependencies..."
pip install build setuptools-scm twine
echo

# Build the package
echo "Building package..."
python -m build
echo

# Check the built package
echo "Checking package..."
twine check dist/*
echo

# Show what was built
echo "Built files:"
ls -la dist/
echo

# Show package info
echo "Package info:"
for file in dist/*.whl; do
    if [ -f "$file" ]; then
        echo "Wheel: $file"
        python -m zipfile -l "$file" | head -20
    fi
done

echo
echo "=== Build completed successfully ==="