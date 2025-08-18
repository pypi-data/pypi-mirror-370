// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_GF_H
#define PXR_GF_H

#define GF_MAJOR_VERSION 0
#define GF_MINOR_VERSION 25
#define GF_PATCH_VERSION 8

#define GF_VERSION (GF_MAJOR_VERSION * 10000 \
                  + GF_MINOR_VERSION * 100   \
                  + GF_PATCH_VERSION)

#define GF_NS pxr
#define GF_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define GF_NS_GLOBAL ::GF_NS

namespace GF_INTERNAL_NS { }

namespace GF_NS {
    using namespace GF_INTERNAL_NS;
}

#define GF_NAMESPACE_OPEN_SCOPE   namespace GF_INTERNAL_NS {
#define GF_NAMESPACE_CLOSE_SCOPE  }
#define GF_NAMESPACE_USING_DIRECTIVE using namespace GF_NS;

#endif // PXR_GF_H
