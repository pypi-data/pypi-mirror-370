
<div align="center">
  <img src="https://i.postimg.cc/hPbkJZzB/icon-raster.png" alt="Typecoverage Logo" width="350"/>
  <h1>🔍 Typecoverage - Python Type Annotation Analyzer</h1>
  <p><em>A strict CLI + library API to report untyped variables, arguments, and function returns in Python code</em></p>

  <p>
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
  </p>
</div>

## 🎯 What is Typecoverage?

Typecoverage is a comprehensive Python static analysis tool that identifies missing type annotations in your codebase. Unlike other type checkers that focus on type correctness, Typecoverage specifically targets **type annotation coverage** - ensuring your code has complete type hints for maintainability and clarity.

### ✨ Key Features

- 🔍 **Comprehensive Detection** - Finds missing annotations in functions, methods, variables, and returns
- 🎯 **Multiple Input Types** - Analyze files, directories, code strings, live Python objects, and more
- 📊 **Rich Output Formats** - Human-readable text with colors or machine-readable JSON
- ⚙️ **Flexible Filtering** - Smart defaults with configurable rules for different coding patterns
- 🚫 **Comment Suppression** - Standard `# type: ignore` and `# noqa` support
- 🚀 **High Performance** - Parallel processing for large codebases
- 🛠️ **CI/CD Ready** - Exit codes and JSON output for continuous integration
- 📝 **Detailed Context** - Source code snippets around issues for easy fixing

### 🚀 Quick Example

```python
from typecoverage import detect_untyped

# Analyze code string
code = """
def calculate_total(items, tax_rate):
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
"""

result = detect_untyped(code, statistics=True)
print(result)
```

**Output:**
```
Found 3 type annotation issues

📁 <string>
  <string>:2:20 - Missing type annotation for argument "items"
    1 │ 
  ► 2 │ def calculate_total(items, tax_rate):
    3 │     subtotal = sum(item.price for item in items)

  <string>:2:27 - Missing type annotation for argument "tax_rate"
    1 │ 
  ► 2 │ def calculate_total(items, tax_rate):
    3 │     subtotal = sum(item.price for item in items)

  <string>:2:1 - Missing return type annotation "calculate_total"
    1 │ 
  ► 2 │ def calculate_total(items, tax_rate):
    3 │     subtotal = sum(item.price for item in items)

📊 Summary
  Total issues: 3
  🔴 Missing argument types: 2
  🟡 Missing return types: 1
```

## 📦 Installation

### From Source (Current)
```bash
git clone <repository-url>
cd typecoverage-project
pip install -r requirements.txt
```

### Using the Package
```bash
# Install in development mode
pip install -e .

# Or install directly
python setup.py install
```

## 🏁 Quick Start

### Command Line Usage

```bash
# Using the module
python -m typecoverage myfile.py

# Using the installed command
typecoverage myfile.py

# Analyze entire project with statistics
typecoverage --recursive --statistics src/

# JSON output for CI/CD
typecoverage --format json --exit-nonzero-on-issues src/ > report.json

# Include context lines for easier fixing
typecoverage --context-lines 3 src/main.py
```

### Python API Usage

```python
from typecoverage import TypeCoverage, detect_untyped

# Simple analysis
result = detect_untyped("def func(x): return x", statistics=True)
print(result)

# Advanced analysis
checker = TypeCoverage()
issues, errors = checker.analyze_targets(
    "src/",
    recursive=True,
    context_lines=2,
    exclude=["__pycache__", "tests"],
)

stats = checker.compute_stats(issues)
print(f"Found {stats.total} issues across {len(set(i.file for i in issues))} files")
```

## 🎯 Supported Input Types

Typecoverage can analyze various types of targets:

| Input Type | Example | Description |
|------------|---------|-------------|
| **Files** | `main.py` | Individual Python files |
| **Directories** | `src/` | Directory trees (with `--recursive`) |
| **Glob Patterns** | `**/*.py` | Wildcard file matching |
| **Code Strings** | `"def func(x): pass"` | Direct Python code |
| **Live Functions** | `my_function` | Runtime function objects |
| **Classes** | `MyClass` | Class objects |
| **Modules** | `import mymodule; mymodule` | Module objects |
| **Paths** | `Path("src/main.py")` | pathlib.Path objects |

