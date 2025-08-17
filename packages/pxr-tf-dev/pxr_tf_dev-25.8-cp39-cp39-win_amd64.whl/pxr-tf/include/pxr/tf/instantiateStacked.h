// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifdef PXR_TF_INSTANTIATE_STACKED_H
#error This file may be included only once in a translation unit (.cpp file).
#endif

#define PXR_TF_INSTANTIATE_STACKED_H

#include "pxr/tf/pxr.h"
#include "pxr/tf/stacked.h"

TF_NAMESPACE_OPEN_SCOPE

#define TF_INSTANTIATE_STACKED(Derived)                \
    template <>                                        \
    std::atomic<typename Derived::Storage::Type*>      \
    Derived::Storage::value(nullptr)

#define TF_INSTANTIATE_DEFINED_STACKED(Derived)        \
    std::atomic<typename Derived::Storage::Type*>      \
    Derived::Storage::value(nullptr)

TF_NAMESPACE_CLOSE_SCOPE
