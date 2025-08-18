// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/trace/pxr.h>

#include <pxr/tf/pyModule.h>

TRACE_NAMESPACE_USING_DIRECTIVE

TF_WRAP_MODULE
{
    TF_WRAP( Collector );
    TF_WRAP( AggregateNode );
    TF_WRAP( AggregateTree );
    TF_WRAP( Reporter );

    TF_WRAP( TestTrace );
}
