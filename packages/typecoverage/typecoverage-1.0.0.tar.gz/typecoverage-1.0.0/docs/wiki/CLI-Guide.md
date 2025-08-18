
# CLI Guide

Complete guide to using the typecoverage command-line interface for automated type annotation analysis.

## Basic Usage

### Command Structure
```bash
# Using the module
python -m typecoverage [OPTIONS] [TARGETS...]

# Using installed command (if installed)
typecoverage [OPTIONS] [TARGETS...]
```

### Simple Examples
```bash
# Analyze a single file
typecoverage myfile.py

# Analyze multiple files
typecoverage file1.py file2.py file3.py

# Analyze current directory
typecoverage .

# Analyze with glob patterns
typecoverage "*.py"
typecoverage "src/**/*.py"
```

## Target Types

The CLI accepts various target types:

### File Paths
```bash
typecoverage src/main.py
typecoverage /absolute/path/to/file.py
```

### Directory Paths
```bash
# Non-recursive (files in directory only)
typecoverage src/

# Recursive (include subdirectories)
typecoverage --recursive src/
```

### Glob Patterns
```bash
# All .py files in current directory
typecoverage "*.py"

# All .py files recursively
typecoverage "**/*.py"

# Specific patterns
typecoverage "src/**/test_*.py"
```

### Code Strings
If a string doesn't resolve to a file path, it's treated as Python code:
```bash
typecoverage "def func(x): return x"
```

## Output Options

### Format Selection
```bash
# Human-readable text (default)
typecoverage --format text myfile.py

# Machine-readable JSON
typecoverage --format json myfile.py
```

### Statistics
```bash
# Include issue count summary
typecoverage --statistics myfile.py
```

### Context Lines
```bash
# Show 2 lines of context around each issue
typecoverage --context-lines 2 myfile.py

# Show 5 lines of context
typecoverage --context-lines 5 myfile.py
```

### Output Destination
```bash
# Print to stdout (default)
typecoverage myfile.py

# Save to file
typecoverage --output report.txt myfile.py

# Save JSON report
typecoverage --format json --output report.json myfile.py
```

### Color Control
```bash
# Auto-detect color support (default)
typecoverage myfile.py

# Force color output
typecoverage --force-color myfile.py
```

## File Selection

### Extensions
```bash
# Only Python files (default)
typecoverage --extensions .py src/

# Multiple extensions
typecoverage --extensions .py,.pyx src/

# Custom extensions
typecoverage --extensions .py,.pyi,.pyx src/
```

### Exclusions
```bash
# Exclude files containing specific substrings
typecoverage --exclude test_,__pycache__ src/

# Exclude multiple patterns
typecoverage --exclude tests,docs,build src/
```

### Recursive Processing
```bash
# Process directories recursively
typecoverage --recursive src/

# Non-recursive (default for most patterns)
typecoverage src/
```

## Filtering Options

### Variable Types

#### Underscore Variables
```bash
# Ignore underscore variables (default)
typecoverage myfile.py

# Include underscore variables
typecoverage --no-ignore-underscore-vars myfile.py
```

#### Loop Variables
```bash
# Ignore for-loop target variables (default)  
typecoverage myfile.py

# Include for-loop variables
typecoverage --no-ignore-for-targets myfile.py
```

#### Exception Variables
```bash
# Ignore exception handler variables (default)
typecoverage myfile.py

# Include exception variables
typecoverage --no-ignore-except-vars myfile.py
```

#### Context Manager Variables
```bash
# Ignore context manager variables (default)
typecoverage myfile.py

# Include context manager variables  
typecoverage --no-ignore-context-vars myfile.py
```

#### Comprehension Variables
```bash
# Ignore comprehension variables (default)
typecoverage myfile.py

# Include comprehension variables
typecoverage --no-ignore-comprehensions myfile.py
```

### Comprehensive Filtering
```bash
# Include all variable types
typecoverage \
  --no-ignore-underscore-vars \
  --no-ignore-for-targets \
  --no-ignore-except-vars \
  --no-ignore-context-vars \
  myfile.py
```

## Exit Behavior

### Exit Codes
- `0`: Success (no issues found or analysis completed)
- `1`: Issues found (when using failure options)
- `2`: Error (invalid arguments, file not found, etc.)

### Failure Conditions
```bash
# Exit with code 1 if any issues found
typecoverage --exit-nonzero-on-issues myfile.py

# Exit with code 1 if 5 or more issues found
typecoverage --fail-under 5 myfile.py

# Combine both conditions
typecoverage --exit-nonzero-on-issues --fail-under 10 src/
```

## Special Modes

### Version Information
```bash
typecoverage --version
```

### Demo Mode
```bash
# Run built-in demonstrations
typecoverage --demo
```

### Help
```bash
# Show all available options
typecoverage --help
```

## Configuration File

Create `pyproject.toml` in your project root:

```toml
[tool.typecoverage]
recursive = true
statistics = true
context-lines = 2
exclude = ["tests", "__pycache__"]
ignore-underscore-vars = true
exit-nonzero-on-issues = true
```

