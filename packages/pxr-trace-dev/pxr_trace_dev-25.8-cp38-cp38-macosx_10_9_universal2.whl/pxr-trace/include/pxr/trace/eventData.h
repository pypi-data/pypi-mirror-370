// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_EVENT_DATA_H
#define PXR_TRACE_EVENT_DATA_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include "pxr/trace/event.h"

#include <string>
#include <variant>

TRACE_NAMESPACE_OPEN_SCOPE

class JsWriter;
////////////////////////////////////////////////////////////////////////////////
///
/// \class TraceEventData
///
/// This class holds data that can be stored in TraceEvents.
///
class TraceEventData {
public:
    /// Ctor for Invalid type.
    TraceEventData() : _data(_NoData()) {}

    /// Ctor for Bool type.
    explicit TraceEventData(bool b) : _data(b) {}

    /// Ctor for Int type.
    explicit TraceEventData(int64_t i) : _data(i) {}

    /// Ctor for UInt type.
    explicit TraceEventData(uint64_t i) : _data(i) {}
    
    /// Ctor for Float type.
    explicit TraceEventData(double d) : _data(d) {}

    /// Ctor for String type.
    explicit TraceEventData(const std::string& s) : _data(s) {}

    /// Returns the Type of the data stored.
    TRACE_API TraceEvent::DataType GetType() const;

    /// Returns a pointer to the data or nullptr if the type is not Int.
    TRACE_API const int64_t* GetInt() const;

    /// Returns a pointer to the data or nullptr if the type is not UInt.
    TRACE_API const uint64_t* GetUInt() const;

    /// Returns a pointer to the data or nullptr if the type is not Float.
    TRACE_API const double* GetFloat() const;

    /// Returns a pointer to the data or nullptr if the type is not Bool.
    TRACE_API const bool* GetBool() const;

    /// Returns a pointer to the data or nullptr if the type is not String.
    TRACE_API const std::string* GetString() const;

    /// Writes a json representation of the data.
    TRACE_API void WriteJson(JsWriter&) const;

private:
    // Type that represents no data was stored in an event.
    struct _NoData {};

    using Variant = 
        std::variant<_NoData, std::string, bool, int64_t, uint64_t, double>;
    Variant _data;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_EVENT_DATA_H