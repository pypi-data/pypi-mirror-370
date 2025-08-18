// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/vt/pxr.h>
#include <pxr/vt/typeHeaders.h>
#include <pxr/vt/wrapArray.h>
#include <pxr/vt/wrapArrayEdit.h>

VT_NAMESPACE_USING_DIRECTIVE

void wrapArrayToken() {
    VtWrapArray<VtArray<TfToken> >();
    VtWrapArrayEdit<VtArrayEdit<TfToken> >();
}
