# Changelog

All notable changes to MinimIDL will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of MinimIDL
- Lark-based parser for IDL syntax
- Pydantic v2 AST nodes with validation
- C++ code generator with modern C++17 features
- C wrapper generator for C++ interfaces
- Swift binding generator with SPM support
- CLI with Typer and rich terminal output
- Workflow system for complete project generation
- Comprehensive test suite with pytest
- MkDocs documentation with examples
- Support for:
  - Namespaces
  - Interfaces with methods and properties
  - Enumerations with explicit backing types
  - Type aliases (typedef)
  - Constants
  - Forward declarations
  - Nullable types
  - Collections (arrays, dictionaries, sets)
  - Read-only and writable properties

### Features
- **Parser**: Complete IDL grammar with expression support
- **Validators**: Semantic validation with type checking
- **C++ Generator**: Modern C++ with smart pointers and move semantics
- **C Wrapper**: Handle-based API with thread-safe error handling
- **Swift Generator**: Native Swift bindings with ARC integration
- **CLI**: Interactive and scriptable interface
- **Workflows**: Generate complete projects with build systems
- **Caching**: AST caching for improved performance
- **Documentation**: Comprehensive guides and API reference

## [0.1.0] - TBD

Initial beta release.