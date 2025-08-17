// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_STATUS_H
#define PXR_TF_STATUS_H

#include "pxr/tf/pxr.h"

#include "pxr/tf/diagnosticBase.h"

TF_NAMESPACE_OPEN_SCOPE

/// \class TfStatus
/// \ingroup group_tf_Diagnostic
///
/// Represents an object that contains information about a status message.
/// 
/// See \ref page_tf_Diagnostic in the C++ API reference for a detailed
/// description of the status message issuing API.  For a example of how to
/// post a status message, see \c TF_STATUS(), also in the C++ API reference.
///
/// In the Python API, you can issue a status message with Tf.Status().
///
class TfStatus: public TfDiagnosticBase
{
private:
    TfStatus(TfEnum statusCode, char const *statusCodeString,
            TfCallContext const &context, const std::string& commentary,
            TfDiagnosticInfo info, bool quiet)
        : TfDiagnosticBase(statusCode, statusCodeString, context,
                            commentary, info, quiet)
    { }

    friend class TfDiagnosticMgr;
};

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_STATUS_H
