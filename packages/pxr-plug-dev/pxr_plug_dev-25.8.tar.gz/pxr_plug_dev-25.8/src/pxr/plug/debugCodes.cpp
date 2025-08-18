// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/plug/pxr.h"
#include "pxr/plug/debugCodes.h"
#include <pxr/tf/debug.h>
#include <pxr/tf/registryManager.h>

PLUG_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_LOAD, "Plugin loading");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_REGISTRATION, "Plugin registration");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_LOAD_IN_SECONDARY_THREAD,
                                "Plugins loaded from non-main threads");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PLUG_INFO_SEARCH, "Plugin info file search");
}

PLUG_NAMESPACE_CLOSE_SCOPE
