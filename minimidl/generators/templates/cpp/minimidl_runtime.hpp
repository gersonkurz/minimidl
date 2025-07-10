// MinimIDL Runtime Support Library
// Provides helper types and utilities for generated code
#pragma once

#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include <stdexcept>
#include <type_traits>

namespace minimidl {

// Exception types
class idl_exception : public std::runtime_error {
public:
    explicit idl_exception(const std::string& msg) : std::runtime_error(msg) {}
};

class null_pointer_exception : public idl_exception {
public:
    explicit null_pointer_exception(const std::string& msg) 
        : idl_exception("Null pointer access: " + msg) {}
};

// Smart pointer helpers
template<typename T>
using object_ptr = std::shared_ptr<T>;

template<typename T>
using weak_ptr = std::weak_ptr<T>;

// Factory function for creating objects
template<typename T, typename... Args>
object_ptr<T> make_object(Args&&... args) {
    return std::make_shared<T>(std::forward<Args>(args)...);
}

// Safe nullable access
template<typename T>
T& deref(const object_ptr<T>& ptr, const char* context = "") {
    if (!ptr) {
        throw null_pointer_exception(context);
    }
    return *ptr;
}

// Type traits for IDL types
template<typename T>
struct is_idl_primitive : std::false_type {};

template<> struct is_idl_primitive<bool> : std::true_type {};
template<> struct is_idl_primitive<int32_t> : std::true_type {};
template<> struct is_idl_primitive<int64_t> : std::true_type {};
template<> struct is_idl_primitive<float> : std::true_type {};
template<> struct is_idl_primitive<double> : std::true_type {};

template<typename T>
constexpr bool is_idl_primitive_v = is_idl_primitive<T>::value;

// String utilities
using string_t = std::string;

// Collection type aliases for clarity
template<typename T>
using array = std::vector<T>;

template<typename K, typename V>
using dict = std::unordered_map<K, V>;

template<typename T>
using set = std::unordered_set<T>;

// Optional support for nullable primitives
template<typename T>
using nullable = std::optional<T>;

// Enum utilities
template<typename E>
constexpr auto to_underlying(E e) noexcept {
    return static_cast<std::underlying_type_t<E>>(e);
}

// Interface casting utilities
template<typename To, typename From>
object_ptr<To> interface_cast(const object_ptr<From>& from) {
    return std::dynamic_pointer_cast<To>(from);
}

template<typename To, typename From>
object_ptr<To> interface_cast_required(const object_ptr<From>& from, 
                                      const char* context = "") {
    auto result = interface_cast<To>(from);
    if (!result && from) {
        throw idl_exception(std::string("Invalid cast: ") + context);
    }
    return result;
}

} // namespace minimidl

// Convenience aliases in global namespace (optional)
namespace idl = minimidl;