// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_KIND_H
#define PXR_KIND_H

#define KIND_MAJOR_VERSION 0
#define KIND_MINOR_VERSION 25
#define KIND_PATCH_VERSION 8

#define KIND_VERSION (KIND_MAJOR_VERSION * 10000 \
                    + KIND_MINOR_VERSION * 100   \
                    + KIND_PATCH_VERSION)

#define KIND_NS pxr
#define KIND_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define KIND_NS_GLOBAL ::KIND_NS

namespace KIND_INTERNAL_NS { }

namespace KIND_NS {
    using namespace KIND_INTERNAL_NS;
}

#define KIND_NAMESPACE_OPEN_SCOPE   namespace KIND_INTERNAL_NS {
#define KIND_NAMESPACE_CLOSE_SCOPE  }
#define KIND_NAMESPACE_USING_DIRECTIVE using namespace KIND_NS;

#endif // PXR_KIND_H