Then run without options:
```bash
typecoverage src/
```

## Common Workflows

### Development Workflow
```bash
# Quick check during development
typecoverage --context-lines 2 myfile.py

# Check specific function
typecoverage --context-lines 1 "def my_func(x): return x"
```

### Project Analysis
```bash
# Full project analysis with summary
typecoverage --recursive --statistics \
          --exclude __pycache__,tests \
          --context-lines 1 \
          src/
```

### CI/CD Integration
```bash
# Continuous Integration
typecoverage --format json \
          --exit-nonzero-on-issues \
          --output typecoverage-report.json \
          --recursive \
          src/

# Check exit code in scripts
if typecoverage --exit-nonzero-on-issues src/; then
    echo "✅ No type annotation issues"
else
    echo "❌ Type annotation issues found"
fi
```

### Quality Gates
```bash
# Enforce maximum issue count
typecoverage --fail-under 10 \
          --statistics \
          --recursive \
          src/

# Gradual improvement (reduce threshold over time)  
typecoverage --fail-under 50 src/  # Start high
typecoverage --fail-under 25 src/  # Reduce gradually
typecoverage --fail-under 10 src/  # Target goal
```

### Documentation Generation
```bash
# Generate detailed report for documentation
typecoverage --recursive \
          --statistics \
          --context-lines 3 \
          --output docs/type-coverage-report.txt \
          src/

# JSON report for badge generation
typecoverage --format json \
          --statistics \
          --recursive \
          --output coverage.json \
          src/
```

## Advanced Usage

### Complex File Selection
```bash
# Multiple glob patterns
typecoverage "src/**/*.py" "lib/**/*.py" "tools/*.py"

# Mixed targets
typecoverage main.py src/ "tests/test_*.py"

# Exclude specific directories
typecoverage --recursive \
          --exclude __pycache__,node_modules,.git \
          .
```

### Performance Optimization
```bash
# Focus on specific areas
typecoverage --exclude tests,docs,examples src/

# Use appropriate extensions only
typecoverage --extensions .py --recursive src/

# Limit context for faster processing
typecoverage --context-lines 0 --recursive src/
```

### Custom Scripts

Create executable scripts for common tasks:

**check-types.sh:**
```bash
#!/bin/bash
typecoverage --recursive \
          --statistics \
          --context-lines 1 \
          --exclude __pycache__,build,dist \
          "$@"
```

**ci-typecoverage.sh:**
```bash
#!/bin/bash
set -e

echo "🔍 Running type annotation check..."

typecoverage --format json \
          --exit-nonzero-on-issues \
          --recursive \
          --output typecoverage-results.json \
          src/

echo "✅ Type annotation check passed"
```

## Integration Examples

### Pre-commit Hook
`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: typecoverage
        name: typecoverage
        entry: typecoverage
        language: system
        args: [--exit-nonzero-on-issues, --recursive]
        files: \.py$
```

### GitHub Actions
`.github/workflows/typecoverage.yml`:
```yaml
name: Type Annotation Check
on: [push, pull_request]

jobs:
  typecoverage:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Install typecoverage
      run: pip install -e .
    - name: Run typecoverage
      run: |
        typecoverage --format json \
                  --exit-nonzero-on-issues \
                  --recursive \
                  --output typecoverage-report.json \
                  src/
    - name: Upload report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: typecoverage-report
        path: typecoverage-report.json
```

### Makefile Integration
```makefile
.PHONY: typecoverage typecoverage-ci typecoverage-report

typecoverage:
	typecoverage --recursive --statistics src/

typecoverage-ci:
	typecoverage --exit-nonzero-on-issues --recursive src/

typecoverage-report:
	typecoverage --recursive --statistics \
	          --context-lines 2 \
	          --output reports/typecoverage.txt \
	          src/
```

## Troubleshooting

### Common Issues

**"No module named 'typecoverage'"**
```bash
# Make sure you've installed the package
pip install -e .

# Or use the module form
python -m typecoverage myfile.py
```

**"Too many issues reported"**
```bash
# Use filtering options
typecoverage --ignore-underscore-vars src/

# Focus on specific issue types
typecoverage --context-lines 0 src/ | grep "Missing return type"
```

**"Performance issues with large codebases"**
```bash
# Exclude unnecessary directories
typecoverage --exclude __pycache__,node_modules,build,dist src/

# Reduce context lines
typecoverage --context-lines 0 src/

# Process specific file patterns
typecoverage "src/**/*.py"
```

### Debug Options
```bash
# Verbose error reporting
typecoverage --format json src/ 2>&1 | jq '.'

# Test with single file first
typecoverage --context-lines 2 single_file.py

# Check configuration loading
python -c "
from typecoverage.core import typecoverage
checker = typecoverage()
print('Configuration loaded successfully')
"
```

---

**Next Steps:**
- [Configuration](Configuration.md) - Advanced settings and pyproject.toml
- [Examples](Examples.md) - Real-world usage examples  
- [API Reference](API-Reference.md) - Python API documentation
