// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_NULL_PTR_H
#define PXR_TF_NULL_PTR_H

#include "pxr/tf/pxr.h"
#include "pxr/tf/api.h"

TF_NAMESPACE_OPEN_SCOPE

// A type used to create the \a TfNullPtr token.
struct TfNullPtrType
{
};

// A token to represent null for smart pointers like \a TfWeakPtr and \a
// TfRefPtr.
TF_API extern const TfNullPtrType TfNullPtr;

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_NULL_PTR_H
