# MinimIDL: Vision Document for Claude Code Implementation

## CRITICAL INSTRUCTION
**DO NOT BEGIN IMPLEMENTATION. READ THIS ENTIRE DOCUMENT, ACKNOWLEDGE UNDERSTANDING, AND WAIT FOR SPECIFIC TASK ASSIGNMENTS.**

## Project Overview

**Name:** minimidl (Modern Interface Notation INterpreter for Multi-language Implementation Definition Language)

**Purpose:** A zero-cost abstraction tool that generates C++ interfaces, C wrappers, and Swift bindings from a clean Interface Definition Language (IDL), eliminating the Microsoft COM/OLE complexity while preserving the proven IDL concept.

**Philosophy:** This is a "glorified macro system" - no runtime marshalling, no cross-process communication, just clean code generation for interface bridging.

## Prerequisites
- macOS environment (initial target)
- Empty local GitHub repository with Git configured for push/fetch/rebase
- Python 3.13+ with uv package manager
- Modern development toolchain (CMake, Xcode/Swift toolchain)

## Architecture

### Core Pipeline
```
IDL Source → Lark Parser → AST → Code Generators → Target Files
                            ↓
                         JSON Cache (optional)
```

### Module Structure
```
minimidl/
├── __init__.py
├── __main__.py              # Entry point: python -m minimidl
├── cli.py                   # Typer CLI interface
├── parser/
│   ├── __init__.py
│   ├── grammar.lark         # IDL grammar definition
│   └── parser.py            # Parser implementation
├── ast/
│   ├── __init__.py
│   ├── nodes.py             # Pydantic AST node definitions
│   └── serialization.py     # JSON serialization
├── generators/
│   ├── __init__.py
│   ├── base.py              # Abstract base generator
│   ├── cpp.py               # C++ interface generator
│   ├── c_wrapper.py         # C wrapper generator
│   └── swift.py             # Swift binding generator
├── helpers/
│   ├── __init__.py
│   └── minimidl_runtime.hpp # Header-only C++ helper library
├── templates/
│   ├── cpp/
│   │   ├── interface.hpp.j2
│   │   ├── implementation.hpp.j2
│   │   ├── implementation.cpp.j2
│   │   └── CMakeLists.txt.j2
│   ├── c_wrapper/
│   │   ├── wrapper.h.j2
│   │   ├── wrapper.cpp.j2
│   │   ├── exports.def.j2
│   │   └── CMakeLists.txt.j2
│   └── swift/
│       ├── Package.swift.j2
│       ├── wrapper.swift.j2
│       └── Types.swift.j2
└── utils/
    ├── __init__.py
    └── common.py            # Shared utilities
```

## IDL Language Specification

### Basic Syntax
- Comments: `//` (single line only)
- Case-sensitive
- Semicolons optional
- Whitespace-agnostic

### Core Constructs

#### Namespaces
```idl
namespace MyLibrary {
    // interfaces, enums, typedefs, constants
}
```

#### Data Types
**Primitives:**
- `bool`
- `int32_t`, `int64_t`
- `float`, `double`
- `string_t` (maps to IDynamicString interface)

**Containers:**
- `Type[]` (arrays)
- `dict<KeyType, ValueType>` (dictionaries/maps)
- `set<Type>` (sets, implemented as dict with ignored values)

**Nullability:**
- `Type` (non-nullable)
- `Type?` (nullable, maps to Swift optionals)

#### Constants
```idl
const int32_t MAX_SIZE = 100;
const int32_t HEX_VALUE = 0xFF;
const int32_t BINARY_VALUE = 0b11010010;
const int32_t SHIFTED_VALUE = (1 << 8);
```
- Support: decimal, hex (0x), binary (0b), bit-shifting
- No octal support
- No string constants

#### Enums
```idl
enum Status : int32_t {
    UNKNOWN = 0,
    ACTIVE = 1,
    ERROR = 2
}

enum Flags : int32_t {
    NONE = 0,
    READ = (1 << 0),
    WRITE = (1 << 1),
    EXECUTE = (1 << 2)
}
```
- Must specify backing type
- Support bitflags with shifting
- Compiler flag determines C++ enum vs enum class

