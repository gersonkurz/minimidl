#pragma once
// MinimIDL Runtime Support Library
// This header provides base classes and utilities for generated code

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <atomic>

namespace minimidl {

// Base class for reference counted objects
class RefCounted {
protected:
    mutable std::atomic<int32_t> m_refCount{1};
    
public:
    virtual ~RefCounted() = default;
    
    void AddRef() const {
        m_refCount.fetch_add(1, std::memory_order_relaxed);
    }
    
    void Release() const {
        if (m_refCount.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete this;
        }
    }
};

// String type for IDL compatibility
using string_t = std::string;

// Array type template
template<typename T>
using array_t = std::vector<T>;

// Dictionary type template
template<typename K, typename V>
using dict_t = std::unordered_map<K, V>;

} // namespace minimidl
