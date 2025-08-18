// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_PLUG_H
#define PXR_PLUG_H

#define PLUG_MAJOR_VERSION 0
#define PLUG_MINOR_VERSION 25
#define PLUG_PATCH_VERSION 8

#define PLUG_VERSION (PLUG_MAJOR_VERSION * 10000 \
                    + PLUG_MINOR_VERSION * 100   \
                    + PLUG_PATCH_VERSION)

#define PLUG_NS pxr
#define PLUG_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define PLUG_NS_GLOBAL ::PLUG_NS

namespace PLUG_INTERNAL_NS { }

namespace PLUG_NS {
    using namespace PLUG_INTERNAL_NS;
}

#define PLUG_NAMESPACE_OPEN_SCOPE   namespace PLUG_INTERNAL_NS {
#define PLUG_NAMESPACE_CLOSE_SCOPE  }
#define PLUG_NAMESPACE_USING_DIRECTIVE using namespace PLUG_NS;

#endif // PXR_PLUG_H
