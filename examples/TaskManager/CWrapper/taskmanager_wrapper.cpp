// Generated by MinimIDL - C Wrapper Implementation
// DO NOT EDIT - This file was automatically generated

#include "taskmanager_wrapper.h"
#include "TaskManager.hpp"
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <cstring>
#include <thread>
#include <atomic>

// Core interfaces
class IRefCounted {
public:
    virtual ~IRefCounted() = default;
    virtual void AddRef() = 0;
    virtual void Release() = 0;
};

class IDynamicString : public IRefCounted {
public:
    virtual const char* GetValue() const = 0;
    virtual void SetValue(const char* value) = 0;
    virtual size_t GetLength() const = 0;
};

// Reference counting template
template <typename T>
class RefCounted : public T {
public:
    RefCounted() : m_refCount{1} {}
    
    void AddRef() override final {
        ++m_refCount;
    }
    
    void Release() override final {
        if (--m_refCount == 0) {
            delete this;
        }
    }

private:
    mutable std::atomic<int32_t> m_refCount;
};

// Concrete string implementation
class DynamicString : public RefCounted<IDynamicString> {
private:
    std::string m_value;
    
public:
    explicit DynamicString(const char* value = nullptr) {
        if (value) {
            m_value = value;
        }
    }
    
    const char* GetValue() const override { 
        return m_value.c_str(); 
    }
    
    void SetValue(const char* value) override { 
        m_value = value ? value : ""; 
    }
    
    size_t GetLength() const override { 
        return m_value.length(); 
    }
};

// Factory function
IDynamicString* CreateDynamicString(const char* value = nullptr) {
    return new DynamicString(value);
}

namespace {
    thread_local std::string g_lastError;
    
    void SetError(const char* error) {
        g_lastError = error ? error : "";
    }
    
    template<typename T>
    T* HandleToPtr(void* handle) {
        return static_cast<T*>(handle);
    }
    
    template<typename T>
    void* PtrToHandle(T* ptr) {
        return static_cast<void*>(ptr);
    }
}

