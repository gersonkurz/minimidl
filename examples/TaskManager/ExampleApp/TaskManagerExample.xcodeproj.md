# Creating Xcode Project for TaskManager Example

To create an Xcode project for this example:

1. Open Xcode
2. Create a new project (File > New > Project)
3. Choose "App" template
4. Configure:
   - Product Name: TaskManagerExample
   - Interface: SwiftUI
   - Language: Swift
5. Replace the generated ContentView.swift with the one in this directory
6. Replace the generated App file with TaskManagerApp.swift
7. Add the Swift package dependency:
   - File > Add Package Dependencies
   - Add local package from ../TaskManager
8. Build and run

Note: Ensure you've built the C libraries first using ../build_c.sh
