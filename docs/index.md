# MinimIDL

**Modern Interface Definition Language for C++ and Swift**

MinimIDL is a clean, modern Interface Definition Language (IDL) compiler that generates C++ interfaces, C wrappers, and Swift bindings without the complexity of traditional IDL tools like Microsoft's MIDL.

## Features

- 🚀 **Clean Syntax** - Modern, readable IDL syntax without legacy baggage
- 🔧 **Zero Dependencies** - Generated code has no runtime dependencies
- 🌉 **Cross-Language** - Seamless interop between C++ and Swift
- 📦 **Complete Projects** - Generates buildable projects, not just headers
- 🎯 **Type Safety** - Strong typing with comprehensive validation
- ⚡ **Fast** - Efficient parser and code generation
- 🛠️ **Extensible** - Template-based generation for customization

## Why MinimIDL?

Traditional IDL tools carry decades of legacy complexity. MinimIDL provides:

- **No COM/OLE baggage** - Just clean interfaces
- **Modern C++17** - Smart pointers, move semantics, constexpr
- **Native Swift** - First-class Swift support with proper optionals
- **Simple workflow** - One command generates everything

## Quick Example

```idl
namespace Example {
    enum Status : int32_t {
        OK = 0,
        ERROR = 1
    }
    
    interface IService {
        string_t GetName();
        Status Process(string_t input);
        void SetConfig(dict<string_t, string_t> options);
    }
}
```

Generate code with one command:

```bash
minimidl generate example.idl --target all --output ./generated
```

This creates:
- Complete C++ project with CMake
- C wrapper library
- Swift package with example app
- Build scripts and documentation

## Installation

```bash
pip install minimidl
```

Or with UV:

```bash
uv pip install minimidl
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
- [Language Reference](language-reference.md) - Complete IDL syntax guide
- [Examples](examples/basic.md) - Learn by example

## Design Philosophy

MinimIDL follows these principles:

1. **Simplicity First** - If it's not needed, it's not included
2. **Zero Cost** - No runtime overhead in generated code
3. **Developer Experience** - Clear errors, helpful documentation
4. **Production Ready** - Generated code is clean, documented, and tested

## License

MinimIDL is open source under the MIT license.