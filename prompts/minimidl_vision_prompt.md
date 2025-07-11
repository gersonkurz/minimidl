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

### Core Memory Management Principle
**All objects that cross language boundaries MUST be reference counted.** This includes:
- All user-defined interfaces
- Strings (which are just interfaces that manage string memory)
- Container objects (arrays, dictionaries, sets)
- Any object returned from or passed to C/Swift bindings

### C++ Interface Generation

#### Fundamental Base Interface
```cpp
// The root of all interfaces - pure virtual
class IRefCounted {
public:
    virtual ~IRefCounted() = default;
    virtual void AddRef() = 0;
    virtual void Release() = 0;
};
```

#### Generated Interfaces
- **ALL interfaces inherit from IRefCounted** (directly or indirectly)
- Pure virtual classes only (no data members, no implementation)
- Namespace mapping from IDL
- Header guards and proper includes
- Methods return interface pointers for all non-primitive types

### C++ Helper Library (minimidl_runtime.hpp)

#### Reference Counting Template
```cpp
// CRTP helper for implementing IRefCounted
template <typename T>
class RefCounted : public T {
public:
    RefCounted() : m_refCount{1} {}
    
    void AddRef() override final {
        ++m_refCount;
    }
    
    void Release() override final {
        if (--m_refCount == 0) {
            delete this;
        }
    }

private:
    mutable std::atomic<int32_t> m_refCount;
};
```

#### String Interface and Implementation
```cpp
// String is just another refcounted interface
class IDynamicString : public IRefCounted {
public:
    virtual const char* GetValue() const = 0;
    virtual void SetValue(const char* value) = 0;
    virtual size_t GetLength() const = 0;
};

// Concrete implementation using the RefCounted template
class DynamicString : public RefCounted<IDynamicString> {
private:
    std::string m_value;
public:
    const char* GetValue() const override { return m_value.c_str(); }
    void SetValue(const char* value) override { m_value = value; }
    size_t GetLength() const override { return m_value.length(); }
};

// Factory function
IDynamicString* CreateDynamicString(const char* value = nullptr);
```

#### Container Interfaces
```cpp
// Arrays are refcounted interfaces too
template<typename T>
class IArray : public IRefCounted {
public:
    virtual size_t GetCount() const = 0;
    virtual T* GetAt(size_t index) = 0;
    virtual void Add(T* item) = 0;
    virtual void RemoveAt(size_t index) = 0;
    virtual void Clear() = 0;
};

// Dictionary interface
template<typename K, typename V>
class IDictionary : public IRefCounted {
public:
    virtual size_t GetCount() const = 0;
    virtual V* Get(const K& key) = 0;
    virtual void Set(const K& key, V* value) = 0;
    virtual void Remove(const K& key) = 0;
    virtual void Clear() = 0;
    // Iterator support...
};
```

### C Wrapper Generation

#### Core Principles
- **ALL string returns MUST be IDynamicString handles**, never `const char*`
- Handle-based API (opaque pointers)
- Consistent error handling through return codes
- Reference counting exposed through C API

#### Example C Wrapper Pattern
```c
// NEVER return const char* directly
// BAD:  const char* ITask_GetId(ITask_Handle handle);
// GOOD: IDynamicString_Handle ITask_GetId(ITask_Handle handle);

// String access pattern
IDynamicString_Handle str = ITask_GetId(task);
const char* cstr = IDynamicString_GetValue(str);
// ... use cstr ...
IDynamicString_Release(str);  // Caller MUST release

// All handles are refcounted
void ITask_AddRef(ITask_Handle handle);
void ITask_Release(ITask_Handle handle);
```

#### Memory Management Rules
- Getters return new references (caller must release)
- Setters take references without transferring ownership
- Collections return enumeration handles, not raw pointers
- Cross-platform compatibility (Windows .def files, macOS exports)

### Swift Binding Generation

#### Swift Memory Management Integration
- Swift wrapper classes hold C handle references
- `deinit` calls the C Release function
- String bridging creates Swift String from IDynamicString
- Collections bridge to native Swift types

#### Example Swift Pattern
```swift
public class Task {
    private let handle: OpaquePointer
    
    init(handle: OpaquePointer) {
        self.handle = handle
        ITask_AddRef(handle)
    }
    
    deinit {
        ITask_Release(handle)
    }
    
    var id: String {
        let strHandle = ITask_GetId(handle)
        defer { IDynamicString_Release(strHandle) }
        return String(cString: IDynamicString_GetValue(strHandle))
    }
}
```

### Summary
The key insight is that **reference counting is not a implementation detail, but the fundamental abstraction** that enables safe memory management across C++, C, and Swift. Every object that crosses language boundaries is refcounted, including strings, which are just specialized refcounted objects that manage string memory.

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