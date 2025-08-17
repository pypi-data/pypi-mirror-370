// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_DEBUG_NOTICE_H
#define PXR_TF_DEBUG_NOTICE_H

/// \file tf/debugNotice.h

#include "pxr/tf/pxr.h"
#include "pxr/tf/notice.h"

TF_NAMESPACE_OPEN_SCOPE

/// \class TfDebugSymbolsChangedNotice
///
/// Sent when the list of available debug symbol names has changed.
class TfDebugSymbolsChangedNotice : public TfNotice
{
public:
    TfDebugSymbolsChangedNotice() {}
    virtual ~TfDebugSymbolsChangedNotice();
};

/// \class TfDebugSymbolEnableChangedNotice
///
/// Sent when a debug symbol has been enabled or disabled.
class TfDebugSymbolEnableChangedNotice : public TfNotice
{
public:
    TfDebugSymbolEnableChangedNotice() {}
    virtual ~TfDebugSymbolEnableChangedNotice();
};

TF_NAMESPACE_CLOSE_SCOPE

#endif
