// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/diagnostic.h>
#include <pxr/tf/pyEnum.h>

#include <pxr/boost/python/def.hpp>

TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapDiagnostic()
{
    TfPyWrapEnum<TfDiagnosticType>();

    def("InstallTerminateAndCrashHandlers",
        TfInstallTerminateAndCrashHandlers);

}