#### Typedefs
```idl
typedef int32_t UserId;
typedef string_t UserName;
```

#### Interfaces
```idl
interface IUserManager {
    // Read-only property
    int32_t UserCount;
    
    // Read-write property
    string_t DefaultName writable;
    
    // Methods
    string_t GetUserName(int32_t userId);
    void SetUserName(int32_t userId, string_t name);
    
    // Nullable returns
    IUser? FindUser(string_t name);
    
    // Arrays and collections
    string_t[] GetAllUserNames();
    dict<int32_t, string_t> GetUserMapping();
}
```

#### Forward Declarations
```idl
interface IUser;
interface IManager;

interface IUser {
    IManager GetManager();
}

interface IManager {
    IUser[] GetUsers();
}
```

## Code Generation Requirements

### C++ Interface Generation
- Pure virtual classes (no data members)
- Abstract base classes with factory pattern
- Namespace mapping from IDL
- Header guards and proper includes
- Clean, readable code formatting

### C++ Helper Library (minimidl_runtime.hpp)
**String handling:**
```cpp
class IDynamicString {
public:
    virtual ~IDynamicString() = default;
    virtual void SetValue(const char* value) = 0;
    virtual const char* GetValue() const = 0;
    virtual void AddRef() = 0;
    virtual void Release() = 0;
};

// Helper implementation
class string_t : public IDynamicString {
    // std::string wrapper with refcounting
};
```

**Container abstractions:**
```cpp
template<typename T>
class array_t {
    // Refcounted array container
public:
    size_t size() const;
    T& operator[](size_t index);
    void push_back(const T& item);
    // Iterator support
};

template<typename K, typename V>
class dict_t {
    // Refcounted dictionary container
};
```

**Refcounting base:**
```cpp
class RefCounted {
protected:
    std::atomic<int32_t> m_refCount{1};
public:
    void AddRef();
    void Release();
    virtual ~RefCounted() = default;
};
```

### C Wrapper Generation
- C-compatible function signatures
- Proper error handling (return codes, not exceptions)
- Memory management through refcounting
- Cross-platform compatibility (Windows .def files, macOS exports)

### Swift Binding Generation
- Swift Package Manager integration
- Native Swift types (String, Array, Dictionary)
- Optional type mapping
- ARC integration with C++ refcounting
- Clean object-oriented Swift interfaces

## User Experience Workflows

### C++ Developer Experience
```bash
minimidl --target cpp myapi.idl
```

**Generated structure:**
```
output/
├── CMakeLists.txt           # Master build configuration
├── interfaces/
│   └── IMyAPI.hpp          # Generated pure virtual interfaces
├── implementation/
│   ├── MyAPI.hpp           # Stub class declarations
│   └── MyAPI.cpp           # Stub implementations (TODO comments)
├── c_wrapper/
│   ├── wrapper.h           # C API declarations
│   ├── wrapper.cpp         # C wrapper implementation
│   └── exports.def         # Windows export definitions
├── testbed/
│   ├── main.c              # Console test application
│   └── CMakeLists.txt      # Test executable build
└── helpers/
    └── minimidl_runtime.hpp # Runtime helper library
```

### Swift Developer Experience
```bash
minimidl --target swift myapi.idl
```

**Generated structure:**
```
swift_output/
├── Package.swift           # SPM package definition
├── Sources/
│   ├── MyAPI/
│   │   ├── MyAPI.swift     # Swift wrapper classes
│   │   └── Types.swift     # Swift type definitions
│   └── CMyAPI/             # C wrapper module
│       ├── module.modulemap
│       └── wrapper.h       # C headers
├── Tests/
│   └── MyAPITests/
│       └── BasicTests.swift # Generated test cases
└── README.md               # Build instructions
```

## Python Code Quality Standards

### Dependencies
- **Core:** uv, lark, pydantic, typer, jinja2, loguru
- **Development:** black, ruff, isort, pylint, mypy
- **Optional:** confz (for configuration if needed)

### Code Quality Requirements
- **Formatting:** black (line length 88)
- **Linting:** ruff (aggressive settings)
- **Import sorting:** isort
- **Type checking:** mypy (strict mode)
- **Documentation:** Google-style docstrings
- **Error handling:** loguru for logging

