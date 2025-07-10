# C++ Integration Guide

This guide covers advanced topics for using MinimIDL-generated C++ code in your projects.

## Generated Code Structure

MinimIDL generates modern C++17 code with these characteristics:

- Header-only interfaces
- No runtime dependencies
- RAII and move semantics
- `constexpr` where applicable
- Namespace preservation

## Interface Implementation

### Basic Implementation

```cpp
#include "myapi.hpp"

class MyServiceImpl : public MyAPI::IService {
private:
    std::string name_;
    bool running_ = false;
    
public:
    // Implement pure virtual methods
    std::string GetName() const override {
        return name_;
    }
    
    void Start() override {
        running_ = true;
        // Implementation
    }
    
    bool IsRunning() const override {
        return running_;
    }
};
```

### Factory Pattern

```cpp
namespace MyAPI {

// Factory function
std::shared_ptr<IService> CreateService(const std::string& config) {
    auto service = std::make_shared<MyServiceImpl>();
    service->Configure(config);
    return service;
}

} // namespace MyAPI
```

## Memory Management

### Smart Pointers

Always use smart pointers with interfaces:

```cpp
// Recommended
auto service = std::make_shared<MyServiceImpl>();
std::unique_ptr<IService> unique_service = std::make_unique<MyServiceImpl>();

// Pass by reference when ownership isn't transferred
void UseService(const IService& service) {
    auto name = service.GetName();
}

// Return shared_ptr for shared ownership
std::shared_ptr<IService> GetGlobalService() {
    static auto service = std::make_shared<MyServiceImpl>();
    return service;
}
```

### Object Lifetime

```cpp
class Manager {
    std::vector<std::shared_ptr<IWorker>> workers_;
    
public:
    void AddWorker(std::shared_ptr<IWorker> worker) {
        workers_.push_back(std::move(worker));
    }
    
    void ProcessAll() {
        for (const auto& worker : workers_) {
            worker->DoWork();
        }
    }
};
```

## Collections

### Working with Arrays

```cpp
// Implementing array return
std::vector<std::string> GetTags() const override {
    return tags_;  // Move semantics
}

// Implementing array property
std::vector<int32_t> GetValues() const override {
    return values_;
}

void SetValues(std::vector<int32_t> values) override {
    values_ = std::move(values);
}
```

### Dictionaries and Sets

```cpp
// Dictionary implementation
std::unordered_map<std::string, std::string> GetConfig() const override {
    return config_;
}

// Set implementation  
std::unordered_set<int32_t> GetUniqueIds() const override {
    return {1, 2, 3, 4, 5};
}
```

## Nullable Types

### Optional Returns

```cpp
std::optional<std::string> FindValue(const std::string& key) const override {
    auto it = map_.find(key);
    if (it != map_.end()) {
        return it->second;
    }
    return std::nullopt;
}

// Using nullable interface references
std::shared_ptr<IUser> FindUser(const std::string& id) override {
    auto it = users_.find(id);
    if (it != users_.end()) {
        return it->second;
    }
    return nullptr;  // Null shared_ptr
}
```

### Checking Nullable Values

```cpp
auto user = manager->FindUser("123");
if (user) {
    std::cout << "Found: " << user->GetName() << "\n";
} else {
    std::cout << "User not found\n";
}
```

## Enum Usage

### Type-Safe Enums

```cpp
void ProcessStatus(MyAPI::Status status) {
    switch (status) {
    case MyAPI::Status::OK:
        // Handle OK
        break;
    case MyAPI::Status::ERROR:
        // Handle error
        break;
    default:
        // Handle unknown
        break;
    }
}

// Enum to integer conversion
int32_t value = static_cast<int32_t>(MyAPI::Status::OK);

// Integer to enum (with validation)
auto status = static_cast<MyAPI::Status>(value);
```

## Properties

### Implementing Properties

```cpp
class ConfigImpl : public IConfig {
private:
    std::string name_;
    bool enabled_ = false;
    
public:
    // Read-only property
    std::string GetName() const override {
        return name_;
    }
    
    // Writable property
    bool GetEnabled() const override {
        return enabled_;
    }
    
    void SetEnabled(bool value) override {
        enabled_ = value;
    }
};
```

## Thread Safety

### Making Implementations Thread-Safe

