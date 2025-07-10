# Task Manager Example

This example demonstrates a complete task management API using MinimIDL.

## Features Demonstrated

- Multiple interfaces with relationships
- Enumerations for type-safe constants
- Properties (read-only and writable)
- Nullable return types
- Collections (arrays and dictionaries)
- Forward declarations
- Real-world API design

## Building the Example

### 1. Generate Code

```bash
# Generate C++ implementation
minimidl generate task_manager.idl --target cpp --output ./cpp

# Generate Swift implementation
minimidl generate task_manager.idl --target swift --output ./swift

# Or generate everything
minimidl generate task_manager.idl --target all --output ./generated
```

### 2. Build C++ Version

```bash
cd cpp/TaskManager
./build.sh
./build/example
```

### 3. Build Swift Version

```bash
cd swift/TaskManager
./build_c.sh
./build_swift.sh
```

## Usage Examples

### C++ Usage

```cpp
#include "taskmanager.hpp"
#include <iostream>
#include <memory>

int main() {
    // Create task manager
    auto manager = CreateTaskManager();
    
    // Create a project
    auto project = manager->CreateProject("Website Redesign");
    project->SetDescription("Redesign company website");
    
    // Add tasks
    auto task1 = project->CreateTask(
        "Design mockups", 
        "Create initial design mockups"
    );
    task1->SetPriority(TaskManager::Priority::HIGH);
    task1->SetDueDate("2024-12-31");
    
    auto task2 = project->CreateTask(
        "Implement frontend",
        "Build React components"
    );
    task2->SetPriority(TaskManager::Priority::MEDIUM);
    
    // Complete a task
    task1->Complete();
    
    // Get project statistics
    auto stats = project->GetTaskCountByStatus();
    for (const auto& [status, count] : stats) {
        std::cout << "Status " << status << ": " << count << " tasks\n";
    }
    
    // Search across all projects
    auto overdue = manager->GetOverdueTasks();
    std::cout << "Overdue tasks: " << overdue.size() << "\n";
    
    // Save state
    manager->Save("tasks.db");
    
    return 0;
}
```

### Swift Usage

```swift
import TaskManager

// Create task manager
let manager = TaskManager()

// Create a project
let project = manager.createProject(name: "iOS App")
project.description = "Build iOS task manager app"
project.active = true

// Add tasks with different priorities
let designTask = project.createTask(
    title: "Design UI",
    description: "Create app interface design"
)
designTask.priority = .high
designTask.tags = ["design", "ui", "mockup"]

let devTask = project.createTask(
    title: "Implement core features",
    description: "Build task management functionality"
)
devTask.priority = .medium
devTask.status = .inProgress

// Query tasks
let highPriorityTasks = manager.getTasksByPriority(.high)
print("High priority tasks: \(highPriorityTasks.count)")

// Get project statistics
let stats = project.getTaskCountByStatus()
for (status, count) in stats {
    print("\(status): \(count) tasks")
}

// Update settings
manager.updateSettings([
    "theme": "dark",
    "notifications": "enabled"
])

// Save data
manager.save(path: "tasks.db")
```

## Implementation Notes

### Task ID Generation
- Use UUIDs or timestamp-based IDs
- Ensure uniqueness across projects

### Date Handling
- Store dates in ISO 8601 format
- Handle timezones appropriately

### Search Implementation
- Index task titles and descriptions
- Support partial matches
- Consider using full-text search

### Persistence
- JSON for simple storage
- SQLite for larger datasets
- Consider versioning for migrations

## Extending the Example

1. **Add User Management**
   - User authentication
   - Task assignment
   - Permissions

2. **Add Comments**
   - Comment interface
   - Threaded discussions
   - Attachments

3. **Add Notifications**
   - Due date reminders
   - Status change alerts
   - Email integration

4. **Add Reports**
   - Burndown charts
   - Productivity metrics
   - Time tracking

## Testing

The generated test files provide a starting point. Extend them with:

- Unit tests for each interface
- Integration tests for workflows
- Performance tests for large datasets
- Edge case handling

## Performance Considerations

- Lazy load tasks when possible
- Cache frequently accessed data
- Use pagination for large lists
- Index search fields

## Error Handling

- Validate input data
- Handle missing projects/tasks gracefully
- Provide meaningful error messages
- Log errors for debugging