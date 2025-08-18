// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_JS_H
#define PXR_JS_H

#define JS_MAJOR_VERSION 0
#define JS_MINOR_VERSION 25
#define JS_PATCH_VERSION 8

#define JS_VERSION (JS_MAJOR_VERSION * 10000 \
                  + JS_MINOR_VERSION * 100   \
                  + JS_PATCH_VERSION)

#define JS_NS pxr
#define JS_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define JS_NS_GLOBAL ::JS_NS

namespace JS_INTERNAL_NS { }

namespace JS_NS {
    using namespace JS_INTERNAL_NS;
}

#define JS_NAMESPACE_OPEN_SCOPE   namespace JS_INTERNAL_NS {
#define JS_NAMESPACE_CLOSE_SCOPE  }
#define JS_NAMESPACE_USING_DIRECTIVE using namespace JS_NS;

#endif // PXR_JS_H
