# Quick Start Guide

This guide will walk you through creating your first MinimIDL interface definition and generating code for C++ and Swift.

## 1. Create Your First IDL File

Create a file named `calculator.idl`:

```idl
namespace Calculator {
    enum Operation : int32_t {
        ADD = 0,
        SUBTRACT = 1,
        MULTIPLY = 2,
        DIVIDE = 3
    }
    
    interface ICalculator {
        // Perform a calculation
        double Calculate(double a, double b, Operation op);
        
        // Get last result
        double GetLastResult();
        
        // Clear calculator state
        void Clear();
        
        // Properties
        string_t name;
        bool scientific_mode writable;
    }
}
```

## 2. Generate C++ Code

```bash
python -m minimidl generate calculator.idl --target cpp --output ./cpp_calculator
```

This creates a complete C++ project:

```
cpp_calculator/Calculator/
├── CMakeLists.txt
├── README.md
├── build.sh
├── include/
│   └── calculator.hpp
├── src/
│   └── example.cpp
└── tests/
    └── test_main.cpp
```

### Build the C++ Project

```bash
cd cpp_calculator/Calculator
./build.sh
```

The generated header provides clean C++ interfaces:

```cpp
#include "calculator.hpp"
#include <memory>

// Implement the interface
class CalculatorImpl : public Calculator::ICalculator {
    double last_result_ = 0.0;
    
public:
    double Calculate(double a, double b, Calculator::Operation op) override {
        switch (op) {
            case Calculator::Operation::ADD:
                last_result_ = a + b;
                break;
            // ... other operations
        }
        return last_result_;
    }
    
    double GetLastResult() const override {
        return last_result_;
    }
    
    void Clear() override {
        last_result_ = 0.0;
    }
};

// Use it
auto calc = std::make_shared<CalculatorImpl>();
double result = calc->Calculate(10, 5, Calculator::Operation::ADD);
```

## 3. Generate Swift Code

```bash
python -m minimidl generate calculator.idl --target swift --output ./swift_calculator
```

This creates a Swift package with C interop:

```
swift_calculator/Calculator/
├── Calculator/          # Swift package
├── CWrapper/           # C wrapper
├── CImplementation/    # C++ implementation stubs
├── ExampleApp/         # iOS/macOS example
├── build_c.sh
├── build_swift.sh
└── README.md
```

### Build and Use

```bash
cd swift_calculator/Calculator
./build_c.sh      # Build C libraries
./build_swift.sh  # Build Swift package
```

Use in Swift:

```swift
import Calculator

let calc = Calculator()
let result = calc.calculate(a: 10, b: 5, op: .add)
print("Result: \(result)")

calc.scientificMode = true
print("Mode: \(calc.scientificMode)")
```

## 4. Generate Everything at Once

```bash
python -m minimidl generate calculator.idl --target all --output ./calculator_sdk
```

This generates:
- C++ project
- C wrapper library
- Swift package
- All in one organized structure

## 5. Working with Complex Types

MinimIDL supports rich type definitions:

```idl
namespace DataProcessor {
    interface IProcessor {
        // Collections
        string_t[] GetTags();
        dict<string_t, double> GetMetrics();
        set<int32_t> GetUniqueIds();
        
        // Nullable types
        string_t? FindValue(string_t key);
        
        // Interface references
        IFilter? GetFilter();
        void SetFilter(IFilter? filter);
    }
    
    interface IFilter {
        bool Matches(string_t input);
        string_t pattern writable;
    }
}
```

## 6. Using AST Caching

For large projects, cache the parsed AST:

```bash
# Parse once and cache
python -m minimidl generate api.idl --cache-ast --target cpp

# Reuse cached AST
python -m minimidl generate --from-ast api.ast --target swift
```

## 7. Validation

Validate your IDL without generating code:

```bash
minimidl validate calculator.idl
```

## Next Steps

- Read the [Language Reference](language-reference.md) for complete syntax
- See [C++ Integration Guide](cpp-integration.md) for advanced C++ usage
- See [Swift Integration Guide](swift-integration.md) for iOS/macOS apps
- Browse [Examples](examples/basic.md) for more patterns

## Tips

1. **Start Simple** - Begin with basic interfaces and add complexity gradually
2. **Use Forward Declarations** - For circular dependencies
3. **Namespace Everything** - Avoid naming conflicts
4. **Document Your IDL** - Comments are preserved in generated code
5. **Version Your API** - Use constants for version numbers