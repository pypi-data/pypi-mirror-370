
# TypeCoverage Library Wiki

Welcome to the comprehensive documentation for the typecoverage library - a powerful Python static analysis tool that helps identify missing type annotations in your code.

## Quick Navigation

- **[Installation](Installation.md)** - How to install and set up the library
- **[Quick Start](Quick-Start.md)** - Get up and running in minutes
- **[API Reference](API-Reference.md)** - Complete API documentation
- **[CLI Guide](CLI-Guide.md)** - Command-line interface usage
- **[Configuration](Configuration.md)** - Settings and customization
- **[Advanced Usage](Advanced-Usage.md)** - Complex scenarios and patterns
- **[Examples](Examples.md)** - Real-world usage examples
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions

## What is typecoverage?

typecoverage is a strict CLI + library API designed to report untyped variables, arguments, and function returns in Python code. It helps maintain code quality by ensuring comprehensive type annotation coverage.

### Key Features

- ✅ **Comprehensive Analysis** - Detects missing type annotations in functions, variables, and returns
- ✅ **Multiple Input Types** - Analyze code strings, files, directories, live objects, and more
- ✅ **Flexible Output** - Text and JSON formats with optional statistics
- ✅ **Smart Filtering** - Configurable rules to ignore specific patterns
- ✅ **Comment Suppression** - Standard `# type: ignore` and `# noqa` support
- ✅ **Parallel Processing** - Fast analysis of large codebases
- ✅ **CLI Integration** - Full command-line interface for automation
- ✅ **CI/CD Ready** - Exit codes and JSON output for continuous integration

### Current Version

**Version**: 0.1.8  
**Python**: 3.11+  
**License**: MIT

### Supported Inputs

The library can analyze various types of targets:

- **Files and Directories** - Individual files or entire directory trees
- **Glob Patterns** - Wildcards like `**/*.py` for flexible file selection  
- **Code Strings** - Direct Python code analysis
- **Live Objects** - Functions, classes, modules from running Python
- **Code Objects** - CodeType, FrameType objects
- **Path Objects** - pathlib.Path instances

### Output Formats

- **Human-Readable Text** - Colorized terminal output with context
- **Machine-Readable JSON** - Structured data for tooling integration
- **Statistics** - Summary counts by issue type
- **Context Lines** - Source code snippets around issues

## Quick Example

```python
from typecoverage import detect_untyped

# Analyze code string
code = """
def calculate_area(length, width):
    return length * width
"""

result = detect_untyped(code, statistics=True)
print(result)
```

Output:
```
Found 3 type annotation issues

📁 <string>
  <string>:2:20 - Missing type annotation for argument "length"
  <string>:2:28 - Missing type annotation for argument "width" 
  <string>:2:1 - Missing return type annotation "calculate_area"

📊 Summary
  Total issues: 3
  🔴 Missing argument types: 2
  🟡 Missing return types: 1
```

## Installation Options

### From Source (Current Development)
```bash
git clone <repository-url>
cd typecoverage-project
pip install -r requirements.txt
```

### Development Installation
```bash
# Install in development mode
pip install -e .

# Or build and install
python setup.py install
```

### Package Structure

The project uses a dual-structure approach:

- **`typecoverage/`** - Main package for distribution
- **`src/`** - Development source code
- **`tests/`** - Test suite
- **`demos/`** - Usage examples
- **`docs/wiki/`** - Documentation

## Getting Started

### Command Line Usage

```bash
# Using the package
python -m typecoverage myfile.py

# Or if installed
typecoverage --recursive --statistics src/
```

### Python API Usage

```bash
from typecoverage import typecoverage, detect_untyped

# Simple analysis
issues, errors = detect_untyped("def func(x): return x")

# Advanced usage
checker = typecoverage()
issues, errors = checker.analyze_targets("src/", recursive=True)
```

## Development Workflows

The project includes several automated workflows:

### Code Quality
- **Black** - Code formatting
- **isort** - Import sorting  
- **Ruff** - Fast linting
- **Pyright** - Type checking

### Testing and Analysis
- **Pytest** - Test runner with coverage
- **Flake8** - Additional linting

### Build and Package
- **Build** - Package building
- **PyPI Upload** - Distribution

## Contributing

This library is actively developed and welcomes contributions:

1. **Setup**: `pip install -r requirements.txt`
2. **Test**: `pytest tests/ -v --cov=typecoverage`
3. **Format**: `black . --line-length 79`
4. **Lint**: `ruff check .`
5. **Type Check**: `pyright`

## Documentation Structure

- **[Quick Start](Quick-Start.md)** - Essential usage patterns
- **[API Reference](API-Reference.md)** - Complete function documentation  
- **[CLI Guide](CLI-Guide.md)** - Command-line interface
- **Examples** - Real-world usage scenarios

## License

MIT License - see LICENSE file for details.

---

**Next Steps**: Start with the [Quick Start Guide](Quick-Start.md) to begin using typecoverage in your projects.
