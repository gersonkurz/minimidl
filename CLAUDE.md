
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