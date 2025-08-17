// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/tf/stopwatch.h>

#include <pxr/boost/python/class.hpp>


TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapStopwatch() {

    typedef TfStopwatch This;

    class_<This>("Stopwatch")

        .def("Start", &This::Start)
        .def("Stop", &This::Stop)
        .def("Reset", &This::Reset)
        .def("AddFrom", &This::AddFrom)

        .add_property("nanoseconds", &This::GetNanoseconds)
        .add_property("microseconds", &This::GetMicroseconds)
        .add_property("milliseconds", &This::GetMilliseconds)
        .add_property("sampleCount", &This::GetSampleCount)
        .add_property("seconds", &This::GetSeconds)
        ;
}
