// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_AR_H
#define PXR_AR_H

#define AR_MAJOR_VERSION 0
#define AR_MINOR_VERSION 25
#define AR_PATCH_VERSION 8

#define AR_NS pxr
#define AR_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define AR_NS_GLOBAL ::AR_NS

namespace AR_INTERNAL_NS { }

namespace AR_NS {
    using namespace AR_INTERNAL_NS;
}

#define AR_NAMESPACE_OPEN_SCOPE   namespace AR_INTERNAL_NS {
#define AR_NAMESPACE_CLOSE_SCOPE  }
#define AR_NAMESPACE_USING_DIRECTIVE using namespace AR_NS;

#endif // PXR_AR_H
