
# API Reference

Complete reference for all public classes, functions, and methods in the typecoverage library.

## Import Statement

```python
from typecoverage import typecoverage, detect_untyped, analyze_targets, Issue, IssueType, Stats
```

## Core Classes

### TypeCoverage

The main analysis class providing all typecoverage functionality.

```python
class typecoverage:
    def __init__(self) -> None
```

**Methods:**

#### analyze_source
```python
def analyze_source(
    self,
    *,
    name: str,
    text: str,
    context_lines: int,
    ignore_underscore_vars: bool = True,
    ignore_comprehensions: bool = True,
    ignore_except_vars: bool = True,
    ignore_for_targets: bool = True,
    ignore_context_vars: bool = True,
) -> Tuple[List[Issue], Optional[str]]
```

Analyze Python source code from a string.

**Parameters:**
- `name`: Pseudo-name for the source (e.g., filename)
- `text`: Python source code as string
- `context_lines`: Number of context lines to include with issues
- `ignore_underscore_vars`: Skip variables starting with underscore
- `ignore_comprehensions`: Skip variables in comprehensions  
- `ignore_except_vars`: Skip exception handler variables
- `ignore_for_targets`: Skip for loop target variables
- `ignore_context_vars`: Skip context manager variables

**Returns:**
- Tuple of (list of issues, optional error message)

**Example:**
```python
from typecoverage import typecoverage

checker = typecoverage()
issues, error = checker.analyze_source(
    name="example.py",
    text="def func(x): return x",
    context_lines=1,
)
```

#### analyze_file
```python
def analyze_file(
    self,
    path: Path,
    *,
    context_lines: int,
    ignore_underscore_vars: bool = True,
    ignore_comprehensions: bool = True,
    ignore_except_vars: bool = True,
    ignore_for_targets: bool = True,
    ignore_context_vars: bool = True,
) -> Tuple[List[Issue], Optional[str]]
```

Analyze a single Python file.

**Parameters:**
- `path`: Path to the Python file
- Other parameters same as `analyze_source`

**Returns:**
- Tuple of (list of issues, optional error message)

#### analyze_object
```python
def analyze_object(
    self,
    obj: Union[CodeType, FrameType, FunctionType, Type[Any], type, ModuleType, Callable],
    *,
    context_lines: int,
    name_hint: Optional[str] = None,
    ignore_underscore_vars: bool = True,
    ignore_comprehensions: bool = True,
    ignore_except_vars: bool = True,
    ignore_for_targets: bool = True,
    ignore_context_vars: bool = True,
) -> Tuple[List[Issue], Optional[str]]
```

Analyze a live Python object by extracting its source.

**Parameters:**
- `obj`: Python object to analyze (function, class, module, etc.)
- `name_hint`: Optional name hint for reporting
- Other parameters same as `analyze_source`

**Returns:**
- Tuple of (list of issues, optional error message)

**Example:**
```python
def my_func(x, y):
    return x + y

from typecoverage import typecoverage
checker = typecoverage()
issues, error = checker.analyze_object(my_func, context_lines=1)
```

#### analyze_targets
```python
def analyze_targets(
    self,
    *targets: TargetLike,
    context_lines: int = 0,
    recursive: bool = True,
    extensions: Sequence[str] = (".py",),
    exclude: Sequence[str] = (),
    ignore_underscore_vars: bool = True,
    ignore_comprehensions: bool = True,
    ignore_except_vars: bool = True,
    ignore_for_targets: bool = True,
    ignore_context_vars: bool = True,
) -> Tuple[List[Issue], List[str]]
```

Analyze multiple targets of various types.

**Parameters:**
- `*targets`: Variable number of targets (strings, paths, objects, etc.)
- `context_lines`: Number of context lines for issues
- `recursive`: Whether to search directories recursively  
- `extensions`: File extensions to include
- `exclude`: Substrings to exclude from file paths
- Other parameters same as `analyze_source`

