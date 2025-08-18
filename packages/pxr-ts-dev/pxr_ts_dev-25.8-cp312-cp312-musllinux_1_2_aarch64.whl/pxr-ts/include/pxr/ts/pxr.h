// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TS_H
#define PXR_TS_H

#define TS_MAJOR_VERSION 0
#define TS_MINOR_VERSION 25
#define TS_PATCH_VERSION 8

#define TS_VERSION (TS_MAJOR_VERSION * 10000 \
                  + TS_MINOR_VERSION * 100   \
                  + TS_PATCH_VERSION)

#define TS_NS pxr
#define TS_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define TS_NS_GLOBAL ::TS_NS

namespace TS_INTERNAL_NS { }

namespace TS_NS {
    using namespace TS_INTERNAL_NS;
}

#define TS_NAMESPACE_OPEN_SCOPE   namespace TS_INTERNAL_NS {
#define TS_NAMESPACE_CLOSE_SCOPE  }
#define TS_NAMESPACE_USING_DIRECTIVE using namespace TS_NS;

#endif // PXR_TS_H
