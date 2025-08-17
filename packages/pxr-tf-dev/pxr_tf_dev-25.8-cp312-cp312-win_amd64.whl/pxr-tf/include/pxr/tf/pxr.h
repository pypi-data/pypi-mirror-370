// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_H
#define PXR_TF_H

#define TF_MAJOR_VERSION 0
#define TF_MINOR_VERSION 25
#define TF_PATCH_VERSION 8

#define TF_VERSION 

#define TF_NS pxr
#define TF_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define TF_NS_GLOBAL ::TF_NS

namespace TF_INTERNAL_NS { }

namespace TF_NS {
    using namespace TF_INTERNAL_NS;
}

#define TF_NAMESPACE_OPEN_SCOPE   namespace TF_INTERNAL_NS {
#define TF_NAMESPACE_CLOSE_SCOPE  }
#define TF_NAMESPACE_USING_DIRECTIVE using namespace TF_NS;

#endif // PXR_TF_H
