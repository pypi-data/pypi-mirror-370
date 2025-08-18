// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TRACE_H
#define PXR_TRACE_H

#define TRACE_MAJOR_VERSION 0
#define TRACE_MINOR_VERSION 25
#define TRACE_PATCH_VERSION 8

#define TRACE_VERSION (TRACE_MAJOR_VERSION * 10000 \
                     + TRACE_MINOR_VERSION * 100   \
                     + TRACE_PATCH_VERSION)

#define TRACE_NS pxr
#define TRACE_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define TRACE_NS_GLOBAL ::TRACE_NS

namespace TRACE_INTERNAL_NS { }

namespace TRACE_NS {
    using namespace TRACE_INTERNAL_NS;
}

#define TRACE_NAMESPACE_OPEN_SCOPE   namespace TRACE_INTERNAL_NS {
#define TRACE_NAMESPACE_CLOSE_SCOPE  }
#define TRACE_NAMESPACE_USING_DIRECTIVE using namespace TRACE_NS;

#endif // PXR_TRACE_H
