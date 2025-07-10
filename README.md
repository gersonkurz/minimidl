# MinimIDL: Modern Interface Definition Language

> *"Bringing back the good parts of IDL without the Microsoft baggage"*

## The Problem

If you've ever tried to integrate a C++ library with Swift on macOS, you know the pain. Swift can't directly talk to C++ - it needs a C bridge. This means:

- **Manual C wrapper creation** - tedious, error-prone, and hard to maintain
- **Memory management nightmares** - who owns what string? When does it get freed?
- **Type system mismatches** - C++ exceptions vs Swift optionals vs C return codes
- **Boilerplate explosion** - every interface change requires updates in three places

Meanwhile, decades ago, Microsoft's IDL (Interface Definition Language) solved similar problems for COM/ActiveX. The core idea was brilliant: define interfaces once, generate implementation stubs and bindings automatically. But IDL got buried under layers of Windows-specific cruft, GUIDs, registry magic, and COM complexity.

## The Solution

**MinimIDL** resurrects the good parts of IDL while discarding the Microsoft baggage. It's a modern, clean interface definition language that generates:

- **C++ abstract interfaces** - clean, header-only definitions
- **C wrapper libraries** - memory-safe bridges with proper lifetime management  
- **Swift native bindings** - first-class Swift APIs with optionals, arrays, and ARC integration

All from a single, simple interface definition.

## The Big Picture

We're not just solving the C++/Swift integration problem - we're creating a **zero-cost abstraction layer** that could work for any language combination. Today it's C++ → Swift, tomorrow it could be C++ → Rust, C++ → Go, or C++ → Python.

Think of it as a "universal translator" for programming languages, but one that generates static code rather than adding runtime overhead.

## Why This Matters

### For C++ Developers
- **Write once, use everywhere** - define your API once, get Swift bindings for free
- **No more manual wrapper maintenance** - change the IDL, regenerate everything
- **Professional output** - generated code looks like it was written by a senior developer
- **Cross-platform by design** - works on macOS, Windows, and Linux

### For Swift Developers  
- **Native Swift experience** - no C interop visible in your code
- **Type safety** - optionals, arrays, and proper error handling
- **ARC integration** - memory management "just works"
- **Swift Package Manager ready** - drop-in integration with your existing projects

### For Teams
- **Single source of truth** - the IDL file is the interface contract
- **Reduced bugs** - no manual synchronization between C++ and Swift code
- **Faster iteration** - add a method to the IDL, rebuild, done
- **Better documentation** - interfaces are self-documenting

## The Technical Vision

### What We're Building
MinimIDL is a **compiler** that transforms clean interface definitions into working code:

```idl
// This single definition...
namespace PaymentAPI {
    interface IPaymentProcessor {
        bool ProcessPayment(string_t cardNumber, double amount);
        string_t[] GetSupportedCurrencies();
        PaymentResult? GetLastResult();
    }
}
```

Becomes:
- **C++ abstract interface** with proper memory management
- **C wrapper library** with cross-platform exports
- **Swift native class** with optionals and arrays
- **Complete build system** (CMake + Swift Package Manager)
- **Test harness** to verify everything works

### Why Not Just Use Existing Tools?

**SWIG?** Generates ugly code, complex configuration, poor Swift integration.

**Objective-C++ bridges?** Ties you to Apple's ecosystem, doesn't solve the fundamental problem.

**Manual C wrappers?** Doesn't scale, maintenance nightmare, error-prone.

**Protocol Buffers/gRPC?** Overkill for in-process communication, runtime overhead.

We wanted something that:
- Generates **beautiful, readable code**
- Has **zero runtime overhead**
- Supports **modern language features** (optionals, generics, etc.)
- Provides **complete project scaffolding**
- Maintains **professional code quality**

## The Philosophy

### "Zero-Cost Abstraction"
Like C++ templates or Rust's trait system, MinimIDL adds no runtime overhead. It's a compile-time tool that generates efficient, direct code.

### "Batteries Included"
Running `minimidl myapi.idl` doesn't just generate interface files - it creates complete, buildable projects with tests, documentation, and proper build systems.

### "Convention Over Configuration"
We make the common case simple and the complex case possible. Sensible defaults, but extensible when needed.

### "Developer Experience First"
Every decision prioritizes the developer experience. Clear error messages, intuitive syntax, professional output, comprehensive documentation.

## Real-World Impact

Imagine you're building a cross-platform application with:
- **C++ core logic** (algorithms, data processing, business logic)
- **Swift UI layer** (native macOS/iOS interface)
- **Potentially other platforms** (Android, Windows, Web)

Today, each platform integration is a custom, manual effort. With MinimIDL:

1. **Define your API once** in clean IDL syntax
2. **Generate platform bindings** with a single command
3. **Focus on your actual product** instead of integration plumbing

This isn't just about C++ and Swift - it's about **breaking down the language barriers** that fragment our industry.

## The Broader Vision

Programming languages are tools, not religions. The best applications often combine multiple languages:
- **C++ for performance-critical code**
- **Swift for native Apple experiences**  
- **Rust for systems programming**
- **Python for data science**
- **JavaScript for web frontends**

But language integration is still painful. MinimIDL represents a step toward a world where:
- **Language choice is based on strengths, not integration difficulty**
- **APIs are defined once and work everywhere**
- **Cross-language development is as smooth as single-language development**

## Why Now?

The timing is perfect:
- **Modern build systems** (CMake, Swift Package Manager, Cargo, etc.) make cross-language builds feasible
- **Type systems have converged** - most modern languages have optionals, generics, and similar concepts
- **Developer expectations have risen** - we expect tooling to "just work"
- **Cross-platform development is mainstream** - every serious project targets multiple platforms

## Getting Started

```bash
# Install minimidl
pip install minimidl

# Define your API
cat > myapi.idl << EOF
namespace MyAPI {
    interface ICalculator {
        double Add(double a, double b);
        double[] GetHistory();
    }
}
EOF

# Generate Swift bindings
minimidl --target swift myapi.idl

# Build and use
cd swift_output
swift build
```

That's it. You now have a complete Swift package that can talk to your C++ code.

## Getting Started with the Documentation

MinimIDL includes comprehensive documentation built with MkDocs. To view the documentation locally:

```bash
# Install documentation dependencies
uv pip install -e ".[docs]"

# Serve the documentation locally
just docs-serve

# Open your browser to http://localhost:8000
```

The documentation includes:
- Complete IDL language reference
- C++ integration guide
- Swift integration guide
- API reference
- Examples and tutorials
- Troubleshooting guide

To build the documentation without serving:
```bash
just docs
```

The built documentation will be in the `site/` directory.

## Contributing

This project represents a significant undertaking - we're essentially building a compiler with multiple code generation backends. We welcome contributions in:

- **Language design** - improving the IDL syntax
- **Code generation** - better templates, more target languages
- **Developer experience** - better error messages, documentation, examples
- **Platform support** - Windows, Linux, mobile platforms

## The Future

MinimIDL starts with C++/Swift integration, but the architecture supports any source/target language combination. Future possibilities:

- **C++ → Rust** bindings for systems programming
- **C++ → Python** bindings for data science
- **C++ → JavaScript** bindings for web applications
- **Rust → Swift** bindings for next-generation apps
- **Language-agnostic protocol definitions** for network services

We're not just building a tool - we're building the foundation for a more integrated, multilingual programming future.

---

*MinimIDL: Because great software shouldn't be limited by language boundaries.*