### Project Configuration
- **pyproject.toml:** uv-based project setup
- **justfile:** Build automation (test, lint, format, build)
- **Python 3.13+** compatibility

## Testing Strategy

### Unit Tests
- IDL parsing tests (valid/invalid syntax)
- AST generation verification
- Code generation output validation
- Cross-platform compatibility tests

### Integration Tests
- Complete workflow tests (IDL → C++ → Swift)
- Generated code compilation tests
- Runtime functionality tests

### Test Structure
```
tests/
├── unit/
│   ├── test_parser.py
│   ├── test_ast.py
│   └── test_generators.py
├── integration/
│   ├── test_workflows.py
│   └── test_generated_code.py
└── fixtures/
    ├── valid_idl/
    ├── invalid_idl/
    └── expected_output/
```

## Documentation Requirements

### Technology Stack
- **MkDocs Material** for documentation
- **Mermaid** for architecture diagrams
- **Python autodoc** for internal code documentation

### Documentation Structure
```
docs/
├── index.md                # Getting started
├── language-reference.md   # Complete IDL syntax
├── cpp-integration.md      # C++ developer guide
├── swift-integration.md    # Swift developer guide
├── examples/
│   ├── basic-example.md
│   ├── advanced-features.md
│   └── real-world-usage.md
├── api-reference/          # Auto-generated from code
└── troubleshooting.md
```

## Build and Development Environment

### Development Commands (justfile)
```bash
just install      # Install dependencies with uv
just test         # Run all tests
just lint         # Run linting (ruff, pylint)
just format       # Format code (black, isort)
just type-check   # Run mypy
just build        # Build package
just docs         # Build documentation
just clean        # Clean build artifacts
```

### Git Workflow
- Standard feature branch workflow
- Pre-commit hooks for code quality
- Automated testing on push
- Version tagging for releases

## CLI Interface Design

### Primary Commands
```bash
# Generate C++ bindings
minimidl --target cpp --output ./cpp_output myapi.idl

# Generate Swift bindings
minimidl --target swift --output ./swift_output myapi.idl

# Generate all targets
minimidl --target all --output ./output myapi.idl

# Cache AST for large projects
minimidl --cache-ast --ast-file myapi.ast myapi.idl

# Use cached AST
minimidl --from-ast myapi.ast --target cpp --output ./cpp_output
```

### Options
- `--target`: cpp, swift, all
- `--output`: Output directory
- `--cache-ast`: Save AST to file
- `--from-ast`: Generate from cached AST
- `--enum-class`: Generate C++ enum class instead of enum
- `--verbose`: Detailed logging
- `--help`: Show help information

## Success Criteria

### Technical Requirements
1. **Complete IDL parsing** with comprehensive error reporting
2. **Clean C++ interface generation** with proper abstractions
3. **Functional C wrapper generation** with cross-platform support
4. **Native Swift binding generation** with proper type mapping
5. **Comprehensive test coverage** (>90%)
6. **Complete documentation** with examples
7. **Professional code quality** (passes all linting/type checking)

### User Experience Requirements
1. **Single command workflow** for each target language
2. **Buildable output** with no manual intervention required
3. **Clear error messages** for IDL syntax errors
4. **Comprehensive examples** and documentation
5. **Professional project structure** suitable for production use

## Development Phases

This project should be developed in discrete phases:

1. **Phase 1:** Core parser and AST (Lark grammar, Pydantic models)
2. **Phase 2:** C++ interface generator with templates
3. **Phase 3:** C wrapper generator with cross-platform support
4. **Phase 4:** Swift binding generator with SPM integration
5. **Phase 5:** CLI interface and user experience polish
6. **Phase 6:** Comprehensive testing and documentation
7. **Phase 7:** Build automation and packaging

## ACKNOWLEDGMENT REQUIRED

**Before proceeding with any implementation, you must:**
1. Confirm understanding of this vision document
2. Acknowledge the phase-based development approach
3. Confirm you will wait for specific task assignments
4. Ask any clarifying questions about the requirements

**DO NOT BEGIN CODING UNTIL EXPLICITLY INSTRUCTED TO START A SPECIFIC PHASE.**