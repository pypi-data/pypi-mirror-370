// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_REPORTER_BASE_H
#define PXR_TRACE_REPORTER_BASE_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include "pxr/trace/collectionNotice.h"
#include "pxr/trace/collection.h"
#include "pxr/trace/reporterDataSourceBase.h"

#include <pxr/tf/declarePtrs.h>

#include <tbb/concurrent_vector.h>

#include <ostream>

TRACE_NAMESPACE_OPEN_SCOPE

TF_DECLARE_WEAK_AND_REF_PTRS(TraceReporterBase);

////////////////////////////////////////////////////////////////////////////////
/// \class TraceReporterBase
///
/// This class is a base class for report implementations. It handles receiving 
/// and processing of TraceCollections.
///
///
class TraceReporterBase :
    public TfRefBase, public TfWeakBase {
public:
    using This = TraceReporterBase;
    using ThisPtr = TraceReporterBasePtr;
    using ThisRefPtr = TraceReporterBaseRefPtr;
    using CollectionPtr = std::shared_ptr<TraceCollection>;
    using DataSourcePtr = std::unique_ptr<TraceReporterDataSourceBase>;

    /// Constructor taking ownership of \p dataSource.
    TRACE_API TraceReporterBase(DataSourcePtr dataSource);

    /// Destructor.
    TRACE_API virtual ~TraceReporterBase();

    /// Write all collections that were processed by this reporter to \p ostr.
    TRACE_API bool SerializeProcessedCollections(std::ostream& ostr) const;
protected:
    /// Removes all references to TraceCollections.
    TRACE_API void _Clear();

    /// Gets the latest data from the TraceCollector singleton and processes all
    /// collections that have been received since the last call to _Update().
    TRACE_API void _Update();

    /// Called once per collection from _Update()
    virtual void _ProcessCollection(const CollectionPtr&) = 0;

private:
    DataSourcePtr _dataSource;
    tbb::concurrent_vector<CollectionPtr> _processedCollections;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_REPORTER_BASE_H
