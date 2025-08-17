// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_CALL_CONTEXT_H
#define PXR_TF_CALL_CONTEXT_H

/// \file tf/callContext.h
/// Functions for recording call locations.
///
/// Many macros want to record the location in which they are invoked.  In
/// fact, this is the most useful feature that function-like macros have over
/// regular functions.  This code provides a standard way to collect and pass
/// that contextual information around.  There are two parts.  First is a
/// small structure which holds the contextual information.  Next is a macro
/// which will produce a temporary structure containing the local contextual
/// information. The intended usage is in a macro.

#include "pxr/tf/pxr.h"
#include "pxr/tf/api.h"
#include <pxr/arch/functionLite.h>

#include <stddef.h>

TF_NAMESPACE_OPEN_SCOPE

/// \hideinitializer
#define TF_CALL_CONTEXT \
TF_NS::TfCallContext(__ARCH_FILE__, __ARCH_FUNCTION__, __LINE__, __ARCH_PRETTY_FUNCTION__)

class TfCallContext
{
public:
    constexpr TfCallContext()
        : _file(nullptr)
        , _function(nullptr)
        , _line(0)
        , _prettyFunction(nullptr)
        , _hidden(false) {}
    
    constexpr TfCallContext(char const *file,
                            char const *function,
                            size_t line,
                            char const *prettyFunction) :
        _file(file),
        _function(function),
        _line(line),
        _prettyFunction(prettyFunction),
        _hidden(false)
    {
    }

    char const *GetFile() const {
        return _file;
    }

    char const *GetFunction() const {
        return _function;
    }

    size_t GetLine() const {
        return _line;
    }

    char const *GetPrettyFunction() const {
        return _prettyFunction;
    }

    TfCallContext const& Hide() const {
        _hidden = true;
        return *this;
    }
    
    bool IsHidden() const {
        return _hidden;
    }

    explicit operator bool() const { return _file && _function; }
    
  private:

    char const *_file;
    char const *_function;
    size_t _line;
    char const *_prettyFunction;
    mutable bool _hidden;
};

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_CALL_CONTEXT_H