## ⚙️ Configuration

### Command Line Options

```bash
# Analysis options
--recursive              # Recurse into subdirectories
--context-lines N        # Show N lines of context around issues
--statistics             # Include summary statistics

# Output options  
--format json            # JSON output instead of text
--output FILE            # Write to file instead of stdout
--force-color            # Force ANSI colors even when piped

# File filtering
--extensions .py,.pyx    # File extensions to analyze
--exclude tests,docs     # Exclude paths containing substrings

# Variable filtering (default: ignore these)
--no-ignore-underscore-vars    # Include _private variables
--no-ignore-for-targets        # Include for loop variables
--no-ignore-except-vars        # Include exception variables  
--no-ignore-context-vars       # Include with statement variables
--no-ignore-comprehensions     # Include list/dict comprehension vars

# Exit behavior
--exit-nonzero-on-issues       # Exit 1 if any issues found
--fail-under N                 # Exit 1 if >= N issues found
```

### Configuration File

Create `pyproject.toml` configuration:

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

## 🚫 Issue Suppression

Use standard Python suppression comments:

```python
# Suppress all issues on this line
def my_function(x, y):  # type: ignore
    return x + y

# Suppress specific issue types
def another_function(x, y):  # noqa: ANN001,ANN201
    return x + y

# Suppress on previous line
# type: ignore
def third_function(x, y):
    return x + y
```

**Supported patterns:**
- `# type: ignore` - Suppress all type checking issues
- `# type: ignore[code]` - Suppress specific error codes
- `# noqa` / `# noqa: code` - Flake8-style suppression
- `# mypy: ignore` / `# pyright: ignore` - Tool-specific suppression

## 📊 Understanding the Output

### Text Format

```
Found 5 type annotation issues

📁 src/calculator.py
  src/calculator.py:15:8 - Missing type annotation for argument "value"
    14 │     def process_value(self, value, multiplier=1):
  ► 15 │         result = value * multiplier
    16 │         return result

📊 Summary
  Total issues: 5
  🔴 Missing argument types: 3
  🟡 Missing return types: 1  
  🔵 Missing variable types: 1
```

### JSON Format

```json
{
  "version": "0.1.8",
  "issues": [
    {
      "file": "src/calculator.py",
      "line": 15,
      "column": 8,
      "type": "untyped-argument", 
      "name": "value",
      "context": ["    def process_value(self, value, multiplier=1):", "        result = value * multiplier"]
    }
  ],
  "statistics": {
    "total": 5,
    "untyped-argument": 3,
    "untyped-return": 1,
    "untyped-variable": 1
  }
}
```

## 🔧 Advanced Usage

### Analyzing Live Objects

```python
from typecoverage import TypeCoverage

def my_function(x, y):
    return x + y

class MyClass:
    def method(self, value):
        return value * 2

checker = TypeCoverage()

# Analyze function
issues, _ = checker.analyze_object(my_function, context_lines=1)
print(f"Function issues: {len(issues)}")

# Analyze class
issues, _ = checker.analyze_object(MyClass, context_lines=1)
print(f"Class issues: {len(issues)}")
```

### Batch Analysis

```python
from pathlib import Path
from typecoverage import analyze_targets

# Analyze multiple targets
issues, errors = analyze_targets(
    "src/main.py",           # Specific file
    Path("lib/"),            # Directory path
    "utils/**/*.py",         # Glob pattern
    my_function,             # Live object
    recursive=True,
    exclude=["test_", "__pycache__"],
    context_lines=1,
)

print(f"Total issues: {len(issues)}")
print(f"Errors: {len(errors)}")
```

## 🏗️ CI/CD Integration

### GitHub Actions

```yaml
name: Type Annotation Coverage
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
    
    - name: Run typecoverage
      run: |
        typecoverage \
          --format json \
          --exit-nonzero-on-issues \
          --recursive \
          --output typecoverage-report.json \
          src/
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: typecoverage-report
        path: typecoverage-report.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: typecoverage
        name: typecoverage
        entry: typecoverage
        language: system
        args: [--exit-nonzero-on-issues, --recursive, src/]
        files: \.py$
```

## 📚 Examples and Demos

