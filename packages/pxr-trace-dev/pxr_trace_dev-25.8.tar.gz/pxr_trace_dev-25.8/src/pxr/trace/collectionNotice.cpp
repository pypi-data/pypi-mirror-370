// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/trace/collectionNotice.h"

#include "pxr/trace/pxr.h"
#include <pxr/tf/registryManager.h>
#include <pxr/tf/type.h>

TRACE_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType)
{
    TfType::Define< TraceCollectionAvailable,
        TfType::Bases<TfNotice> >();
}

TraceCollectionAvailable::~TraceCollectionAvailable() {}

TRACE_NAMESPACE_CLOSE_SCOPE
