// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_COLLECTION_NOTICE_H
#define PXR_TRACE_COLLECTION_NOTICE_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include <pxr/tf/notice.h>
#include "pxr/trace/collection.h"

TRACE_NAMESPACE_OPEN_SCOPE

///////////////////////////////////////////////////////////////////////////////
/// \class TraceCollectionAvailable
///
/// A TfNotice that is sent when the TraceCollector creates a TraceCollection.
/// This can potentially be sent from multiple threads. Listeners must be 
/// thread safe.
class TraceCollectionAvailable : public TfNotice
{
public:
    /// Constructor.
    TraceCollectionAvailable(const std::shared_ptr<TraceCollection>& collection)
        : _collection(collection)
    {}

    /// Destructor.
    TRACE_API virtual ~TraceCollectionAvailable();

    /// Returns the TraceCollection which was produced.
    const std::shared_ptr<TraceCollection>& GetCollection() const {
        return _collection;
    }

private:
    std::shared_ptr<TraceCollection> _collection;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_COLLECTION_NOTICE_H