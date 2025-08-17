// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyObjectFinder.h"
#include "pxr/tf/pyUtils.h"
#include "pxr/tf/staticData.h"
#include "pxr/tf/typeInfoMap.h"

using std::type_info;

TF_NAMESPACE_OPEN_SCOPE

using namespace pxr_boost::python;

static TfStaticData<TfTypeInfoMap<Tf_PyObjectFinderBase const *> > _finders;


void Tf_RegisterPythonObjectFinderInternal(std::type_info const &type,
                                           Tf_PyObjectFinderBase const *finder) {
    _finders->Set(type, finder);
}

object Tf_FindPythonObject(void const *objPtr, std::type_info const &type) {
    Tf_PyObjectFinderBase const *finder = 0;
    if (Tf_PyObjectFinderBase const **x = _finders->Find(type))
        finder = *x;
    if (finder)
        return finder->Find(objPtr);
    return object();
}
    

Tf_PyObjectFinderBase::~Tf_PyObjectFinderBase() {}

TF_NAMESPACE_CLOSE_SCOPE
