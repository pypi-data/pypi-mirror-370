// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.
////////////////////////////////////////////////////////////////////////

#include "pxr/tf/pxr.h"
#include "pxr/tf/registryManager.h"
#include "pxr/tf/scriptModuleLoader.h"
#include "pxr/tf/token.h"

#include <vector>

namespace pxr {

TF_REGISTRY_FUNCTION(TfScriptModuleLoader) {
    // List of direct dependencies for this library.
    const std::vector<TfToken> reqs = {
        TfToken("arch"),
        TfToken("boost-python"),
    };
    TfScriptModuleLoader::GetInstance().
    RegisterLibrary(TfToken("tf"), TfToken("pxr.Tf"), reqs);
}

}  // namespace pxr
