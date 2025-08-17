// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/diagnosticBase.h"

#include "pxr/tf/stringUtils.h"
#include "pxr/tf/diagnosticMgr.h"
#include "pxr/tf/registryManager.h"

#include <string>

using std::string;

TF_NAMESPACE_OPEN_SCOPE

TfDiagnosticBase::TfDiagnosticBase(
    TfEnum code, const char* codeString,
    TfCallContext const &context, const string& commentary,
    TfDiagnosticInfo info, bool quiet)
    : _context(context)
{
    _commentary = commentary;
    _code = code;
    _codeString = TfEnum::GetName(code);
    _info = info;
    _quiet = quiet;
    
    if (_codeString.empty())
        _codeString = TfSafeString(codeString);
}

bool
TfDiagnosticBase::IsFatal() const
{
    TfEnum code = _code;
    return (code == TF_DIAGNOSTIC_FATAL_CODING_ERROR_TYPE) ||
           (code == TF_DIAGNOSTIC_FATAL_ERROR_TYPE) ||
           (code == TF_APPLICATION_EXIT_TYPE);
}

bool
TfDiagnosticBase::IsCodingError() const
{
    TfEnum code = _code;
    return (code == TF_DIAGNOSTIC_CODING_ERROR_TYPE) ||
           (code == TF_DIAGNOSTIC_FATAL_CODING_ERROR_TYPE);
}

TF_NAMESPACE_CLOSE_SCOPE
