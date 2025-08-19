@_default:
    just --list --unsorted

# Run all build-related recipes in the justfile
run-all: install-deps format-python check-python check-unused test-python check-security check-spelling check-commits build-website build-readme

# Install the pre-commit hooks
install-precommit:
  # Install pre-commit hooks
  uvx pre-commit install
  # Run pre-commit hooks on all files
  uvx pre-commit run --all-files
  # Update versions of pre-commit hooks
  uvx pre-commit autoupdate

# Install Python package dependencies
install-deps:
  uv sync --all-extras --dev --upgrade

# Run the Python tests
test-python:
  uv run pytest
  # Make the badge from the coverage report
  uv run genbadge coverage \
    -i coverage.xml \
    -o htmlcov/coverage.svg

# Check Python code for any errors that need manual attention
check-python:
  # Check formatting
  uv run ruff check .
  # Check types
  uv run mypy .

# Reformat Python code to match coding style and general structure
format-python:
  uv run ruff check --fix .
  uv run ruff format .

# Build the documentation website using Quarto
build-website:
  # To let Quarto know where python is.
  export QUARTO_PYTHON=.venv/bin/python3
  # Delete any previously built files from quartodoc.
  # -f is to not give an error if the files don't exist yet.
  rm -f docs/reference/*.qmd
  uv run quartodoc build
  uv run quarto render --execute

# Run checks on commits with non-main branches
check-commits:
  #!/bin/zsh
  branch_name=$(git rev-parse --abbrev-ref HEAD)
  number_of_commits=$(git rev-list --count HEAD ^main)
  if [[ ${branch_name} != "main" && ${number_of_commits} -gt 0 ]]
  then
    uv run cz check --rev-range main..HEAD
  else
    echo "Can't either be on ${branch_name} or have more than ${number_of_commits}."
  fi

# Run basic security checks on the package
check-security:
  uv run bandit -r src/

# Check for spelling errors in files
check-spelling:
  uv run typos

# Build the documentation as PDF using Quarto
build-pdf:
  # To let Quarto know where python is.
  export QUARTO_PYTHON=.venv/bin/python3
  uv run quarto install tinytex
  # For generating images from Mermaid diagrams
  uv run quarto install chromium
  uv run quarto render --profile pdf --to pdf
  find docs -name "mermaid-figure-*.png" -delete

# Check for unused code in the package and its tests
check-unused:
  # exit code=0: No unused code was found
  # exit code=3: Unused code was found
  # Three confidence values:
  # - 100 %: function/method/class argument, unreachable code
  # - 90 %: import
  # - 60 %: attribute, class, function, method, property, variable
  # There are some things should be ignored though, with the allowlist.
  # Create an allowlist with `vulture --make-allowlist`
  uv run vulture src/ tests/ **/vulture-allowlist.py

# Re-build the README from the Quarto file
build-readme:
  uvx --from quarto quarto render README.qmd --to gfm
