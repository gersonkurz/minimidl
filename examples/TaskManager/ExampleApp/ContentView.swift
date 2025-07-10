import SwiftUI
import TaskManager

struct ContentView: View {
    @State private var statusMessage = "Ready"
    
    var body: some View {
        VStack(spacing: 20) {
            Text("TaskManager Example")
                .font(.largeTitle)
                .padding()
            
            Text(statusMessage)
                .font(.body)
                .foregroundColor(.secondary)
            
            Button("Test API") {
                testAPI()
            }
            .buttonStyle(.borderedProminent)
            
            Spacer()
        }
        .padding()
    }
    
    func testAPI() {
        // TODO: Add your API test code here
        statusMessage = "API test completed"
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
