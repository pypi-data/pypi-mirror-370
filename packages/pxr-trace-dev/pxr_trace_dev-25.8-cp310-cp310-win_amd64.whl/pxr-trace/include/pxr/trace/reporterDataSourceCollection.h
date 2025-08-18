// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_REPORTER_DATA_SOURCE_COLLECTION_H
#define PXR_TRACE_REPORTER_DATA_SOURCE_COLLECTION_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include "pxr/trace/collection.h"
#include "pxr/trace/reporterDataSourceBase.h"

#include <vector>

TRACE_NAMESPACE_OPEN_SCOPE

////////////////////////////////////////////////////////////////////////////////
/// \class TraceReporterDataSourceCollection
///
/// This class is an implementation of TraceReporterDataSourceBase which provides 
/// access to a set number of TraceCollection instances. This class is useful if
/// you want to generate reports from serialized TraceCollections.
///
class TraceReporterDataSourceCollection : public TraceReporterDataSourceBase {
public:
    using This = TraceReporterDataSourceCollection;
    using ThisRefPtr = std::unique_ptr<This>;

    static ThisRefPtr New(CollectionPtr collection) {
        return ThisRefPtr(new This(collection));
    }
    static ThisRefPtr New(std::vector<CollectionPtr> collections) {
        return ThisRefPtr(new This(std::move(collections)));
    }

    /// Removes all references to TraceCollections.
    TRACE_API void Clear() override;

    /// Returns the next TraceCollections which need to be processed.
    TRACE_API std::vector<CollectionPtr> ConsumeData() override;

private:
    TRACE_API TraceReporterDataSourceCollection(CollectionPtr collection);
    TRACE_API TraceReporterDataSourceCollection(
        std::vector<CollectionPtr> collections);

    std::vector<CollectionPtr> _data;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_REPORTER_DATA_SOURCE_COLLECTION_H