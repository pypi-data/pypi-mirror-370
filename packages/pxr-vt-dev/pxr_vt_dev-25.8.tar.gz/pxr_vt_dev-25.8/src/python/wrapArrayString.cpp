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

#include <string>
using std::string;

VT_NAMESPACE_USING_DIRECTIVE

void wrapArrayString() {
    VtWrapArray<VtArray<string> >();
    VtWrapArrayEdit<VtArrayEdit<string> >();
}
