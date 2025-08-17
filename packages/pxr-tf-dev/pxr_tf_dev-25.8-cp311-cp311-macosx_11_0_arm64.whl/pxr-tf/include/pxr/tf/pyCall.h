// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_PY_CALL_H
#define PXR_TF_PY_CALL_H

/// \file tf/pyCall.h
/// Utilities for calling python callables.
/// 
/// These functions handle trapping python errors and converting them to \a
/// TfErrors.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyError.h"
#include "pxr/tf/pyLock.h"
#include "pxr/tf/pyObjWrapper.h"

#include <pxr/boost/python/call.hpp>

TF_NAMESPACE_OPEN_SCOPE

/// \class TfPyCall
///
/// Provide a way to call a Python callable.
/// 
/// Usage is as follows:
/// \code
///     return TfPyCall<RetType>(callable)(arg1, arg2, ... argN);
/// \endcode
/// Generally speaking, TfPyCall instances may be copied, assigned, destroyed,
/// and invoked without the client holding the GIL.  However, if the \a Return
/// template parameter is a \a pxr_boost::python::object (or a derived class, such
/// as list or tuple) then the client must hold the GIL in order to invoke the
/// call operator.
template <typename Return>
struct TfPyCall {
    /// Construct with callable \a c.  Constructing with a \c
    /// pxr_boost::python::object works, since those implicitly convert to \c
    /// TfPyObjWrapper, however in that case the GIL must be held by the caller.
    explicit TfPyCall(TfPyObjWrapper const &c) : _callable(c) {}

    template <typename... Args>
    Return operator()(Args... args);

private:
    TfPyObjWrapper _callable;
};

template <typename Return>
template <typename... Args>
inline Return
TfPyCall<Return>::operator()(Args... args)
{
    TfPyLock pyLock;
    // Do *not* call through if there's an active python exception.
    if (!PyErr_Occurred()) {
        try {
            return pxr_boost::python::call<Return>
                (_callable.ptr(), args...);
        } catch (pxr_boost::python::error_already_set const &) {
            // Convert any exception to TF_ERRORs.
            TfPyConvertPythonExceptionToTfErrors();
            PyErr_Clear();
        }
    }
    return Return();
}

TF_NAMESPACE_CLOSE_SCOPE

#endif
