// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyErrorInternal.h"

#include "pxr/tf/enum.h"
#include "pxr/tf/registryManager.h"

#include <pxr/boost/python/handle.hpp>
#include <pxr/boost/python/object.hpp>

TF_NAMESPACE_OPEN_SCOPE

using namespace pxr_boost::python;

TF_REGISTRY_FUNCTION(TfEnum) {
    TF_ADD_ENUM_NAME(TF_PYTHON_EXCEPTION);
}

// Should probably use a better mechanism.

static handle<> _ExceptionClass;

handle<> Tf_PyGetErrorExceptionClass()
{
    return _ExceptionClass;
}

void Tf_PySetErrorExceptionClass(object const &cls)
{
    _ExceptionClass = handle<>(borrowed(cls.ptr()));
}

TfPyExceptionStateScope::TfPyExceptionStateScope() :
    _state(TfPyExceptionState::Fetch())
{
}

TfPyExceptionStateScope::~TfPyExceptionStateScope()
{
    _state.Restore();
}

TF_NAMESPACE_CLOSE_SCOPE
