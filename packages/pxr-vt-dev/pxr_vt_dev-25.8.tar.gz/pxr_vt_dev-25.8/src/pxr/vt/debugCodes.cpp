// Copyright 2025 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/vt/pxr.h"
#include "pxr/vt/debugCodes.h"
#include <pxr/tf/debug.h>
#include <pxr/tf/registryManager.h>

VT_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        VT_ARRAY_EDIT_BOUNDS, "VtArrayEdit operations out-of-bounds");
}

VT_NAMESPACE_CLOSE_SCOPE

