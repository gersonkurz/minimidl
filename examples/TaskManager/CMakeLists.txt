cmake_minimum_required(VERSION 3.16)
project(TaskManager VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Header files
set(HEADERS
    include/TaskManager.hpp
)

# Create interface library for headers
add_library(${PROJECT_NAME}_interface INTERFACE)
target_include_directories(${PROJECT_NAME}_interface 
    INTERFACE 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Example executable
add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE ${PROJECT_NAME}_interface)

# Enable testing
enable_testing()

# Test executable
add_executable(test_main tests/test_main.cpp)
target_link_libraries(test_main PRIVATE ${PROJECT_NAME}_interface)
add_test(NAME test_main COMMAND test_main)

# Add C wrapper if it exists
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/CWrapper/CMakeLists.txt")
    add_subdirectory(CWrapper)
endif()

# Installation rules
install(FILES ${HEADERS} DESTINATION include)
install(TARGETS ${PROJECT_NAME}_interface
    EXPORT ${PROJECT_NAME}Targets
    INCLUDES DESTINATION include
)

# Optional: Export targets for find_package support
# Uncomment the following lines if you want to install this as a library
# install(EXPORT ${PROJECT_NAME}Targets
#     FILE ${PROJECT_NAME}Targets.cmake
#     NAMESPACE ${PROJECT_NAME}::
#     DESTINATION lib/cmake/${PROJECT_NAME}
# )
