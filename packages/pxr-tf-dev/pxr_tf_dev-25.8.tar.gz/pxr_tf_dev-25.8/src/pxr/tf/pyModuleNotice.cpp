// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyModuleNotice.h"

TF_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType) {
    TfType::Define<TfPyModuleWasLoaded, TfType::Bases<TfNotice> >();
}

TfPyModuleWasLoaded::~TfPyModuleWasLoaded() {
}

TF_NAMESPACE_CLOSE_SCOPE
