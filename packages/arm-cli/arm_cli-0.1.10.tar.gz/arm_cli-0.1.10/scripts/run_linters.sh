#!/bin/bash

# ARM CLI Linting Script
# This script runs all configured linters for the arm-cli project using pip

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the arm-cli root directory."
    exit 1
fi

print_status "Starting linting checks for arm-cli..."
print_status "Ensuring required tools are installed..."
python -m pip install --upgrade pip >/dev/null
python -m pip install black==24.8.0 isort==5.13.2 >/dev/null

# Run Black (code formatter)
print_status "Running Black (code formatter)..."
if black --check .; then
    print_success "Black check passed - code is properly formatted"
else
    print_error "Black check failed - code needs formatting"
    print_status "Run 'black .' to automatically format the code"
    BLACK_FAILED=true
fi

# Run isort (import sorter)
print_status "Running isort (import sorter)..."
if isort --check-only .; then
    print_success "isort check passed - imports are properly sorted"
else
    print_error "isort check failed - imports need sorting"
    print_status "Run 'isort .' to automatically sort imports"
    ISORT_FAILED=true
fi

# # Run Flake8 (style checker)
# print_status "Running Flake8 (style checker)..."
# if flake8 .; then
#     print_success "Flake8 check passed - no style issues found"
# else
#     print_error "Flake8 check failed - style issues found"
#     FLAKE8_FAILED=true
# fi

# # Run MyPy (type checker)
# print_status "Running MyPy (type checker)..."
# if mypy .; then
#     print_success "MyPy check passed - no type issues found"
# else
#     print_error "MyPy check failed - type issues found"
#     MYPY_FAILED=true
# fi

# Summary
echo
print_status "Linting Summary:"
if [ "$BLACK_FAILED" = true ] || [ "$ISORT_FAILED" = true ] || [ "$FLAKE8_FAILED" = true ] || [ "$MYPY_FAILED" = true ]; then
    print_error "Some linting checks failed!"
    echo
    print_status "To fix formatting issues:"
    echo "  black ."
    echo "  isort ."
    echo
    print_status "To run individual linters:"
    echo "  flake8 ."
    echo "  mypy ."
    exit 1
else
    print_success "All linting checks passed! 🎉"
fi 