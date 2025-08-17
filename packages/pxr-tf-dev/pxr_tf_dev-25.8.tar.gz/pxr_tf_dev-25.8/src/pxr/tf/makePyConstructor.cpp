// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/makePyConstructor.h"

TF_NAMESPACE_OPEN_SCOPE

namespace Tf_MakePyConstructor {

bp::object _DummyInit(bp::tuple const & /* args */,
                      bp::dict const & /* kw */) {
    return bp::object();
}

}

TF_NAMESPACE_CLOSE_SCOPE
