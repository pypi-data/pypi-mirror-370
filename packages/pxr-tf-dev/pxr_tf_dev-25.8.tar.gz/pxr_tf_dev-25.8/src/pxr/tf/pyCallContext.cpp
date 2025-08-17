// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/pyCallContext.h"
#include "pxr/tf/callContext.h"
#include "pxr/tf/stringUtils.h"

#include <tbb/spin_mutex.h>

#include <set>
#include <string>

using namespace std;

namespace {
    struct _Cache {
        tbb::spin_mutex lock;
        set<string> data;
    };
}


TF_NAMESPACE_OPEN_SCOPE

/*
 * TfCallContext's contain const char*'s which are assumed to be program literals.
 * That assumption fails badly when it comes to python.
 */
TfCallContext
Tf_PythonCallContext(char const *fileName,
                     char const *moduleName,
                     char const *functionName,
                     size_t line)
{
    static _Cache cache;

    string const& fullName = TfStringPrintf("%s.%s", moduleName, functionName);

    tbb::spin_mutex::scoped_lock lock(cache.lock);
    char const* prettyFunctionPtr = cache.data.insert(fullName).first->c_str();
    char const* fileNamePtr = cache.data.insert(fileName).first->c_str();

    return TfCallContext(fileNamePtr, prettyFunctionPtr, line, prettyFunctionPtr);
}

TF_NAMESPACE_CLOSE_SCOPE
