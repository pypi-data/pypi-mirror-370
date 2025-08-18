// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#define ADDITION_OPERATOR

#include <pxr/vt/pxr.h>
#include <pxr/vt/typeHeaders.h>
#include <pxr/vt/wrapArray.h>
#include <pxr/vt/wrapArrayEdit.h>
#include <pxr/tf/preprocessorUtilsLite.h>

VT_NAMESPACE_USING_DIRECTIVE

void wrapArrayRange() {
    TF_PP_SEQ_FOR_EACH(VT_WRAP_ARRAY, ~, VT_RANGE_VALUE_TYPES);
    TF_PP_SEQ_FOR_EACH(VT_WRAP_ARRAY_EDIT, ~, VT_RANGE_VALUE_TYPES);
}