```cpp
class ThreadSafeService : public IService {
private:
    mutable std::mutex mutex_;
    std::string data_;
    
public:
    std::string GetData() const override {
        std::lock_guard<std::mutex> lock(mutex_);
        return data_;
    }
    
    void SetData(const std::string& value) override {
        std::lock_guard<std::mutex> lock(mutex_);
        data_ = value;
    }
};
```

## Integration with CMake

### Using Generated Code

```cmake
# Include generated headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/generated/include)

# Your executable
add_executable(myapp 
    src/main.cpp
    src/service_impl.cpp
)

# Link with C++17
target_compile_features(myapp PRIVATE cxx_std_17)
```

### As a Library

```cmake
# Create interface library
add_library(myapi INTERFACE)
target_include_directories(myapi INTERFACE 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/generated/include>
    $<INSTALL_INTERFACE:include>
)

# Use in other targets
target_link_libraries(myapp PRIVATE myapi)
```

## Testing

### Unit Testing Interfaces

```cpp
#include <gtest/gtest.h>
#include "myapi.hpp"

class MockService : public MyAPI::IService {
public:
    MOCK_METHOD(std::string, GetName, (), (const, override));
    MOCK_METHOD(void, Start, (), (override));
};

TEST(ServiceTest, BasicOperation) {
    auto service = std::make_shared<MyServiceImpl>();
    
    EXPECT_FALSE(service->IsRunning());
    service->Start();
    EXPECT_TRUE(service->IsRunning());
}
```

## Performance Tips

1. **Use Move Semantics**: Return containers by value
2. **Pass by Const Reference**: For large objects in parameters
3. **Reserve Capacity**: When building collections
4. **Avoid Virtual Calls in Loops**: Cache results when possible

```cpp
// Good: Move semantics
std::vector<std::string> GetLargeData() override {
    std::vector<std::string> result;
    result.reserve(1000);  // Reserve capacity
    // Fill result...
    return result;  // Moved, not copied
}

// Good: Const reference for input
void ProcessData(const std::vector<std::string>& data) override {
    // Process without copying
}
```

## Advanced Patterns

### Visitor Pattern

```cpp
class IVisitor {
public:
    virtual ~IVisitor() = default;
    virtual void Visit(IUser& user) = 0;
    virtual void Visit(IPost& post) = 0;
};

class StatsVisitor : public IVisitor {
    int user_count_ = 0;
    int post_count_ = 0;
    
public:
    void Visit(IUser& user) override { user_count_++; }
    void Visit(IPost& post) override { post_count_++; }
};
```

### PIMPL for ABI Stability

```cpp
// In header (myservice.hpp)
class MyService : public IService {
    class Impl;
    std::unique_ptr<Impl> pimpl_;
    
public:
    MyService();
    ~MyService();
    
    // IService implementation
    std::string GetName() const override;
};

// In source (myservice.cpp)
class MyService::Impl {
    std::string name_;
public:
    std::string GetName() const { return name_; }
};

MyService::MyService() : pimpl_(std::make_unique<Impl>()) {}
MyService::~MyService() = default;

std::string MyService::GetName() const {
    return pimpl_->GetName();
}
```

## Debugging

### Adding Debug Output

```cpp
#ifdef DEBUG
#define LOG(msg) std::cerr << "[" << __FUNCTION__ << "] " << msg << std::endl
#else
#define LOG(msg)
#endif

class DebugService : public IService {
    void Start() override {
        LOG("Starting service");
        // Implementation
    }
};
```

## Best Practices

1. **Always Use Override**: Catch interface changes at compile time
2. **Prefer make_shared**: For better performance and exception safety
3. **Document Ownership**: Be clear about who owns what
4. **Use Const Correctly**: Mark methods const when they don't modify state
5. **Handle All Enum Values**: Add default case or use -Wswitch
6. **Validate Input**: Especially for public APIs
7. **RAII Everything**: Resources should be managed automatically

## Common Pitfalls

1. **Slicing**: Always pass interfaces by reference or pointer
2. **Dangling References**: Be careful with lifetime of returned references
3. **Thread Safety**: Interfaces don't guarantee thread safety
4. **Exception Safety**: Consider what happens if methods throw
5. **Virtual Destructor**: Already handled by generated code