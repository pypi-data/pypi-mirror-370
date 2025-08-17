// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/tf/pyModuleNotice.h>
#include <pxr/tf/pyNoticeWrapper.h>

#include <pxr/boost/python/return_by_value.hpp>
#include <pxr/boost/python/return_value_policy.hpp>

TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

namespace {

TF_INSTANTIATE_NOTICE_WRAPPER(TfPyModuleWasLoaded, TfNotice);

} // anonymous namespace 

void wrapPyModuleNotice() {

    TfPyNoticeWrapper<TfPyModuleWasLoaded, TfNotice>::Wrap("PyModuleWasLoaded")
        .def("name", make_function(&TfPyModuleWasLoaded::GetName,
                                   return_value_policy<return_by_value>()))
        ;
}
