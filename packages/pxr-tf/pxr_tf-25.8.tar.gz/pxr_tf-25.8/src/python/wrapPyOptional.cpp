// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

///
/// \file tf/wrapOptional.cpp

#include <pxr/tf/pxr.h>
#include <pxr/tf/pyOptional.h>

#include <string>
#include <vector>

TF_NAMESPACE_USING_DIRECTIVE

void wrapPyOptional() {
    TfPyOptional::python_optional<std::string>();
    TfPyOptional::python_optional<std::vector<std::string> >();
    TfPyOptional::python_optional<double>();
    TfPyOptional::python_optional<float>();
    TfPyOptional::python_optional<long>();
    TfPyOptional::python_optional<unsigned long>();
    TfPyOptional::python_optional<int>();
    TfPyOptional::python_optional<unsigned int>();
    TfPyOptional::python_optional<short>();
    TfPyOptional::python_optional<unsigned short>();
    TfPyOptional::python_optional<char>();
    TfPyOptional::python_optional<unsigned char>();
    TfPyOptional::python_optional<bool>();
}
