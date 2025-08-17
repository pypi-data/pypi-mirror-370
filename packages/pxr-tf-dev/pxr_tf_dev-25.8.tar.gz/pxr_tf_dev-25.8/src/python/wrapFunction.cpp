// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>
#include <pxr/tf/pyFunction.h>
#include <pxr/tf/pyObjWrapper.h>

#include <pxr/boost/python/object.hpp>

#include <string>

TF_NAMESPACE_USING_DIRECTIVE

void wrapFunction() {
    TfPyFunctionFromPython<void ()>();
    TfPyFunctionFromPython<bool ()>();
    TfPyFunctionFromPython<int ()>();
    TfPyFunctionFromPython<long ()>();
    TfPyFunctionFromPython<double ()>();
    TfPyFunctionFromPython<std::string ()>();
    TfPyFunctionFromPython<pxr_boost::python::object ()>();
    TfPyFunctionFromPython<TfPyObjWrapper ()>();
}
