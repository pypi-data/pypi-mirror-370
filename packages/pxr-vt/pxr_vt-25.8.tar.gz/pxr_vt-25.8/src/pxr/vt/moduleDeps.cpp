// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.
////////////////////////////////////////////////////////////////////////

#include "pxr/vt/pxr.h"
#include "pxr/tf/registryManager.h"
#include "pxr/tf/scriptModuleLoader.h"
#include "pxr/tf/token.h"

#include <vector>

VT_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfScriptModuleLoader) {
    // List of direct dependencies for this library.
    const std::vector<TfToken> reqs = {
        TfToken("arch"),
        TfToken("gf"),
        TfToken("tf"),
        TfToken("trace")
    };
    TfScriptModuleLoader::GetInstance().
        RegisterLibrary(TfToken("vt"), TfToken("pxr.Vt"), reqs);
}

VT_NAMESPACE_CLOSE_SCOPE
