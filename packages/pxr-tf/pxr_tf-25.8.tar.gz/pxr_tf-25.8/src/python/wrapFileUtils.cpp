// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/boost/python/def.hpp>

#include <pxr/tf/fileUtils.h>

#include <string>

using std::string;

TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapFileUtils() {

    def("TouchFile", &TfTouchFile, (arg("fileName"), arg("create")=bool(false)));
}
