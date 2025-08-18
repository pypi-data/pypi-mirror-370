// Copyright 2025 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/vt/pxr.h"
#include "pxr/vt/arrayEdit.h"
#include "pxr/vt/typeHeaders.h"
#include <pxr/tf/preprocessorUtilsLite.h>

VT_NAMESPACE_OPEN_SCOPE

// Instantiate basic ArrayEdit templates.
#define VT_ARRAY_EDIT_EXPLICIT_INST(unused, elem) \
    template class VT_API VtArrayEdit< VT_TYPE(elem) >;
TF_PP_SEQ_FOR_EACH(VT_ARRAY_EDIT_EXPLICIT_INST, ~, VT_SCALAR_VALUE_TYPES)
#undef VT_ARRAY_EDIT_EXPLICIT_INST
    
VT_NAMESPACE_CLOSE_SCOPE
