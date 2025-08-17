// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_DIAGNOSTIC_LITE_H
#define PXR_TF_DIAGNOSTIC_LITE_H

/// \file tf/diagnosticLite.h
/// Stripped down version of \c diagnostic.h that doesn't define \c std::string.
///
/// This file provides the same functionality as \c diagnostic.h, except that
/// all strings must be passed as plain \c const \c char*, and not by
/// \c std::string, and the macro \c TF_FUNCTION_NAME() is only defined by
/// \c diagnostic.h
///
/// In particular, this header file does not include the C++ header file
/// \c < \c string \c >, making inclusion of this file a very light-weight
/// addition. Include this file, as opposed to pxr/tf/diagnostic.h in
/// header files that need to remain as light-weight as possible.
///
/// These macros are safe to use in multiple threads.

#include "pxr/tf/pxr.h"
#include <pxr/arch/attributes.h>
#include "pxr/tf/api.h"
#include <pxr/arch/buildMode.h>
#include <pxr/arch/hints.h>
#include "pxr/tf/callContext.h"

#include <stddef.h>

TF_NAMESPACE_OPEN_SCOPE

/// \enum TfDiagnosticType
/// Enum describing various diagnostic conditions.
enum TfDiagnosticType : int {
    TF_DIAGNOSTIC_INVALID_TYPE = 0,
    TF_DIAGNOSTIC_CODING_ERROR_TYPE,
    TF_DIAGNOSTIC_FATAL_CODING_ERROR_TYPE,
    TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE,
    TF_DIAGNOSTIC_FATAL_ERROR_TYPE,
    TF_DIAGNOSTIC_NONFATAL_ERROR_TYPE,
    TF_DIAGNOSTIC_WARNING_TYPE,
    TF_DIAGNOSTIC_STATUS_TYPE,
    TF_APPLICATION_EXIT_TYPE,
};


#if !defined(doxygen)

struct Tf_DiagnosticLiteHelper {
    constexpr Tf_DiagnosticLiteHelper(TfCallContext const &context,
                                      TfDiagnosticType type)
        : _context(context),
          _type(type)
    {
    }
    
    TF_API void IssueError(
        char const *fmt, ...) const ARCH_PRINTF_FUNCTION(2,3);
    [[noreturn]]
    TF_API void IssueFatalError(
        char const *fmt, ...) const ARCH_PRINTF_FUNCTION(2,3);
    TF_API void IssueWarning(
        char const *fmt, ...) const ARCH_PRINTF_FUNCTION(2,3);
    TF_API void IssueStatus(
        char const *fmt, ...) const ARCH_PRINTF_FUNCTION(2,3);

private:
    TfCallContext _context;
    TfDiagnosticType _type;
};

#define TF_CODING_ERROR                                            \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_CODING_ERROR_TYPE).IssueError

#define TF_CODING_WARNING                                          \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_CODING_ERROR_TYPE).IssueWarning              \

#define TF_FATAL_CODING_ERROR                                      \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_CODING_ERROR_TYPE).IssueFatalError

#define TF_RUNTIME_ERROR                                           \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE).IssueError

#define TF_FATAL_ERROR                                             \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_FATAL_ERROR_TYPE).IssueFatalError

#define TF_DIAGNOSTIC_FATAL_ERROR                                  \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE).IssueFatalError

#define TF_DIAGNOSTIC_NONFATAL_ERROR                               \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_WARNING_TYPE).IssueWarning

#define TF_DIAGNOSTIC_WARNING                                      \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT.Hide(),         \
        TF_DIAGNOSTIC_WARNING_TYPE).IssueWarning

#define TF_WARN                                                    \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_WARNING_TYPE).IssueWarning

#define TF_STATUS                                                  \
    TF_NS::Tf_DiagnosticLiteHelper(TF_CALL_CONTEXT,                \
        TF_DIAGNOSTIC_STATUS_TYPE).IssueStatus

constexpr bool
Tf_AxiomHelper(bool val, TfCallContext const &ctx, char const *txt) {
    return (ARCH_LIKELY(val)) ? true :
        (Tf_DiagnosticLiteHelper(ctx, TF_DIAGNOSTIC_FATAL_ERROR_TYPE).
         IssueFatalError("Failed axiom: ' %s '", txt), false);
}

#define TF_AXIOM(cond)                                                  \
    TF_NS::Tf_AxiomHelper(static_cast<bool>((cond)), TF_CALL_CONTEXT, #cond)

#define TF_DEV_AXIOM(cond)                                              \
    TF_NS::Tf_AxiomHelper(!ARCH_DEV_BUILD ||                            \
                   static_cast<bool>((cond)), TF_CALL_CONTEXT, #cond)

#endif  // !defined(doxygen)

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_DIAGNOSTIC_LITE_H
