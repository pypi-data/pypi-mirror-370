// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/stopwatch.h"

#include <ostream>


TF_NAMESPACE_OPEN_SCOPE


std::ostream &
operator<<(std::ostream& out, const TfStopwatch& s)
{
    return out << s.GetSeconds() << " seconds";
}

TF_NAMESPACE_CLOSE_SCOPE
