// Copyright 2019 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/smallVector.h"

TF_NAMESPACE_OPEN_SCOPE

#ifndef ARCH_OS_WASM_VM
static_assert(
    sizeof(TfSmallVector<int, 1>) == 16,
    "Expecting sizeof(TfSmallVector<int, N = 1>) to be 16 bytes.");
#else
static_assert(
    sizeof(TfSmallVector<int, 1>) == 12,
    "Expecting sizeof(TfSmallVector<int, N = 1>) to be 12 bytes.");
#endif

static_assert(
    sizeof(TfSmallVector<int, 2>) == 16,
    "Expecting sizeof(TfSmallVector<int, N = 2>) to be 16 bytes.");

static_assert(
    sizeof(TfSmallVector<double, 1>) == 16,
    "Expecting sizeof(TfSmallVector<double, N = 1>) to be 16 bytes.");

static_assert(
    sizeof(TfSmallVector<double, 2>) == 24,
    "Expecting sizeof(TfSmallVector<double, N = 2>) to be 24 bytes.");

#ifndef ARCH_OS_WASM_VM
static_assert(
    TfSmallVectorBase::ComputeSerendipitousLocalCapacity<char>() == 8,
    "Expecting 8 bytes of local capacity.");
#else
static_assert(
    TfSmallVectorBase::ComputeSerendipitousLocalCapacity<char>() == 4,
    "Expecting 4 bytes of local capacity.");
#endif

TF_NAMESPACE_CLOSE_SCOPE
