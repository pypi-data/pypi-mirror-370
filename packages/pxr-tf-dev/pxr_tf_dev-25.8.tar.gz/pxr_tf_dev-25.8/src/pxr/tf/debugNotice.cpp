// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/debugNotice.h"
#include "pxr/tf/registryManager.h"
#include "pxr/tf/type.h"

TF_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType)
{
    TfType::Define< TfDebugSymbolsChangedNotice,
        TfType::Bases<TfNotice> >();
    TfType::Define< TfDebugSymbolEnableChangedNotice,
        TfType::Bases<TfNotice> >();
}

TfDebugSymbolsChangedNotice::~TfDebugSymbolsChangedNotice() {}
TfDebugSymbolEnableChangedNotice::~TfDebugSymbolEnableChangedNotice() {}

TF_NAMESPACE_CLOSE_SCOPE