// Error handling implementation
extern "C" {

const char* TaskManager_GetLastError() {
    return g_lastError.c_str();
}

void TaskManager_ClearError() {
    g_lastError.clear();
}

// IDynamicString C API implementation
IDynamicString_Handle IDynamicString_Create(const char* value) {
    try {
        return PtrToHandle(CreateDynamicString(value));
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void IDynamicString_AddRef(IDynamicString_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* str = HandleToPtr<IDynamicString>(handle);
        str->AddRef();
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

void IDynamicString_Release(IDynamicString_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* str = HandleToPtr<IDynamicString>(handle);
        str->Release();
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

const char* IDynamicString_GetValue(IDynamicString_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return "";
    }
    try {
        auto* str = HandleToPtr<IDynamicString>(handle);
        return str->GetValue();
    } catch (const std::exception& e) {
        SetError(e.what());
        return "";
    }
}

size_t IDynamicString_GetLength(IDynamicString_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return 0;
    }
    try {
        auto* str = HandleToPtr<IDynamicString>(handle);
        return str->GetLength();
    } catch (const std::exception& e) {
        SetError(e.what());
        return 0;
    }
}

void IDynamicString_SetValue(IDynamicString_Handle handle, const char* value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* str = HandleToPtr<IDynamicString>(handle);
        str->SetValue(value);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// ITask implementation

ITask_Handle ITask_Create() {
    try {
        // Note: This assumes the C++ implementation has a concrete class
        // In practice, you'd need a factory or concrete implementation
        SetError("ITask_Create not implemented - interface requires concrete implementation");
        return nullptr;
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void ITask_Release(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        delete obj;
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

void ITask_AddRef(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    // Note: This would need proper reference counting implementation
    // For now, this is a no-op placeholder
}

// Property: id
IDynamicString_Handle ITask_Getid(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        std::string result = obj->get_id();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}


// Property: title
IDynamicString_Handle ITask_Gettitle(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        std::string result = obj->get_title();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}


// Property: created_at
IDynamicString_Handle ITask_Getcreated_at(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        std::string result = obj->get_created_at();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}


// Property: description
IDynamicString_Handle ITask_Getdescription(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        std::string result = obj->get_description();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void ITask_Setdescription(ITask_Handle handle, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    if (!value) {
        SetError("Null value");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        auto* str = HandleToPtr<IDynamicString>(value);
        obj->set_description(str->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: priority
Priority ITask_Getpriority(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        return static_cast<Priority>(obj->get_priority());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

void ITask_Setpriority(ITask_Handle handle, Priority value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->set_priority(static_cast<TaskManager::Priority>(value));
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: status
Status ITask_Getstatus(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        return static_cast<Status>(obj->get_status());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

void ITask_Setstatus(ITask_Handle handle, Status value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->set_status(static_cast<TaskManager::Status>(value));
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: due_date
IDynamicString_Handle ITask_Getdue_date(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        std::string result = obj->get_due_date();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void ITask_Setdue_date(ITask_Handle handle, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    if (!value) {
        SetError("Null value");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        auto* str = HandleToPtr<IDynamicString>(value);
        obj->set_due_date(str->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: tags
size_t ITask_Gettags_Count(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return 0;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        return obj->get_tags().size();
    } catch (const std::exception& e) {
        SetError(e.what());
        return 0;
    }
}

IDynamicString_Handle ITask_Gettags_Item(ITask_Handle handle, size_t index) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        const auto& array = obj->get_tags();
        if (index >= array.size()) {
            SetError("Index out of bounds");
            return {};
        }
        std::string str = array[index];
        IDynamicString* dynStr = CreateDynamicString(str.c_str());
        return PtrToHandle(dynStr);
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

void ITask_Settags_Clear(ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->set_tags({});
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

void ITask_Settags_Add(ITask_Handle handle, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    if (!value) {
        SetError("Null value");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        auto array = obj->get_tags();
        auto* str = HandleToPtr<IDynamicString>(value);
        array.push_back(str->GetValue());
        obj->set_tags(array);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: Complete
void ITask_Complete(
    ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->Complete(
);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: Cancel
void ITask_Cancel(
    ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->Cancel(
);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: IsOverdue
bool ITask_IsOverdue(
    ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        auto result = obj->IsOverdue(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetMetadata
TaskManagerDict_Handle ITask_GetMetadata(
    ITask_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        auto result = obj->GetMetadata(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: SetMetadata
void ITask_SetMetadata(
    ITask_Handle handle, IDynamicString_Handle key, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITask>(handle);
        obj->SetMetadata(
HandleToPtr<IDynamicString>(key)->GetValue(), HandleToPtr<IDynamicString>(value)->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// IProject implementation

IProject_Handle IProject_Create() {
    try {
        // Note: This assumes the C++ implementation has a concrete class
        // In practice, you'd need a factory or concrete implementation
        SetError("IProject_Create not implemented - interface requires concrete implementation");
        return nullptr;
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void IProject_Release(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        delete obj;
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

void IProject_AddRef(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    // Note: This would need proper reference counting implementation
    // For now, this is a no-op placeholder
}

// Property: id
IDynamicString_Handle IProject_Getid(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        std::string result = obj->get_id();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}


// Property: name
IDynamicString_Handle IProject_Getname(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        std::string result = obj->get_name();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void IProject_Setname(IProject_Handle handle, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    if (!value) {
        SetError("Null value");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto* str = HandleToPtr<IDynamicString>(value);
        obj->set_name(str->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: description
IDynamicString_Handle IProject_Getdescription(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return nullptr;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        std::string result = obj->get_description();
        // Create new IDynamicString with refcount=1
        IDynamicString* str = CreateDynamicString(result.c_str());
        return PtrToHandle(str);
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void IProject_Setdescription(IProject_Handle handle, IDynamicString_Handle value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    if (!value) {
        SetError("Null value");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto* str = HandleToPtr<IDynamicString>(value);
        obj->set_description(str->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Property: active
bool IProject_Getactive(IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        return obj->get_active();
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

void IProject_Setactive(IProject_Handle handle, bool value) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        obj->set_active(value);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: CreateTask
ITask_Handle IProject_CreateTask(
    IProject_Handle handle, IDynamicString_Handle title, IDynamicString_Handle description) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->CreateTask(
HandleToPtr<IDynamicString>(title)->GetValue(), HandleToPtr<IDynamicString>(description)->GetValue());
        return PtrToHandle(result.get());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTask
ITask_Handle IProject_GetTask(
    IProject_Handle handle, IDynamicString_Handle taskId) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetTask(
HandleToPtr<IDynamicString>(taskId)->GetValue());
        return PtrToHandle(result.get());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTasks
TaskManagerArray_Handle IProject_GetTasks(
    IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetTasks(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTasksByStatus
TaskManagerArray_Handle IProject_GetTasksByStatus(
    IProject_Handle handle, Status status) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetTasksByStatus(
static_cast<TaskManager::Status>(status));
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: DeleteTask
bool IProject_DeleteTask(
    IProject_Handle handle, IDynamicString_Handle taskId) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->DeleteTask(
HandleToPtr<IDynamicString>(taskId)->GetValue());
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTaskCount
int32_t IProject_GetTaskCount(
    IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetTaskCount(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetCompletedCount
int32_t IProject_GetCompletedCount(
    IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetCompletedCount(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTaskCountByStatus
TaskManagerDict_Handle IProject_GetTaskCountByStatus(
    IProject_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::IProject>(handle);
        auto result = obj->GetTaskCountByStatus(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// ITaskManager implementation

ITaskManager_Handle ITaskManager_Create() {
    try {
        // Note: This assumes the C++ implementation has a concrete class
        // In practice, you'd need a factory or concrete implementation
        SetError("ITaskManager_Create not implemented - interface requires concrete implementation");
        return nullptr;
    } catch (const std::exception& e) {
        SetError(e.what());
        return nullptr;
    }
}

void ITaskManager_Release(ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        delete obj;
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

void ITaskManager_AddRef(ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    // Note: This would need proper reference counting implementation
    // For now, this is a no-op placeholder
}

// Method: CreateProject
IProject_Handle ITaskManager_CreateProject(
    ITaskManager_Handle handle, IDynamicString_Handle name) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->CreateProject(
HandleToPtr<IDynamicString>(name)->GetValue());
        return PtrToHandle(result.get());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetProject
IProject_Handle ITaskManager_GetProject(
    ITaskManager_Handle handle, IDynamicString_Handle projectId) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetProject(
HandleToPtr<IDynamicString>(projectId)->GetValue());
        return PtrToHandle(result.get());
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetProjects
TaskManagerArray_Handle ITaskManager_GetProjects(
    ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetProjects(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetActiveProjects
TaskManagerArray_Handle ITaskManager_GetActiveProjects(
    ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetActiveProjects(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: DeleteProject
bool ITaskManager_DeleteProject(
    ITaskManager_Handle handle, IDynamicString_Handle projectId) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->DeleteProject(
HandleToPtr<IDynamicString>(projectId)->GetValue());
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: SearchTasks
TaskManagerArray_Handle ITaskManager_SearchTasks(
    ITaskManager_Handle handle, IDynamicString_Handle query) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->SearchTasks(
HandleToPtr<IDynamicString>(query)->GetValue());
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetTasksByPriority
TaskManagerArray_Handle ITaskManager_GetTasksByPriority(
    ITaskManager_Handle handle, Priority priority) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetTasksByPriority(
static_cast<TaskManager::Priority>(priority));
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetOverdueTasks
TaskManagerArray_Handle ITaskManager_GetOverdueTasks(
    ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetOverdueTasks(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: GetSettings
TaskManagerDict_Handle ITaskManager_GetSettings(
    ITaskManager_Handle handle) {
    if (!handle) {
        SetError("Null handle");
        return {};
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        auto result = obj->GetSettings(
);
        return result;
    } catch (const std::exception& e) {
        SetError(e.what());
        return {};
    }
}

// Method: UpdateSettings
void ITaskManager_UpdateSettings(
    ITaskManager_Handle handle, TaskManagerDict_Handle settings) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        obj->UpdateSettings(
settings);
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: Save
void ITaskManager_Save(
    ITaskManager_Handle handle, IDynamicString_Handle path) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        obj->Save(
HandleToPtr<IDynamicString>(path)->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Method: Load
void ITaskManager_Load(
    ITaskManager_Handle handle, IDynamicString_Handle path) {
    if (!handle) {
        SetError("Null handle");
        return;
    }
    try {
        auto* obj = HandleToPtr<TaskManager::ITaskManager>(handle);
        obj->Load(
HandleToPtr<IDynamicString>(path)->GetValue());
    } catch (const std::exception& e) {
        SetError(e.what());
    }
}

// Collection iteration helpers

struct ArrayIterator {
    size_t current = 0;
    // Would contain actual array data
};

struct DictIterator {
    size_t current = 0;
    // Would contain actual map iterator
};

struct SetIterator {
    size_t current = 0;
    // Would contain actual set iterator
};

void TaskManagerArray_Release(TaskManagerArray_Handle handle) {
    delete HandleToPtr<ArrayIterator>(handle);
}

size_t TaskManagerArray_Count(TaskManagerArray_Handle handle) {
    if (!handle) return 0;
    // Implementation would return actual count
    return 0;
}

void TaskManagerDict_Release(TaskManagerDict_Handle handle) {
    delete HandleToPtr<DictIterator>(handle);
}

size_t TaskManagerDict_Count(TaskManagerDict_Handle handle) {
    if (!handle) return 0;
    // Implementation would return actual count
    return 0;
}

bool TaskManagerDict_Next(TaskManagerDict_Handle handle, const char** key, void** value) {
    if (!handle) return false;
    // Implementation would iterate through dictionary
    return false;
}

void TaskManagerDict_Reset(TaskManagerDict_Handle handle) {
    if (!handle) return;
    auto* iter = HandleToPtr<DictIterator>(handle);
    iter->current = 0;
}

void TaskManagerSet_Release(TaskManagerSet_Handle handle) {
    delete HandleToPtr<SetIterator>(handle);
}

size_t TaskManagerSet_Count(TaskManagerSet_Handle handle) {
    if (!handle) return 0;
    // Implementation would return actual count
    return 0;
}

bool TaskManagerSet_Next(TaskManagerSet_Handle handle, void** value) {
    if (!handle) return false;
    // Implementation would iterate through set
    return false;
}

void TaskManagerSet_Reset(TaskManagerSet_Handle handle) {
    if (!handle) return;
    auto* iter = HandleToPtr<SetIterator>(handle);
    iter->current = 0;
}

} // extern "C"