# Generated by MinimIDL - CMake Build Configuration
# DO NOT EDIT - This file was automatically generated

cmake_minimum_required(VERSION 3.15)
project(TaskManager_wrapper VERSION 1.0.0 LANGUAGES CXX C)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Export compile commands for IDEs
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Position independent code
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Library source files
set(WRAPPER_SOURCES
    taskmanager_wrapper.cpp
    taskmanager_wrapper.h
)

# Create shared library
add_library(taskmanager_wrapper SHARED ${WRAPPER_SOURCES})

# Set export macro
target_compile_definitions(taskmanager_wrapper PRIVATE TASKMANAGER_EXPORTS)

# Include directories
target_include_directories(taskmanager_wrapper
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<INSTALL_INTERFACE:include>
)

# Platform-specific settings
if(WIN32)
    # Use .def file for exports on Windows
    set_target_properties(taskmanager_wrapper PROPERTIES
        WINDOWS_EXPORT_ALL_SYMBOLS OFF
    )
    target_sources(taskmanager_wrapper PRIVATE taskmanager_exports.def)
else()
    # Use visibility attributes on Unix-like systems
    target_compile_options(taskmanager_wrapper PRIVATE -fvisibility=hidden)
endif()

# Compiler warnings
if(MSVC)
    target_compile_options(taskmanager_wrapper PRIVATE /W4 /WX)
else()
    target_compile_options(taskmanager_wrapper PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# Test executable
add_executable(taskmanager_test taskmanager_test.c)
target_link_libraries(taskmanager_test PRIVATE taskmanager_wrapper)

# Installation rules
include(GNUInstallDirs)

install(TARGETS taskmanager_wrapper
    EXPORT TaskManagerTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(FILES taskmanager_wrapper.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Package configuration
install(EXPORT TaskManagerTargets
    FILE TaskManagerTargets.cmake
    NAMESPACE TaskManager::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/TaskManager
)

# Optional: Export for find_package support
# To enable package export, create a Config.cmake.in file and uncomment below:
# include(CMakePackageConfigHelpers)
# configure_package_config_file(...)

# Enable testing
enable_testing()
add_test(NAME taskmanager_test COMMAND taskmanager_test)