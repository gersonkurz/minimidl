# Swift Integration Guide

This guide covers using MinimIDL-generated Swift code in iOS, macOS, and other Apple platform applications.

## Overview

MinimIDL generates Swift packages that:
- Wrap C++ implementations with safe Swift APIs
- Handle memory management automatically with ARC
- Provide native Swift types and optionals
- Support Swift Package Manager

## Generated Package Structure

```
YourAPI/
├── Package.swift           # Swift Package Manager manifest
├── Sources/
│   ├── YourAPI/           # Swift wrapper code
│   │   ├── YourAPI.swift  # Main wrapper classes
│   │   └── Types.swift    # Enums and type definitions
│   └── YourAPIC/          # C module
│       └── module.modulemap
├── Tests/
│   └── YourAPITests/
└── README.md
```

## Basic Usage

### Adding to Your Project

#### Swift Package Manager

Add to your `Package.swift`:

```swift
dependencies: [
    .package(path: "../path/to/YourAPI")
]
```

#### Xcode Project

1. File → Add Package Dependencies
2. Add local package from the generated directory
3. Import in your Swift files:

```swift
import YourAPI
```

### Creating Instances

```swift
// Create an instance
let service = Service()

// Use properties
print("Name: \(service.name)")
service.enabled = true

// Call methods
let result = service.calculate(a: 10, b: 20)
```

## Memory Management

### Automatic Reference Counting

The generated Swift wrappers handle memory management automatically:

```swift
class UserManager {
    private let api: API
    
    init() {
        // Automatically managed by ARC
        self.api = API()
    }
    
    func getUser(id: String) -> User? {
        // Returned objects are also managed
        return api.findUser(id: id)
    }
}
// api is automatically released when UserManager is deallocated
```

### Ownership

```swift
// Objects can be shared
let service1 = Service()
let service2 = service1  // Both reference the same object

// Weak references for cycles
class Controller {
    weak var delegate: ServiceDelegate?
}
```

## Working with Types

### Enumerations

```swift
// Using enums
let status = Status.running
service.setStatus(status)

switch service.getStatus() {
case .idle:
    print("Idle")
case .running:
    print("Running")
case .error:
    print("Error occurred")
}

// Converting to/from raw values
let rawValue = Status.running.rawValue  // Int32
let status = Status(rawValue: 1)        // Status?
```

### Collections

#### Arrays

```swift
// Getting arrays
let names = service.getNames()
for name in names {
    print(name)
}

// Setting arrays
service.tags = ["swift", "ios", "minimidl"]

// Array properties
let count = service.values.count
let first = service.values.first
```

#### Dictionaries

```swift
// Getting dictionaries
let config = service.getConfig()
if let value = config["key"] {
    print("Value: \(value)")
}

// Setting dictionaries
service.metadata = [
    "version": "1.0",
    "author": "minimidl"
]

// Iterating
for (key, value) in service.settings {
    print("\(key): \(value)")
}
```

#### Sets

```swift
// Working with sets
let uniqueTags = service.getTags()
if uniqueTags.contains("important") {
    // Handle important tag
}

// Set operations
let combined = tags1.union(tags2)
let common = tags1.intersection(tags2)
```

### Optional Types

```swift
// Nullable returns
if let user = userManager.findUser(id: "123") {
    print("Found: \(user.name)")
} else {
    print("User not found")
}

// Optional chaining
let email = userManager.currentUser?.email

// Nil coalescing
let name = service.getName() ?? "Unknown"

// Guard statements
guard let config = service.getConfig() else {
    print("No configuration")
    return
}
// Use config safely here
```

## Properties

### Read-Only Properties

```swift
// Accessing read-only properties
let id = user.id
let count = service.itemCount

// Cannot assign to read-only
// user.id = "new" // ❌ Compiler error
```

### Writable Properties

```swift
// Get and set writable properties
service.threshold = 0.95
let current = service.threshold

// Property observers in your code
class Monitor {
    var service: Service {
        didSet {
            print("Service changed")
        }
    }
}
```

## Error Handling

### Using Error Information

```swift
// Check for errors after operations
service.performOperation()
if let error = getLastError() {
    print("Operation failed: \(error)")
    clearError()
}

// Wrapper pattern for throwing
extension Service {
    func performOperationThrowing() throws {
        performOperation()
        if let error = getLastError() {
            clearError()
            throw ServiceError.operationFailed(error)
        }
    }
}
```

### Swift Error Types

```swift
enum ServiceError: Error {
    case notFound
    case invalidInput(String)
    case operationFailed(String)
}

// Using with throws
func processUser(id: String) throws -> User {
    guard let user = userManager.findUser(id: id) else {
        throw ServiceError.notFound
    }
    return user
}
```

## Async/Await Integration

### Wrapping for Async

```swift
extension Service {
    func calculateAsync(a: Double, b: Double) async -> Double {
        await withCheckedContinuation { continuation in
            DispatchQueue.global().async {
                let result = self.calculate(a: a, b: b)
                continuation.resume(returning: result)
            }
        }
    }
}

// Usage
Task {
    let result = await service.calculateAsync(a: 10, b: 20)
    print("Result: \(result)")
}
```

