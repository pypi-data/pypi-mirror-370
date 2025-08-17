// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pySingleton.h"

#include <string>

using std::string;

TF_NAMESPACE_OPEN_SCOPE

namespace Tf_PySingleton {

bp::object _DummyInit(bp::tuple const & /* args */,
                      bp::dict const & /* kw */) {
    return bp::object();
}
    
string _Repr(bp::object const &self, string const &prefix) {
    string name(bp::extract<string>(self.attr("__class__").attr("__name__")));
    return prefix + name + "()";
}

}

Tf_PySingleton::Visitor TfPySingleton() {
    return Tf_PySingleton::Visitor();
}

TF_NAMESPACE_CLOSE_SCOPE
