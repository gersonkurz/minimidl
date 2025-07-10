
## Task 1: Project Setup and Core Parser

### Objective
Create the foundational project structure with uv/pyproject.toml setup and implement the Lark grammar parser for the IDL language.

### Prerequisites
- Vision document has been read and acknowledged
- Empty GitHub repository is ready
- macOS environment with Python 3.13+ and uv installed

### Deliverables

**1. Project Structure Setup**
```
minimidl/
├── pyproject.toml           # uv-based project configuration
├── justfile                 # Build automation
├── README.md                # Basic project description
├── .gitignore               # Python/macOS gitignore
├── minimidl/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   └── parser/
│       ├── __init__.py
│       ├── grammar.lark     # Complete IDL grammar
│       └── parser.py        # Parser implementation
└── tests/
    ├── __init__.py
    └── unit/
        ├── __init__.py
        └── test_parser.py   # Parser unit tests
```