// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyWrapContext.h"
#include "pxr/tf/diagnosticLite.h"
#include "pxr/tf/instantiateSingleton.h"

TF_NAMESPACE_OPEN_SCOPE

TF_INSTANTIATE_SINGLETON(Tf_PyWrapContextManager);

Tf_PyWrapContextManager::Tf_PyWrapContextManager()
{
    // initialize the stack of context names
    _contextStack.clear();
}

TF_NAMESPACE_CLOSE_SCOPE
