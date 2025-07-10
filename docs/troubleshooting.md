# Troubleshooting Guide

This guide helps you resolve common issues when using MinimIDL.

## Installation Issues

### Python Version Error

**Problem**: `ERROR: MinimIDL requires Python 3.13 or later`

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.13+ using pyenv
pyenv install 3.13.0
pyenv local 3.13.0

# Or use UV to manage Python versions
uv python install 3.13
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'minimidl'`

**Solution**:
```bash
# Ensure MinimIDL is installed
pip install minimidl

# Or if using virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install minimidl
```

## IDL Parsing Errors

### Syntax Errors

**Problem**: `Unexpected token 'X' at line Y, column Z`

**Common Causes and Solutions**:

1. **Missing semicolon**:
```idl
// ❌ Wrong
interface IExample {
    void Method()  // Missing semicolon
}

// ✅ Correct
interface IExample {
    void Method();
}
```

2. **Invalid enum backing type**:
```idl
// ❌ Wrong
enum Status {  // Missing backing type
    OK = 0
}

// ✅ Correct
enum Status : int32_t {
    OK = 0
}
```

3. **Writable on methods**:
```idl
// ❌ Wrong
void SetValue(string_t value) writable;

// ✅ Correct - writable is only for properties
string_t value writable;
```

### Type Not Found

**Problem**: `ValidationError: Unknown type 'TypeName'`

**Solutions**:

1. **Check type is defined**:
```idl
namespace API {
    // Define before use
    interface IUser;  // Forward declaration
    
    interface IManager {
        IUser GetUser();  // Now valid
    }
    
    interface IUser {
        string_t GetName();
    }
}
```

2. **Check namespace**:
```idl
// Types from different namespaces must be fully qualified
// MinimIDL currently doesn't support cross-namespace references
```

### Duplicate Type Names

**Problem**: `ValidationError: Duplicate type definition: TypeName`

**Solution**:
```idl
namespace API {
    interface IUser { }
    // interface IUser { }  // ❌ Duplicate
    
    // Use different names or namespaces
    interface IUserDetails { }  // ✅ Different name
}
```

## Code Generation Issues

### No Output Generated

**Problem**: Command runs but no files are created

**Check**:
```bash
# Verify output directory
python -m minimidl generate api.idl --target cpp --output ./output

# Check for validation errors
python -m minimidl validate api.idl

# Enable verbose mode
python -m minimidl --verbose generate api.idl --target cpp
```

### Generated Code Doesn't Compile

**C++ Issues**:

1. **Missing C++17 support**:
```cmake
# Add to CMakeLists.txt
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
```

2. **Header not found**:
```cpp
// Check include paths
#include "generated/api.hpp"  // Relative to include directory
```

**Swift Issues**:

1. **Module not found**:
```bash
# Build C libraries first
cd YourAPI
./build_c.sh
./build_swift.sh
```

2. **Undefined symbols**:
```
# Ensure C wrapper is linked
# Check module.modulemap points to correct header
```

## Runtime Issues

### C++ Runtime Errors

**Null Pointer Access**:
```cpp
// ❌ Wrong
auto user = GetUser();
user->GetName();  // Crash if null

// ✅ Correct
auto user = GetUser();
if (user) {
    user->GetName();
}
```

**Pure Virtual Call**:
```cpp
// Ensure all pure virtual methods are implemented
class MyService : public IService {
    // Must implement ALL methods from IService
};
```

### Swift Runtime Errors

**Force Unwrap Crash**:
```swift
// ❌ Wrong
let user = api.findUser(id: "123")!  // Crash if nil

// ✅ Correct
if let user = api.findUser(id: "123") {
    // Use user
}
```

**Memory Issues**:
```swift
// Check for retain cycles
class Manager {
    weak var delegate: ManagerDelegate?  // Use weak
}
```

## Platform-Specific Issues

### macOS

**Code Signing**:
```bash
# Disable code signing for development
cmake -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" ..
```

**Swift Package Manager**:
```bash
# Clear cache if having issues
rm -rf .build
swift package clean
swift build
```

### Linux

**Missing Dependencies**:
```bash
# Install build tools
sudo apt-get update
sudo apt-get install build-essential cmake

# For Swift
wget https://swift.org/builds/swift-5.9-release/ubuntu2204/swift-5.9-RELEASE/swift-5.9-RELEASE-ubuntu22.04.tar.gz
```

### Windows

**Path Issues**:
```powershell
# Use forward slashes or raw strings
python -m minimidl generate C:/path/to/api.idl --output C:/output

# Or
python -m minimidl generate "C:\path\to\api.idl" --output "C:\output"
```

**Visual Studio**:
```bash
# Generate for Visual Studio
cd build
cmake .. -G "Visual Studio 17 2022"
```

## Performance Issues

### Slow Parsing

**Large IDL Files**:
```bash
# Use AST caching
python -m minimidl generate large.idl --cache-ast
python -m minimidl generate --from-ast large.ast --target cpp
```

### Memory Usage

**Large Collections**:
```cpp
// Reserve capacity for large vectors
std::vector<Item> GetItems() {
    std::vector<Item> result;
    result.reserve(10000);  // If you know the size
    // Fill result
    return result;
}
```

## Debugging Tips

### Enable Verbose Logging

```bash
# See detailed output
python -m minimidl --verbose generate api.idl --target cpp

# Set log level in Python code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Generated Code

```bash
# Examine generated files
cat generated/include/api.hpp

# Check for TODO comments
grep -r "TODO" generated/
```

### Validate Step by Step

```bash
# 1. Validate IDL
python -m minimidl validate api.idl

# 2. Parse to JSON
python -m minimidl parse api.idl --json -o ast.json

# 3. Examine AST
cat ast.json | jq .

# 4. Generate one target at a time
python -m minimidl generate api.idl --target cpp
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Unexpected token` | Syntax error | Check semicolons, braces |
| `Unknown type` | Type not defined | Add forward declaration |
| `Duplicate type` | Name collision | Rename or use different namespace |
| `Expected X, got Y` | Wrong type usage | Check type compatibility |
| `Reference to undefined` | Missing declaration | Define before use |

## Getting Help

1. **Check the docs**: Read relevant sections of this documentation
2. **Search issues**: Check [GitHub issues](https://github.com/yourusername/minimidl/issues)
3. **Ask questions**: Open a new issue with:
   - MinimIDL version (`minimidl --version`)
   - Platform (OS, Python version)
   - Minimal IDL file that reproduces the issue
   - Complete error message
   - What you've tried

## Reporting Bugs

When reporting bugs, include:

1. **Minimal reproducible example**:
```idl
// Smallest IDL that shows the problem
namespace Test {
    interface IExample {
        // Problem here
    }
}
```

2. **Expected behavior**: What should happen
3. **Actual behavior**: What actually happens
4. **Environment**: OS, Python version, MinimIDL version
5. **Full error output**: Including stack trace