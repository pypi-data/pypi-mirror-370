// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_AGGREGATE_TREE_BUILDER_H
#define PXR_TRACE_AGGREGATE_TREE_BUILDER_H

#include "pxr/trace/pxr.h"

#include "pxr/trace/api.h"
#include "pxr/trace/collection.h"
#include "pxr/trace/aggregateTree.h"
#include "pxr/trace/eventTree.h"

TRACE_NAMESPACE_OPEN_SCOPE

////////////////////////////////////////////////////////////////////////////////
/// \class Trace_AggregateTreeBuilder
///
/// This class populates a tree of TraceAggregateTree instances from
/// TraceCollection instances.
///
///
class Trace_AggregateTreeBuilder : private TraceCollection::Visitor
{
public:
    static void AddEventTreeToAggregate(
        TraceAggregateTree* aggregateTree,
        const TraceEventTreeRefPtr& eventTree,
        const TraceCollection& collection);

private:
    Trace_AggregateTreeBuilder(
        TraceAggregateTree* tree, const TraceEventTreeRefPtr& eventTree);

    void _ProcessCounters(const TraceCollection& collection);

    void _CreateAggregateNodes();

    // TraceCollection::Visitor interface
    virtual void OnBeginCollection() override;
    virtual void OnEndCollection() override;
    virtual void OnBeginThread(const TraceThreadId& threadId) override;
    virtual void OnEndThread(const TraceThreadId& threadId) override;
    virtual bool AcceptsCategory(TraceCategoryId categoryId) override;
    virtual void OnEvent(
        const TraceThreadId& threadIndex, 
        const TfToken& key, 
        const TraceEvent& e) override;

    void _OnCounterEvent(const TraceThreadId& threadIndex, 
        const TfToken& key, 
        const TraceEvent& e);

    TraceAggregateNodePtr _FindAggregateNode(
        const TraceThreadId& threadId, const TraceEvent::TimeStamp ts) const ;

    TraceAggregateTree* _aggregateTree;
    TraceEventTreeRefPtr _tree;
};

TRACE_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TRACE_AGGREGATE_TREE_BUILDER_H
