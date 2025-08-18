// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_WORK_H
#define PXR_WORK_H

#define WORK_MAJOR_VERSION 0
#define WORK_MINOR_VERSION 25
#define WORK_PATCH_VERSION 8

#define WORK_VERSION (WORK_MAJOR_VERSION * 10000 \
                    + WORK_MINOR_VERSION * 100   \
                    + WORK_PATCH_VERSION)

#define WORK_NS pxr
#define WORK_INTERNAL_NS pxrInternal_v0_25_8__pxrReserved__
#define WORK_NS_GLOBAL ::WORK_NS

namespace WORK_INTERNAL_NS { }

namespace WORK_NS {
    using namespace WORK_INTERNAL_NS;
}

#define WORK_NAMESPACE_OPEN_SCOPE   namespace WORK_INTERNAL_NS {
#define WORK_NAMESPACE_CLOSE_SCOPE  }
#define WORK_NAMESPACE_USING_DIRECTIVE using namespace WORK_NS;

#endif // PXR_WORK_H
