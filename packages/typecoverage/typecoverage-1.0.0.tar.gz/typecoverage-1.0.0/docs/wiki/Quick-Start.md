
# Quick Start Guide

Get up and running with typecoverage in just a few minutes. This guide covers the most common usage patterns.

## Installation

### From Source (Current Development)
```bash
# Clone or download the repository
# Navigate to the project directory
pip install -r requirements.txt
```

### Development Installation
```bash
# Install in editable/development mode
pip install -e .

# Or install directly
python setup.py install
```

## Basic Usage

### 1. Command Line Analysis

Using the package module:
```bash
python -m typecoverage myfile.py
```

Using the installed command (if installed):
```bash
typecoverage myfile.py
```

Analyze multiple files:
```bash
typecoverage file1.py file2.py file3.py
```

Analyze a directory recursively:
```bash
typecoverage --recursive src/
```

### 2. Python API

```python
from typecoverage import detect_untyped

# Analyze code string
code = """
def greet(name):
    return f"Hello, {name}!"
"""

result = detect_untyped(code)
print(result)
```

### 3. Analyze Live Objects

```python
from typecoverage import typecoverage

def my_function(x, y):
    return x + y

checker = typecoverage()
issues, errors = checker.analyze_object(my_function)

for issue in issues:
    print(f"{issue.type}: {issue.name} at line {issue.line}")
```

## Common Options

### Show Statistics
```bash
typecoverage --statistics myfile.py
```

### Include Context Lines
```bash
typecoverage --context-lines 3 myfile.py
```

### JSON Output
```bash
typecoverage --format json myfile.py
```

### Save to File
```bash
typecoverage --output report.txt myfile.py
```

## Filtering Options

### Ignore Patterns (Default)
By default, typecoverage ignores:
- Variables starting with underscore (`_var`, `__private`)
- Loop variables (`for i in range(10)`)
- Exception variables (`except Exception as e`)
- Context manager variables (`with open() as f`)
- Comprehension variables (`[x for x in items]`)

### Include More Variables
```bash
# Include underscore variables
typecoverage --no-ignore-underscore-vars myfile.py

# Include all variable types
typecoverage --no-ignore-underscore-vars \
          --no-ignore-for-targets \
          --no-ignore-except-vars \
          --no-ignore-context-vars \
          myfile.py
```

## Suppression Comments

Use standard Python suppression comments:

```python
def my_function(x, y):  # type: ignore
    return x + y

def another_function(x, y):  # noqa: ANN001,ANN201
    return x + y
```

Supported patterns:
- `# type: ignore` - Suppress all issues
- `# type: ignore[ANN001]` - Suppress specific codes
- `# noqa` - Suppress all issues  
- `# noqa: ANN001` - Suppress specific codes
- `# mypy: ignore`, `# pyright: ignore` - Tool-specific

## Exit Codes

Control exit behavior for CI/CD:

```bash
# Exit with code 1 if any issues found
typecoverage --exit-nonzero-on-issues myfile.py

# Exit with code 1 if 5 or more issues found
typecoverage --fail-under 5 myfile.py
```

## Real-World Examples

### 1. Check Entire Project
```bash
typecoverage --recursive --statistics \
          --exclude __pycache__,tests \
          src/
```

### 2. CI/CD Integration
```bash
typecoverage --format json \
          --exit-nonzero-on-issues \
          --output typecoverage-report.json \
          src/
```

### 3. Gradual Adoption
```bash
# Start with just function signatures
typecoverage --no-ignore-underscore-vars \
          --context-lines 2 \
          src/core.py
```

### 4. API Analysis Script

```python
#!/usr/bin/env python3
"""Analyze project and generate report."""

from typecoverage import typecoverage
from pathlib import Path

def analyze_project():
    checker = typecoverage()
    
    # Find all Python files
    py_files = list(Path("src").rglob("*.py"))
    
    # Analyze files
    issues, errors = checker.analyze_targets(
        *py_files,
        context_lines=1,
        ignore_underscore_vars=True,
    )
    
    # Generate report
    stats = checker.compute_stats(issues)
    
    print(f"Analyzed {len(py_files)} files")
    print(f"Found {stats.total} type annotation issues")
    print(f"  Arguments: {stats.by_type.get('untyped-argument', 0)}")
    print(f"  Returns: {stats.by_type.get('untyped-return', 0)}")
    print(f"  Variables: {stats.by_type.get('untyped-variable', 0)}")
    
    if errors:
        print(f"\nErrors: {len(errors)}")
        for error in errors[:3]:  # Show first 3
            print(f"  {error}")

if __name__ == "__main__":
    analyze_project()
```

## Configuration

### pyproject.toml Configuration

Create `pyproject.toml` in your project root:

```toml
[tool.typecoverage]
recursive = true
statistics = true
context-lines = 2
exclude = ["tests", "__pycache__", "build"]
ignore-underscore-vars = true
exit-nonzero-on-issues = true
fail-under = 50
```

Then run without options:
```bash
typecoverage src/
```

## Testing Your Installation

### Run Demo Scripts
```bash
# Basic usage examples
python demos/basic_usage.py

# Advanced features demo
python demos/advanced_usage.py

# CLI examples
python demos/cli_examples.py
```

### Run Test Suite
```bash
# Full test suite
pytest tests/ -v --cov=typecoverage --cov-report=term-missing

# Specific tests
pytest tests/test_core.py::Testtypecoverage -v
```

## Next Steps

- **[API Reference](API-Reference.md)** - Complete function documentation
- **[CLI Guide](CLI-Guide.md)** - All command-line options
- **[Configuration](Configuration.md)** - Advanced settings
- **[Examples](Examples.md)** - More complex usage patterns

## Common Issues

**Q: "No module named 'typecoverage'"**
A: Make sure you've installed the package: `pip install -e .` or use `python -m typecoverage`

**Q: Too many issues reported**
A: Use filtering options like `--ignore-underscore-vars` or suppression comments

**Q: Performance with large codebases** 
A: Use `--exclude` to skip unnecessary directories, enable parallel processing (automatic)

**Q: False positives**
A: Check the [FAQ](FAQ.md) for common patterns and solutions

---

**Tip**: Start with `--statistics` to get an overview, then use `--context-lines 2` to see the actual code around issues.
