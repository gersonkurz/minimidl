# MinimIDL Language Reference

This document provides a complete reference for the MinimIDL language syntax and features.

## Basic Structure

Every MinimIDL file consists of one or more namespaces:

```idl
namespace MyAPI {
    // Type definitions go here
}
```

## Primitive Types

MinimIDL supports these primitive types:

| Type | Description | C++ Type | Swift Type |
|------|-------------|----------|------------|
| `void` | No value (methods only) | `void` | `Void` |
| `bool` | Boolean | `bool` | `Bool` |
| `int32_t` | 32-bit signed integer | `int32_t` | `Int32` |
| `int64_t` | 64-bit signed integer | `int64_t` | `Int64` |
| `float` | 32-bit floating point | `float` | `Float` |
| `double` | 64-bit floating point | `double` | `Double` |
| `string_t` | UTF-8 string | `std::string` | `String` |

## Interfaces

Interfaces define object contracts:

```idl
interface IExample {
    // Methods
    string_t GetName();
    void SetName(string_t name);
    int32_t Calculate(int32_t a, int32_t b);
    
    // Properties (read-only by default)
    int32_t count;
    string_t id;
    
    // Writable properties
    bool enabled writable;
    double threshold writable;
}
```

### Method Rules
- Methods can have zero or more parameters
- Return type can be any type including void
- Parameters are passed by value (primitives) or const reference (objects)

### Property Rules
- Properties are read-only by default
- Add `writable` keyword for read-write properties
- Properties become getter/setter methods in generated code

## Enumerations

Enums must specify a backing type:

```idl
enum Status : int32_t {
    IDLE = 0,
    RUNNING = 1,
    STOPPED = 2,
    ERROR = -1
}

enum Flags : int32_t {
    NONE = 0,
    READ = 1 << 0,      // 1
    WRITE = 1 << 1,     // 2
    EXECUTE = 1 << 2,   // 4
    ALL = 0x07          // 7
}
```

### Enum Features
- Backing type must be `int32_t` or `int64_t`
- Values can be decimal, hexadecimal (`0x`), or binary (`0b`)
- Supports bit shift expressions
- Values must be compile-time constants

## Type Definitions

Create type aliases for complex types:

```idl
typedef string_t[] StringArray;
typedef dict<string_t, string_t> StringMap;
typedef set<int32_t> IntSet;
```

## Collections

### Arrays
```idl
string_t[] GetNames();
int32_t[] values;
IUser[] GetUsers();
```

### Dictionaries
```idl
dict<string_t, string_t> GetConfig();
dict<int32_t, IUser> GetUserMap();
```

### Sets
```idl
set<string_t> GetTags();
set<int32_t> unique_ids;
```

## Nullable Types

Any type can be made nullable with `?`:

```idl
interface IContainer {
    IUser? FindUser(string_t name);
    string_t? GetOptionalValue();
    int32_t?[] GetNullableArray();  // Array of nullable ints
}
```

## Constants

Define compile-time constants:

```idl
const int32_t MAX_SIZE = 1024;
const int32_t DEFAULT_PORT = 8080;
const int32_t VERSION = (1 << 16) | 2;  // 1.2
```

### Constant Expressions
Constants support these operators:
- Arithmetic: `+`, `-`, `*`
- Bitwise: `|`, `&`, `<<`, `>>`
- Parentheses for grouping

## Forward Declarations

Declare interfaces before defining them:

```idl
namespace MyAPI {
    // Forward declarations
    interface IManager;
    interface IWorker;
    
    interface IManager {
        IWorker CreateWorker();
        void AssignWork(IWorker worker);
    }
    
    interface IWorker {
        void DoWork();
        IManager GetManager();
    }
}
```

## Comments

Single-line and multi-line comments are supported:

```idl
// Single-line comment

/*
 * Multi-line comment
 * Can span multiple lines
 */

interface IExample {
    // This comment will appear in generated code
    string_t GetName();
}
```

## Namespace Rules

1. All types must be defined within a namespace
2. Namespace names should be PascalCase
3. Types in different namespaces are isolated
4. No nested namespaces

## Naming Conventions

Recommended conventions:

| Element | Convention | Example |
|---------|------------|---------|
| Namespace | PascalCase | `MyAPI` |
| Interface | PascalCase with `I` prefix | `IUserManager` |
| Enum | PascalCase | `ErrorCode` |
| Enum Value | UPPER_SNAKE_CASE | `NOT_FOUND` |
| Method | PascalCase | `GetUserName` |
| Property | snake_case | `user_count` |
| Parameter | snake_case | `user_id` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |

## Complete Example

```idl
namespace SocialMedia {
    // Forward declarations
    interface IUser;
    interface IPost;
    
    // Enumerations
    enum UserRole : int32_t {
        GUEST = 0,
        MEMBER = 1,
        MODERATOR = 2,
        ADMIN = 3
    }
    
    enum PostStatus : int32_t {
        DRAFT = 0,
        PUBLISHED = 1,
        ARCHIVED = 2,
        DELETED = 3
    }
    
    // Type definitions
    typedef string_t[] TagList;
    typedef dict<string_t, int32_t> MetricsMap;
    
    // Constants
    const int32_t MAX_POST_LENGTH = 280;
    const int32_t API_VERSION = 1;
    
    // Interfaces
    interface IUser {
        // Properties
        string_t id;
        string_t username;
        string_t email writable;
        UserRole role writable;
        bool verified;
        
        // Methods
        string_t GetDisplayName();
        void UpdateProfile(dict<string_t, string_t> fields);
        IPost[] GetPosts(int32_t offset, int32_t limit);
        bool Follow(IUser user);
        bool Unfollow(IUser user);
        IUser[] GetFollowers();
        IUser[] GetFollowing();
    }
    
    interface IPost {
        // Properties
        string_t id;
        string_t content;
        IUser author;
        PostStatus status writable;
        TagList tags writable;
        int32_t likes;
        
        // Methods
        void Publish();
        void Archive();
        void Delete();
        bool Like(IUser user);
        bool Unlike(IUser user);
        IUser[] GetLikers();
        MetricsMap GetMetrics();
        IPost? GetParent();  // For replies
        IPost[] GetReplies();
    }
    
    interface ISocialService {
        // User management
        IUser? Authenticate(string_t username, string_t password);
        IUser CreateUser(string_t username, string_t email);
        IUser? FindUser(string_t username);
        IUser[] SearchUsers(string_t query, int32_t limit);
        
        // Post management
        IPost CreatePost(IUser author, string_t content);
        IPost? GetPost(string_t id);
        IPost[] GetTimeline(IUser user, int32_t count);
        IPost[] GetTrending(int32_t count);
        
        // Analytics
        dict<string_t, int32_t> GetSystemMetrics();
        void LogEvent(string_t event, dict<string_t, string_t> data);
    }
}
```

## Grammar Specification

For the complete formal grammar, see the [Lark grammar file](https://github.com/yourusername/minimidl/blob/main/minimidl/parser/grammar.lark) in the source code.