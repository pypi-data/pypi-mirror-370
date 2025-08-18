// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_REPORTER_DATA_SOURCE_BASE_H
#define PXR_TRACE_REPORTER_DATA_SOURCE_BASE_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include "pxr/trace/collection.h"

#include <vector>

TRACE_NAMESPACE_OPEN_SCOPE

////////////////////////////////////////////////////////////////////////////////
/// \class TraceReporterDataSourceBase
///
/// This class is a base class for TraceReporterBase data sources. 
/// TraceReporterBase uses an instance of a TraceReporterDataSourceBase derived 
/// class to access TraceCollections.
///
class TraceReporterDataSourceBase {
public:
    using CollectionPtr = std::shared_ptr<TraceCollection>;

    /// Destructor
    TRACE_API virtual ~TraceReporterDataSourceBase();

    /// Removes all references to TraceCollections.
    virtual void Clear() = 0;

    /// Returns the next TraceCollections which need to be processed.
    virtual std::vector<CollectionPtr> ConsumeData() = 0;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_REPORTER_DATA_SOURCE_BASE_H