### Combine Integration

```swift
import Combine

extension Service {
    func valuesPublisher() -> AnyPublisher<[Int32], Never> {
        CurrentValueSubject(values)
            .eraseToAnyPublisher()
    }
    
    func performOperationPublisher() -> Future<Void, Error> {
        Future { promise in
            self.performOperation()
            if let error = getLastError() {
                promise(.failure(ServiceError.operationFailed(error)))
            } else {
                promise(.success(()))
            }
        }
    }
}
```

## SwiftUI Integration

### Observable Objects

```swift
import SwiftUI

class ServiceViewModel: ObservableObject {
    @Published var isRunning = false
    @Published var status = Status.idle
    @Published var items: [String] = []
    
    private let service = Service()
    
    func start() {
        service.start()
        isRunning = service.isRunning
        status = service.status
    }
    
    func refresh() {
        items = service.getItems()
    }
}
```

### SwiftUI Views

```swift
struct ServiceView: View {
    @StateObject private var viewModel = ServiceViewModel()
    
    var body: some View {
        VStack {
            Text("Status: \(viewModel.status)")
            
            Toggle("Running", isOn: $viewModel.isRunning)
                .onChange(of: viewModel.isRunning) { newValue in
                    if newValue {
                        viewModel.start()
                    } else {
                        viewModel.stop()
                    }
                }
            
            List(viewModel.items, id: \.self) { item in
                Text(item)
            }
        }
        .onAppear {
            viewModel.refresh()
        }
    }
}
```

## UIKit Integration

### View Controllers

```swift
class ServiceViewController: UIViewController {
    private let service = Service()
    private var items: [String] = []
    
    @IBOutlet weak var tableView: UITableView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        loadData()
    }
    
    private func loadData() {
        items = service.getItems()
        tableView.reloadData()
    }
}

extension ServiceViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return items.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.text = items[indexPath.row]
        return cell
    }
}
```

## Testing

### Unit Tests

```swift
import XCTest
@testable import YourAPI

class ServiceTests: XCTestCase {
    var service: Service!
    
    override func setUp() {
        super.setUp()
        service = Service()
    }
    
    override func tearDown() {
        service = nil
        super.tearDown()
    }
    
    func testCalculation() {
        let result = service.calculate(a: 10, b: 5, operation: .add)
        XCTAssertEqual(result, 15)
    }
    
    func testProperties() {
        service.threshold = 0.5
        XCTAssertEqual(service.threshold, 0.5, accuracy: 0.001)
    }
    
    func testOptionalReturn() {
        let user = service.findUser(id: "test")
        XCTAssertNil(user)
    }
}
```

### Integration Tests

```swift
class IntegrationTests: XCTestCase {
    func testCompleteWorkflow() async throws {
        let service = Service()
        
        // Setup
        service.configure(options: ["mode": "test"])
        
        // Execute
        service.start()
        XCTAssertTrue(service.isRunning)
        
        // Wait for async operation
        try await Task.sleep(nanoseconds: 1_000_000_000)
        
        // Verify
        let results = service.getResults()
        XCTAssertFalse(results.isEmpty)
        
        // Cleanup
        service.stop()
    }
}
```

## Performance Tips

### Efficient Collection Usage

```swift
// Avoid repeated calls
let items = service.getItems()  // Call once
for item in items {
    // Process
}

// Use lazy when appropriate
let filtered = service.getLargeDataSet()
    .lazy
    .filter { $0.isValid }
    .map { $0.processed }
```

### Caching

```swift
class CachedService {
    private let service = Service()
    private var cache: [String: User] = [:]
    
    func getUser(id: String) -> User? {
        if let cached = cache[id] {
            return cached
        }
        
        if let user = service.findUser(id: id) {
            cache[id] = user
            return user
        }
        
        return nil
    }
}
```

## Best Practices

1. **Use Swift Naming**: Follow Swift conventions in your extensions
2. **Handle Optionals**: Use guard, if-let, and nil-coalescing appropriately  
3. **Avoid Force Unwrapping**: Never use `!` with MinimIDL optionals
4. **Create Convenience Extensions**: Add Swift-friendly APIs
5. **Document Your Code**: Add documentation comments
6. **Test Thoroughly**: Test both success and failure cases
7. **Use Proper Access Control**: Mark implementation details as private

## Common Issues

### Build Errors

```bash
# Ensure C libraries are built first
cd YourAPI
./build_c.sh
./build_swift.sh
```

### Module Not Found

```swift
// Check module.modulemap exists and is correct
// Verify C headers are in the right location
// Clean build folder and rebuild
```

### Memory Issues

```swift
// Avoid retain cycles
class Manager {
    weak var delegate: ManagerDelegate?
}

// Use weak self in closures
service.performAsync { [weak self] result in
    self?.handleResult(result)
}
```