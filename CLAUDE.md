
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