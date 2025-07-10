# Basic Examples

This page provides simple examples to get you started with MinimIDL.

## Hello World Interface

The simplest possible interface:

```idl
namespace HelloWorld {
    interface IGreeter {
        string_t SayHello();
    }
}
```

### C++ Implementation

```cpp
#include "helloworld.hpp"
#include <iostream>

class Greeter : public HelloWorld::IGreeter {
public:
    std::string SayHello() override {
        return "Hello, World!";
    }
};

int main() {
    auto greeter = std::make_shared<Greeter>();
    std::cout << greeter->SayHello() << std::endl;
    return 0;
}
```

### Swift Usage

```swift
import HelloWorld

let greeter = Greeter()
print(greeter.sayHello())
```

## Simple Calculator

A basic calculator interface with enums:

```idl
namespace Calculator {
    enum Operation : int32_t {
        ADD = 0,
        SUBTRACT = 1,
        MULTIPLY = 2,
        DIVIDE = 3
    }
    
    interface ICalculator {
        double Calculate(double a, double b, Operation op);
        double GetLastResult();
        void Clear();
    }
}
```

### C++ Implementation

```cpp
class CalculatorImpl : public Calculator::ICalculator {
private:
    double last_result_ = 0.0;
    
public:
    double Calculate(double a, double b, Calculator::Operation op) override {
        switch (op) {
        case Calculator::Operation::ADD:
            last_result_ = a + b;
            break;
        case Calculator::Operation::SUBTRACT:
            last_result_ = a - b;
            break;
        case Calculator::Operation::MULTIPLY:
            last_result_ = a * b;
            break;
        case Calculator::Operation::DIVIDE:
            if (b != 0) {
                last_result_ = a / b;
            } else {
                // Handle division by zero
                last_result_ = std::numeric_limits<double>::infinity();
            }
            break;
        }
        return last_result_;
    }
    
    double GetLastResult() override {
        return last_result_;
    }
    
    void Clear() override {
        last_result_ = 0.0;
    }
};
```

### Swift Usage

```swift
let calc = Calculator()

let sum = calc.calculate(a: 10, b: 5, op: .add)
print("10 + 5 = \(sum)")

let product = calc.calculate(a: 10, b: 5, op: .multiply)
print("10 * 5 = \(product)")

print("Last result: \(calc.getLastResult())")
calc.clear()
```

## User Management

Example with properties and nullable types:

```idl
namespace UserSystem {
    interface IUser {
        // Read-only properties
        string_t id;
        string_t username;
        
        // Writable properties
        string_t email writable;
        bool active writable;
        
        // Methods
        string_t GetFullName();
        void UpdatePassword(string_t newPassword);
    }
    
    interface IUserManager {
        IUser? FindUserById(string_t id);
        IUser? FindUserByEmail(string_t email);
        IUser CreateUser(string_t username, string_t email);
        bool DeleteUser(string_t id);
        string_t[] GetAllUserIds();
    }
}
```

### C++ Implementation

