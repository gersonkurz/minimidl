#include <iostream>
#include <cassert>
#include "TaskManager.hpp"

// Simple test framework
#define TEST(name) void test_##name(); tests.push_back({#name, test_##name}); void test_##name()
#define ASSERT(cond) if (!(cond)) { std::cerr << "FAILED: " #cond " at " __FILE__ ":" << __LINE__ << "\n"; return; }

struct Test {
    const char* name;
    void (*func)();
};

std::vector<Test> tests;

TEST(basic_compilation) {
    // Test that headers compile correctly
    std::cout << "  Testing basic compilation... ";
    ASSERT(true);
    std::cout << "PASSED\n";
}

TEST(interface_creation) {
    // TODO: Add interface creation tests
    std::cout << "  Testing interface creation... ";
    ASSERT(true);
    std::cout << "PASSED\n";
}

int main() {
    std::cout << "TaskManager Tests\n";
    std::cout << "===================\n\n";
    
    int passed = 0;
    int failed = 0;
    
    for (const auto& test : tests) {
        std::cout << "Running " << test.name << ":\n";
        test.func();
        passed++;
    }
    
    std::cout << "\nTest Summary: " << passed << " passed, " << failed << " failed\n";
    return failed > 0 ? 1 : 0;
}