**Returns:**
- Tuple of (list of issues, list of error messages)

**Example:**
```python
from typecoverage import typecoverage

checker = typecoverage()
issues, errors = checker.analyze_targets(
    "src/",
    "*.py",
    my_function,
    recursive=True,
    exclude=["test_", "__pycache__"],
)
```

#### detect_untyped
```python
def detect_untyped(
    self,
    *targets: TargetLike,
    context_lines: int = 0,
    format: Literal["text", "json"] = "text",
    statistics: bool = False,
    recursive: bool = True,
    extensions: Sequence[str] = (".py",),
    exclude: Sequence[str] = (),
    force_color: bool = False,
    ignore_underscore_vars: bool = True,
    ignore_comprehensions: bool = True,
    ignore_except_vars: bool = True,
    ignore_for_targets: bool = True,
    ignore_context_vars: bool = True,
) -> str
```

Analyze targets and return a formatted report.

**Parameters:**
- `*targets`: Targets to analyze
- `format`: Output format ("text" or "json")
- `statistics`: Whether to include statistics
- `force_color`: Force ANSI color output
- Other parameters same as `analyze_targets`

**Returns:**
- Formatted analysis report as string

**Example:**
```python
from typecoverage import typecoverage

checker = typecoverage()
report = checker.detect_untyped(
    "myfile.py",
    format="text",
    statistics=True,
    context_lines=2,
)
print(report)
```

#### compute_stats
```python
def compute_stats(self, issues: Sequence[Issue]) -> Stats
```

Compute statistics from a sequence of issues.

**Parameters:**
- `issues`: Sequence of Issue objects

**Returns:**
- Stats object with total count and per-type counts

#### render_text
```python
def render_text(
    self,
    *,
    issues: Sequence[Issue],
    stats: Optional[Stats],
    use_color: bool = True,
) -> str
```

Render issues as human-readable text.

**Parameters:**
- `issues`: Issues to render
- `stats`: Optional statistics for summary
- `use_color`: Whether to apply ANSI colors

**Returns:**
- Formatted text report

#### render_json
```python
def render_json(
    self,
    *,
    issues: Sequence[Issue],
    stats: Optional[Stats],
) -> str
```

Render issues as machine-readable JSON.

**Parameters:**
- `issues`: Issues to render  
- `stats`: Optional statistics

**Returns:**
- JSON-formatted string

## Data Classes

### Issue
```python
@dataclass(frozen=True)
class Issue:
    file: Path
    line: int
    column: int
    type: IssueType
    name: str
    context: List[str]
```

Represents one finding of a missing annotation.

**Attributes:**
- `file`: File path where issue was found
- `line`: 1-based line number
- `column`: 0-based column offset  
- `type`: Kind of issue ("untyped-argument", "untyped-return", "untyped-variable")
- `name`: Identifier name (function or variable)
- `context`: Source context lines around the issue

### Stats
```python
@dataclass
class Stats:
    total: int
    by_type: MutableMapping[IssueType, int]
```

Aggregate counters for issues.

**Attributes:**
- `total`: Total number of issues
- `by_type`: Mapping from IssueType to count

### Scope
```python
@dataclass
class Scope:
    kind: ScopeKind
    defined: Set[str]
    annotated: Set[str]
    globals_: Set[str]
    nonlocals: Set[str]
```

Tracks state for a lexical scope (internal use).

## Type Aliases

### IssueType
```python
IssueType = Literal[
    "untyped-argument",
    "untyped-return", 
    "untyped-variable",
]
```

### ScopeKind  
```python
ScopeKind = Literal[
    "module",
    "function",
    "class", 
    "comp",
    "other",
]
```

### TargetLike
```python
TargetLike = Union[
    str,                # File path, glob pattern, or code string
    Path,               # pathlib Path object
    CodeType,           # Code object
    FrameType,          # Frame object
    FunctionType,       # Function object
    Type[Any],          # Class type
    ModuleType,         # Module object
    Callable,           # Any callable
]
```

