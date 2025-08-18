// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_VT_H
#define PXR_VT_H

#define VT_MAJOR_VERSION 0
#define VT_MINOR_VERSION 25
#define VT_PATCH_VERSION 8

#define VT_VERSION (VT_MAJOR_VERSION * 10000 \
                  + VT_MINOR_VERSION * 100   \
                  + VT_PATCH_VERSION)

#define VT_NS pxr
#define VT_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define VT_NS_GLOBAL ::VT_NS

namespace VT_INTERNAL_NS { }

namespace VT_NS {
    using namespace VT_INTERNAL_NS;
}

#define VT_NAMESPACE_OPEN_SCOPE   namespace VT_INTERNAL_NS {
#define VT_NAMESPACE_CLOSE_SCOPE  }
#define VT_NAMESPACE_USING_DIRECTIVE using namespace VT_NS;

#endif // PXR_VT_H
