// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/vt/pxr.h"
#include "pxr/vt/array.h"
#include "pxr/vt/typeHeaders.h"
#include <pxr/tf/envSetting.h>
#include <pxr/tf/preprocessorUtilsLite.h>
#include <pxr/tf/stackTrace.h>
#include <pxr/tf/stringUtils.h>

VT_NAMESPACE_OPEN_SCOPE

TF_DEFINE_ENV_SETTING(
    VT_LOG_STACK_ON_ARRAY_DETACH_COPY, false,
    "Log a stack trace when a VtArray is copied to detach it from shared "
    "storage, to help track down unintended copies.");

void
Vt_ArrayBase::_DetachCopyHook(char const *funcName) const
{
    static bool log = TfGetEnvSetting(VT_LOG_STACK_ON_ARRAY_DETACH_COPY);
    if (ARCH_UNLIKELY(log)) {
        TfLogStackTrace(TfStringPrintf("Detach/copy VtArray (%s)", funcName));
    }
}

// Instantiate basic array templates.
#define VT_ARRAY_EXPLICIT_INST(unused, elem) \
    template class VT_API VtArray< VT_TYPE(elem) >;
TF_PP_SEQ_FOR_EACH(VT_ARRAY_EXPLICIT_INST, ~, VT_SCALAR_VALUE_TYPES)


VT_NAMESPACE_CLOSE_SCOPE
