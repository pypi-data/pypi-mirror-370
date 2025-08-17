// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/tf/weakPtr.h>
#include <pxr/tf/scriptModuleLoader.h>

#include <pxr/tf/pySingleton.h>
#include <pxr/tf/pyResultConversions.h>

#include <pxr/boost/python/class.hpp>

TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapScriptModuleLoader() {
    typedef TfScriptModuleLoader This;
    class_<This, TfWeakPtr<This>,
        noncopyable>("ScriptModuleLoader", no_init)
        .def(TfPySingleton())
        .def("GetModulesDict", &This::GetModulesDict)
        .def("WriteDotFile", &This::WriteDotFile)

        // For testing purposes only.
        .def("_RegisterLibrary", &This::RegisterLibrary)
        .def("_LoadModulesForLibrary", &This::LoadModulesForLibrary)
        ;
}
