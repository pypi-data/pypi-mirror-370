// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/errorTransport.h"

TF_NAMESPACE_OPEN_SCOPE

void
TfErrorTransport::_PostImpl()
{
    TfDiagnosticMgr::GetInstance()._SpliceErrors(_errorList);
}

TF_NAMESPACE_CLOSE_SCOPE