### Basic Usage Demo
```bash
python demos/basic_usage.py
```

### Advanced Features Demo
```bash  
python demos/advanced_usage.py
```

### CLI Examples
```bash
python demos/cli_examples.py
```

### Test the Library
```bash
# Run comprehensive test suite
pytest tests/ -v --cov=typecoverage --cov-report=term-missing

# Test specific functionality
pytest tests/test_core.py::TestTypeCoverage -v
```

## 🏗️ Project Structure

```
├── typecoverage/
│   ├── __init__.py          # Public API exports
│   ├── __main__.py          # CLI entry point
│   └── core.py              # Main typecoverage implementation
├── src/
│   └── core.py              # Development version
├── tests/
│   ├── test_core.py         # Comprehensive test suite  
│   └── test_suppressions.py # Suppression functionality tests
├── demos/
│   ├── basic_usage.py       # Basic usage examples
│   ├── advanced_usage.py    # Advanced features demo
│   └── cli_examples.py      # CLI usage examples
├── docs/
│   └── wiki/               # Comprehensive documentation
│       ├── Home.md         # Wiki home page
│       ├── Quick-Start.md  # Getting started guide
│       ├── API-Reference.md# Complete API docs
│       └── CLI-Guide.md    # Command-line reference
├── scripts/                # Development utilities
├── logs/                   # Analysis logs
├── setup.py               # Package setup
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and clone your fork
2. **Install development dependencies**: `pip install -r requirements.txt`
3. **Run tests**: `pytest tests/ -v`
4. **Check code style**: `ruff check . && black . --check`
5. **Make your changes** and add tests
6. **Run the full test suite**: `pytest tests/ --cov=typecoverage`
7. **Submit a pull request** with a clear description

### Development Workflow

```bash
# Set up development environment
pip install -r requirements.txt

# Run code formatting
black . --line-length 79
isort . -l 79 -m 1
ruff format . --line-length 79

# Run linting
ruff check .
pyright

# Run tests with coverage
pytest tests/ --cov=typecoverage --cov-report=term-missing
```

## 📈 Roadmap

- [x] **Core Analysis Engine** - AST-based type annotation detection
- [x] **CLI Interface** - Full command-line interface
- [x] **Python API** - Programmatic access
- [x] **Multiple Input Types** - Files, directories, code strings, live objects
- [x] **Output Formats** - Text and JSON with statistics
- [x] **Comment Suppression** - Standard suppression patterns
- [x] **Configuration Files** - pyproject.toml support
- [ ] **IDE Extensions** - VS Code, PyCharm plugin support  
- [ ] **Type Hint Suggestions** - Automated type annotation suggestions
- [ ] **Incremental Analysis** - Only check changed files
- [ ] **Custom Rules** - User-defined annotation requirements
- [ ] **HTML Reports** - Rich web-based reporting

## ❓ FAQ

**Q: How does this differ from mypy or pyright?**
A: Mypy and pyright focus on type correctness (catching type errors). Typecoverage focuses on type **coverage** (ensuring annotations exist). Use them together for comprehensive type safety.

**Q: Can I use this with existing type checkers?**  
A: Absolutely! Typecoverage complements mypy, pyright, and other type checkers. Run typecoverage first to ensure annotations exist, then use other tools to verify type correctness.

**Q: What about performance on large codebases?**
A: Typecoverage uses parallel processing and is optimized for speed. For very large projects, use `--exclude` to skip unnecessary directories and `--extensions` to limit file types.

**Q: How do I handle legacy code with many issues?**
A: Start with `--fail-under` set to your current issue count, then gradually reduce it. Use suppression comments for intentionally untyped code.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python's `ast` module for accurate source code analysis
- Inspired by flake8, mypy, and other Python code quality tools
- Uses parallel processing for performance on large codebases
- Follows Google-style docstrings and modern Python practices

---

<div align="center">
  <p>Made with ❤️ for the Python community</p>
  <p>
    <a href="docs/wiki/Home.md">📚 Documentation</a> •
    <a href="demos/">🎯 Examples</a> •
    <a href="https://github.com/yourusername/typecoverage/issues">🐛 Report Issues</a> •
    <a href="https://github.com/yourusername/typecoverage/discussions">💬 Discussions</a>
  </p>
</div>
