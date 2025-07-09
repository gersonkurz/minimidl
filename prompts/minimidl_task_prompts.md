# MinimIDL Task Prompts for Claude Code

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

**2. Dependencies Configuration**
- Core: lark, pydantic, typer, jinja2, loguru
- Development: black, ruff, isort, pylint, mypy, pytest
- Configure pyproject.toml with proper metadata and scripts

**3. Lark Grammar Implementation**
Create complete grammar.lark file supporting:
- Namespaces, interfaces, enums, typedefs, constants
- All data types (primitives, string_t, arrays, dicts, sets)
- Nullability syntax (Type?)
- Properties (readonly and writable)
- Methods with parameters and return types
- Forward declarations
- Comments (//)
- Numeric literals (decimal, hex, binary, bit-shifting)

**4. Parser Implementation**
- Lark-based parser class
- Error handling with line numbers and context
- Basic AST node creation (simple dict/list structures for now)

**5. Basic Testing**
- Unit tests for valid IDL parsing
- Error handling tests for invalid syntax
- Test fixtures with example IDL files

**6. Build Automation**
- justfile with: install, test, lint, format, clean commands
- Pre-commit hook setup

### Success Criteria
- `just install` sets up complete development environment
- `just test` runs all parser tests successfully
- Parser correctly handles all IDL syntax from vision document
- Clean code quality (passes black, ruff, mypy)
- Comprehensive error reporting for syntax errors

### Example IDL Test Cases
Include test cases for:
```idl
// Basic interface
namespace TestAPI {
    interface IUser {
        string_t GetName();
        void SetName(string_t name);
        int32_t Age;
        bool IsActive writable;
    }
}

// Complex example with all features
namespace ComplexAPI {
    const int32_t MAX_USERS = 0xFF;
    const int32_t FLAGS = (1 << 8);
    
    typedef int32_t UserId;
    
    enum Status : int32_t {
        UNKNOWN = 0,
        ACTIVE = 1,
        INACTIVE = 2
    }
    
    interface IUserManager;
    
    interface IUser {
        UserId GetId();
        string_t? GetOptionalName();
        Status GetStatus();
        IUserManager GetManager();
        string_t[] GetTags();
        dict<string_t, string_t> GetProperties();
    }
    
    interface IUserManager {
        IUser[] GetUsers();
        IUser? FindUser(UserId id);
        void AddUser(IUser user);
    }
}
```

---

## Task 2: AST Node Definitions and Serialization

### Objective
Replace simple parser output with proper Pydantic AST node definitions and implement JSON serialization for AST caching.

### Prerequisites
- Task 1 completed successfully
- Parser generating basic AST structures

### Deliverables

**1. AST Node Definitions**
```
minimidl/ast/
├── __init__.py
├── nodes.py                 # All Pydantic AST node classes
└── serialization.py         # JSON save/load functionality
```

**2. Pydantic AST Node Classes**
Create comprehensive node hierarchy:
- `ASTNode` (base class)
- `Namespace`, `Interface`, `Enum`, `Typedef`, `Constant`
- `Method`, `Property`, `Parameter`
- `Type`, `ArrayType`, `DictType`, `SetType`, `NullableType`
- `EnumValue`, `ConstantValue`
- `ForwardDeclaration`

**3. Parser Integration**
- Update parser.py to generate proper AST nodes
- Transformer class to convert Lark tree to AST
- Type validation and semantic analysis

**4. JSON Serialization**
- AST to JSON conversion with proper type handling
- JSON to AST deserialization
- File-based caching system

**5. Enhanced Testing**
- AST node validation tests
- Serialization round-trip tests
- Semantic analysis tests (type checking, forward references)

### Success Criteria
- All IDL constructs represented as proper AST nodes
- JSON serialization preserves all AST information
- Parser performs basic semantic validation
- AST nodes have comprehensive type hints
- Full test coverage for all node types

### Example AST Structure
```python
@dataclass
class Interface(ASTNode):
    name: str
    methods: List[Method]
    properties: List[Property]
    forward_declarations: List[str]
    
@dataclass
class Method(ASTNode):
    name: str
    return_type: Type
    parameters: List[Parameter]
    
@dataclass
class Type(ASTNode):
    name: str
    nullable: bool = False
    
@dataclass
class ArrayType(Type):
    element_type: Type
```

---

## Task 3: C++ Interface Generator

### Objective
Implement the C++ interface generator with Jinja2 templates to create clean, professional C++ header files.

### Prerequisites
- Task 2 completed successfully
- AST nodes properly defined and tested

### Deliverables

**1. Generator Infrastructure**
```
minimidl/generators/
├── __init__.py
├── base.py                  # Abstract base generator class
└── cpp.py                   # C++ interface generator
```

**2. C++ Templates**
```
minimidl/templates/cpp/
├── interface.hpp.j2         # Interface class template
├── implementation.hpp.j2    # Stub implementation header
├── implementation.cpp.j2    # Stub implementation source
├── factory.hpp.j2           # Factory pattern template
└── CMakeLists.txt.j2        # CMake build configuration
```

**3. C++ Helper Library**
```
minimidl/helpers/
└── minimidl_runtime.hpp     # Header-only runtime library
```

**4. C++ Generator Implementation**
- AST traversal and code generation
- Namespace mapping
- Type conversion (IDL types → C++ types)
- Property generation (getters/setters)
- Method signature generation
- Forward declaration handling

**5. Template System**
- Jinja2 environment setup
- Template inheritance for common patterns
- Cross-platform compatibility (Windows/macOS/Linux)

### Success Criteria
- Generates compilable C++ header files
- Clean, readable, professionally formatted code
- Proper namespace organization
- Complete CMake integration
- All IDL constructs properly mapped to C++
- Stub implementations with TODO comments for user completion

### Example Generated Output
```cpp
// Generated from TestAPI.idl
#pragma once

#include "minimidl_runtime.hpp"

namespace TestAPI {
    
    class IUser : public minimidl::RefCounted {
    public:
        virtual ~IUser() = default;
        
        // Properties
        virtual minimidl::string_t GetName() const = 0;
        virtual void SetName(minimidl::string_t value) = 0;
        virtual int32_t GetAge() const = 0;
        virtual bool GetIsActive() const = 0;
        virtual void SetIsActive(bool value) = 0;
        
        // Methods
        virtual void UpdateProfile(minimidl::string_t name, int32_t age) = 0;
        virtual minimidl::array_t<minimidl::string_t> GetTags() const = 0;
    };
    
    // Factory function
    extern "C" IUser* CreateUser();
}
```

---

## Task 4: C Wrapper Generator

### Objective
Implement the C wrapper generator that creates C-compatible APIs from C++ interfaces, with cross-platform export handling.

### Prerequisites
- Task 3 completed successfully
- C++ interface generation working properly

### Deliverables

**1. C Wrapper Generator**
```
minimidl/generators/
└── c_wrapper.py             # C wrapper generator
```

**2. C Wrapper Templates**
```
minimidl/templates/c_wrapper/
├── wrapper.h.j2             # C header declarations
├── wrapper.cpp.j2           # C wrapper implementation
├── exports.def.j2           # Windows export definitions
└── CMakeLists.txt.j2        # C wrapper build configuration
```

**3. C Wrapper Generation Logic**
- C-compatible function signatures
- Object handle management (void* pointers)
- String handling through const char*
- Array/dictionary iteration interfaces
- Memory management through refcounting
- Error handling (return codes, not exceptions)

**4. Cross-Platform Export Handling**
- Windows: .def file generation
- macOS/Linux: __attribute__((visibility("default")))
- CMake configuration for both platforms

**5. Test Harness Generation**
```
minimidl/templates/c_wrapper/
├── testbed.c.j2             # Console test application
└── testbed_cmake.txt.j2     # Test executable CMake
```

### Success Criteria
- C wrapper functions are pure C compatible
- Proper memory management without leaks
- Cross-platform compilation (Windows/macOS/Linux)
- Generated test harness demonstrates all functionality
- Complete CMake integration
- Professional error handling

### Example Generated C API
```c
// Generated C API from TestAPI.idl
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// Object handles
typedef void* IUser_Handle;

// IUser interface
IUser_Handle IUser_Create();
void IUser_Release(IUser_Handle handle);

// Properties
const char* IUser_GetName(IUser_Handle handle);
void IUser_SetName(IUser_Handle handle, const char* value);
int32_t IUser_GetAge(IUser_Handle handle);

// Methods
void IUser_UpdateProfile(IUser_Handle handle, const char* name, int32_t age);

// Array handling
size_t IUser_GetTags_Count(IUser_Handle handle);
const char* IUser_GetTags_Item(IUser_Handle handle, size_t index);

#ifdef __cplusplus
}
#endif
```

---

## Task 5: Swift Binding Generator

### Objective
Implement the Swift binding generator that creates native Swift APIs with proper type mapping and Swift Package Manager integration.

### Prerequisites
- Task 4 completed successfully
- C wrapper generation working properly

### Deliverables

**1. Swift Generator**
```
minimidl/generators/
└── swift.py                 # Swift binding generator
```

**2. Swift Templates**
```
minimidl/templates/swift/
├── Package.swift.j2         # Swift Package Manager configuration
├── wrapper.swift.j2         # Swift wrapper classes
├── Types.swift.j2           # Swift type definitions
├── module.modulemap.j2      # C module mapping
└── README.md.j2             # Swift package documentation
```

**3. Swift Code Generation**
- Native Swift class generation
- Type mapping (C types → Swift types)
- Optional type handling (nullable → Swift optionals)
- Array/Dictionary bridging
- ARC integration with C++ refcounting
- Error handling with Swift patterns

**4. Swift Package Manager Integration**
- Complete Package.swift configuration
- C module wrapping
- Target dependencies
- Build configuration

**5. Swift Test Generation**
```
minimidl/templates/swift/
├── BasicTests.swift.j2      # Unit tests for generated code
└── IntegrationTests.swift.j2 # Integration tests
```

### Success Criteria
- Generated Swift code compiles without warnings
- Native Swift API experience (no C interop visible)
- Proper Swift optionals handling
- Clean memory management (ARC + refcounting)
- Complete SPM package structure
- Comprehensive test coverage

### Example Generated Swift API
```swift
// Generated from TestAPI.idl
import Foundation

public class User {
    private let handle: OpaquePointer
    
    public init() {
        self.handle = IUser_Create()
    }
    
    deinit {
        IUser_Release(handle)
    }
    
    // Properties
    public var name: String {
        get {
            let cString = IUser_GetName(handle)
            return cString != nil ? String(cString: cString!) : ""
        }
        set {
            IUser_SetName(handle, newValue)
        }
    }
    
    public var age: Int32 {
        get {
            return IUser_GetAge(handle)
        }
    }
    
    // Methods
    public func updateProfile(name: String, age: Int32) {
        IUser_UpdateProfile(handle, name, age)
    }
    
    public func getTags() -> [String] {
        let count = IUser_GetTags_Count(handle)
        var result: [String] = []
        for i in 0..<count {
            if let cString = IUser_GetTags_Item(handle, i) {
                result.append(String(cString: cString))
            }
        }
        return result
    }
}
```

---

## Task 6: CLI Interface and User Experience

### Objective
Implement the complete CLI interface with Typer, user experience workflows, and output project generation.

### Prerequisites
- Tasks 1-5 completed successfully
- All generators working properly

### Deliverables

**1. CLI Implementation**
```
minimidl/
├── cli.py                   # Complete Typer CLI interface
└── workflows/
    ├── __init__.py
    ├── cpp_workflow.py      # C++ project generation
    └── swift_workflow.py    # Swift project generation
```

**2. CLI Commands**
- Primary generation commands (--target cpp/swift/all)
- AST caching commands (--cache-ast, --from-ast)
- Configuration options (--enum-class, --output, --verbose)
- Help and version information

**3. User Experience Workflows**
- Complete project structure generation
- Buildable output with no manual intervention
- Professional project organization
- Clear instructions and README files

**4. Error Handling and Validation**
- Comprehensive input validation
- Clear error messages with suggestions
- Graceful handling of edge cases
- Detailed logging with loguru

**5. Integration Testing**
- End-to-end workflow tests
- Generated code compilation tests
- Cross-platform compatibility tests

### Success Criteria
- Single command generates complete, buildable projects
- Professional output suitable for production use
- Comprehensive error handling and user guidance
- Clean CLI interface with intuitive commands
- All output projects compile and run successfully

### Example CLI Usage
```bash
# Generate C++ project
minimidl --target cpp --output ./my_cpp_api myapi.idl

# Generate Swift project
minimidl --target swift --output ./my_swift_api myapi.idl

# Generate all targets
minimidl --target all --output ./my_api myapi.idl

# Use AST caching for large projects
minimidl --cache-ast --ast-file myapi.ast myapi.idl
minimidl --from-ast myapi.ast --target cpp --output ./cpp_api
```

---

## Task 7: Testing, Documentation, and Packaging

### Objective
Implement comprehensive testing, create complete documentation with MkDocs, and prepare the package for distribution.

### Prerequisites
- Tasks 1-6 completed successfully
- All functionality working end-to-end

### Deliverables

**1. Comprehensive Testing**
```
tests/
├── unit/                    # Unit tests for all modules
├── integration/             # End-to-end workflow tests
├── fixtures/               # Test IDL files and expected outputs
└── generated/              # Generated code compilation tests
```

**2. Documentation System**
```
docs/
├── mkdocs.yml              # MkDocs configuration
├── index.md                # Getting started guide
├── language-reference.md   # Complete IDL syntax reference
├── cpp-integration.md      # C++ developer guide
├── swift-integration.md    # Swift developer guide
├── examples/               # Comprehensive examples
├── api-reference/          # Auto-generated API docs
└── troubleshooting.md      # Common issues and solutions
```

**3. Build and Packaging**
- Complete pyproject.toml with all metadata
- justfile with all development commands
- GitHub Actions workflows (optional)
- Package distribution preparation

**4. Example Projects**
- Complete working examples
- Real-world usage scenarios
- Performance benchmarks
- Integration guides

**5. Quality Assurance**
- Code coverage reports (>90%)
- Performance testing
- Cross-platform verification
- Professional code quality

### Success Criteria
- All tests pass on macOS (primary target)
- Complete documentation with examples
- Professional package quality
- Ready for production use
- Comprehensive troubleshooting guide

---

## Operational Instructions for Task Execution

### How to Request Task Execution
```
Please execute Task [NUMBER]: [TASK_NAME]

Focus on: [any specific areas of concern]
Additional requirements: [any modifications or additions]
```

### How to Provide Feedback
```
Task [NUMBER] feedback:
- Issue: [description of problem]
- Expected: [what should happen]
- Actual: [what actually happened]
- Action: [modify/redo/continue]
```

### How to Iterate on Tasks
```
Please refine Task [NUMBER] with these changes:
1. [specific change 1]
2. [specific change 2]
3. [specific change 3]

Keep everything else the same.
```

### Progress Tracking
After each task completion, provide:
- Summary of what was accomplished
- Any deviations from the original plan
- Issues encountered and how they were resolved
- Readiness for the next task

### Quality Gates
Each task must pass:
- All existing tests continue to pass
- New functionality has comprehensive tests
- Code quality checks pass (black, ruff, mypy)
- Documentation is updated appropriately
- Git commits are clean and well-documented

Remember: Each task builds on the previous ones. Don't proceed to the next task until the current one meets all success criteria.