```cpp
class User : public UserSystem::IUser {
private:
    std::string id_;
    std::string username_;
    std::string email_;
    bool active_ = true;
    std::string password_hash_;
    
public:
    User(std::string id, std::string username, std::string email)
        : id_(std::move(id))
        , username_(std::move(username))
        , email_(std::move(email)) {}
    
    // Read-only properties
    std::string GetId() const override { return id_; }
    std::string GetUsername() const override { return username_; }
    
    // Writable properties
    std::string GetEmail() const override { return email_; }
    void SetEmail(const std::string& email) override { email_ = email; }
    
    bool GetActive() const override { return active_; }
    void SetActive(bool active) override { active_ = active; }
    
    // Methods
    std::string GetFullName() override {
        // Simple implementation
        return username_;
    }
    
    void UpdatePassword(const std::string& newPassword) override {
        // Hash password (simplified)
        password_hash_ = "hashed_" + newPassword;
    }
};

class UserManager : public UserSystem::IUserManager {
private:
    std::unordered_map<std::string, std::shared_ptr<User>> users_;
    int next_id_ = 1000;
    
public:
    std::shared_ptr<UserSystem::IUser> FindUserById(const std::string& id) override {
        auto it = users_.find(id);
        return (it != users_.end()) ? it->second : nullptr;
    }
    
    std::shared_ptr<UserSystem::IUser> FindUserByEmail(const std::string& email) override {
        for (const auto& [id, user] : users_) {
            if (user->GetEmail() == email) {
                return user;
            }
        }
        return nullptr;
    }
    
    std::shared_ptr<UserSystem::IUser> CreateUser(
        const std::string& username, 
        const std::string& email) override {
        
        auto id = std::to_string(next_id_++);
        auto user = std::make_shared<User>(id, username, email);
        users_[id] = user;
        return user;
    }
    
    bool DeleteUser(const std::string& id) override {
        return users_.erase(id) > 0;
    }
    
    std::vector<std::string> GetAllUserIds() override {
        std::vector<std::string> ids;
        ids.reserve(users_.size());
        for (const auto& [id, _] : users_) {
            ids.push_back(id);
        }
        return ids;
    }
};
```

### Swift Usage

```swift
let userManager = UserManager()

// Create users
let alice = userManager.createUser(username: "alice", email: "alice@example.com")
let bob = userManager.createUser(username: "bob", email: "bob@example.com")

// Find users
if let user = userManager.findUserByEmail("alice@example.com") {
    print("Found user: \(user.username)")
    user.active = false  // Deactivate
}

// List all users
let userIds = userManager.getAllUserIds()
print("Total users: \(userIds.count)")

// Delete user
if userManager.deleteUser(id: bob.id) {
    print("User deleted")
}
```

## Configuration System

Example with collections:

```idl
namespace Config {
    interface IConfiguration {
        // Dictionary property
        dict<string_t, string_t> settings writable;
        
        // Methods for individual settings
        string_t? GetSetting(string_t key);
        void SetSetting(string_t key, string_t value);
        bool HasSetting(string_t key);
        
        // Batch operations
        void LoadFromFile(string_t path);
        void SaveToFile(string_t path);
        void Clear();
    }
}
```

### Usage Examples

```cpp
// C++
auto config = std::make_shared<ConfigurationImpl>();
config->SetSetting("api_url", "https://api.example.com");
config->SetSetting("timeout", "30");

if (config->HasSetting("api_url")) {
    auto url = config->GetSetting("api_url");
    // Use URL
}

// Get all settings
auto settings = config->GetSettings();
for (const auto& [key, value] : settings) {
    std::cout << key << " = " << value << std::endl;
}
```

```swift
// Swift
let config = Configuration()
config.setSetting(key: "api_url", value: "https://api.example.com")
config.setSetting(key: "timeout", value: "30")

if let url = config.getSetting(key: "api_url") {
    // Use URL
}

// Update all settings
config.settings = [
    "api_url": "https://api.example.com",
    "timeout": "30",
    "debug": "true"
]
```

## Event System

Example with callbacks and forward declarations:

```idl
namespace Events {
    // Forward declaration
    interface IEventHandler;
    
    interface IEventEmitter {
        void Subscribe(IEventHandler handler);
        void Unsubscribe(IEventHandler handler);
        void Emit(string_t event, dict<string_t, string_t> data);
    }
    
    interface IEventHandler {
        void HandleEvent(string_t event, dict<string_t, string_t> data);
        string_t GetId();
    }
}
```

This demonstrates:
- Forward declarations for circular dependencies
- Interface parameters
- Dictionary parameters for flexible data

## Key Takeaways

1. **Start Simple**: Begin with basic interfaces and add complexity
2. **Use Properties**: More convenient than getter/setter methods
3. **Nullable Types**: Use `?` for optional returns
4. **Collections**: Arrays, dictionaries, and sets are first-class
5. **Enums**: Always specify backing type
6. **Forward Declarations**: Resolve circular dependencies