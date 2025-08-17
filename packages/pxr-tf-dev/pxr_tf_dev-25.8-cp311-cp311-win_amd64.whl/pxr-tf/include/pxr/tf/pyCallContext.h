// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_PY_CALL_CONTEXT_H
#define PXR_TF_PY_CALL_CONTEXT_H

#include "pxr/tf/callContext.h"

TF_NAMESPACE_OPEN_SCOPE

TF_API TfCallContext
Tf_PythonCallContext(char const *fileName,
                     char const *moduleName,
                     char const *functionName,
                     size_t line);

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_PY_CALL_CONTEXT_H
