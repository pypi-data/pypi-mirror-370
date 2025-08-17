// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>
#include <pxr/tf/callContext.h>

#include <pxr/boost/python/class.hpp>

using std::string;
TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

namespace {

static string
_GetFileString(TfCallContext const& cc) {
    return string(cc.GetFile());
}

static string
_GetFunctionString(TfCallContext const& cc) {
    return string(cc.GetFunction());
}

static string
_GetPrettyFunctionString(TfCallContext const& cc) {
    return string(cc.GetPrettyFunction());
}

} // anonymous namespace 

void wrapCallContext() {
    typedef TfCallContext This;

    class_ <This> ("CallContext", no_init)
        .add_property("file", &_GetFileString)
        .add_property("function", &_GetFunctionString)
        .add_property("line", &This::GetLine)
        .add_property("prettyFunction", &_GetPrettyFunctionString)
    ;
}
