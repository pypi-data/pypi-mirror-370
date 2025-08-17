// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/refBase.h"
#include "pxr/tf/diagnostic.h"

TF_NAMESPACE_OPEN_SCOPE

TfRefBase::UniqueChangedListener TfRefBase::_uniqueChangedListener;

TfRefBase::~TfRefBase()
{
}

void
TfRefBase::SetUniqueChangedListener(UniqueChangedListener listener)
{
    if (_uniqueChangedListener.lock ||
        _uniqueChangedListener.func ||
        _uniqueChangedListener.unlock) {
        TF_FATAL_ERROR("Setting an already set UniqueChangedListener");
    }
    _uniqueChangedListener = listener;
}

TfSimpleRefBase::~TfSimpleRefBase()
{
}

TF_NAMESPACE_CLOSE_SCOPE