## Convenience Functions

### detect_untyped (Module Level)
```python
def detect_untyped(*args, **kwargs) -> str
```

Convenience function that creates a typecoverage instance and calls its `detect_untyped` method.

**Example:**
```python
from typecoverage import detect_untyped

result = detect_untyped("def func(x): return x", statistics=True)
print(result)
```

### analyze_targets (Module Level)
```python
def analyze_targets(*args, **kwargs) -> Tuple[List[Issue], List[str]]
```

Convenience function that creates a typecoverage instance and calls its `analyze_targets` method.

**Example:**
```python
from typecoverage import analyze_targets

issues, errors = analyze_targets("src/", recursive=True)
print(f"Found {len(issues)} issues")
```

### parse_and_run
```python
def parse_and_run(argv: Optional[Sequence[str]] = None) -> int
```

Main CLI entry point. Parses command-line arguments and runs analysis.

**Parameters:**
- `argv`: Optional argument list (uses sys.argv if None)

**Returns:**
- Exit code (0 for success, 1 for issues found, 2 for errors)

## Comment Suppression

### CommentSuppression
```python
class typecoverage.CommentSuppression:
    @classmethod
    def is_suppressed(cls, line_text: str, issue_type: IssueType) -> bool
```

Checks if an issue type is suppressed by comments.

**Supported Patterns:**
- `# type: ignore`
- `# type: ignore[code1,code2]`  
- `# noqa`
- `# noqa: code1,code2`
- `# mypy: ignore`
- `# pyright: ignore`

**Issue Type Codes:**

**untyped-argument:**
- ANN001, ANN002, ANN003, ANN101, ANN102
- arg-type, no-untyped-def, type-arg

**untyped-return:**
- ANN201, ANN202
- return-value, no-untyped-def, type-return

**untyped-variable:**
- ANN001
- var-annotated, name-defined, type-var

## Constants

### VERSION
```python
VERSION: str = "0.1.8"
```

Library version string.

### Colors
```python
class Colors(Enum):
    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    # ... other colors
```

ANSI color constants for terminal output.

## Usage Examples

### Basic Analysis
```python
from typecoverage import typecoverage

checker = typecoverage()
code = "def func(x): return x"

# Simple analysis
issues, error = checker.analyze_source(
    name="test.py", 
    text=code, 
    context_lines=0
)

print(f"Found {len(issues)} issues")
```

### Comprehensive Project Analysis
```python
from pathlib import Path
from typecoverage import typecoverage

def analyze_project(project_path: Path):
    checker = typecoverage()
    
    # Get all Python files
    py_files = list(project_path.rglob("*.py"))
    
    # Analyze all files
    issues, errors = checker.analyze_targets(
        *py_files,
        context_lines=1,
        exclude=["__pycache__", ".git"],
    )
    
    # Generate statistics
    stats = checker.compute_stats(issues)
    
    # Create report
    report = checker.render_text(
        issues=issues,
        stats=stats,
        use_color=False,
    )
    
    return report, stats

# Usage
report, stats = analyze_project(Path("src"))
print(f"Total issues: {stats.total}")
print(report)
```

### JSON Integration
```python
import json
from typecoverage import detect_untyped

# Analyze and get JSON
result_json = detect_untyped(
    "myfile.py",
    format="json",
    statistics=True,
)

# Parse JSON
data = json.loads(result_json)

# Process results
print(f"Version: {data['version']}")
print(f"Total issues: {data['statistics']['total']}")

for issue in data['issues']:
    print(f"{issue['type']}: {issue['name']} at {issue['file']}:{issue['line']}")
```

---

**See Also:**
- [CLI Guide](CLI-Guide.md) for command-line usage
- [Examples](Examples.md) for more complex scenarios
- [Configuration](Configuration.md) for advanced settings
