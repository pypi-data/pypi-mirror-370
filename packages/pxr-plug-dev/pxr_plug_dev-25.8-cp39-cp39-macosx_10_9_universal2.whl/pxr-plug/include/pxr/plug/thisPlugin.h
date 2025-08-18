// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_PLUG_THIS_PLUGIN_H
#define PXR_PLUG_THIS_PLUGIN_H

#include "pxr/plug/pxr.h"
#include "pxr/plug/registry.h"
#include <pxr/tf/preprocessorUtilsLite.h>

PLUG_NAMESPACE_OPEN_SCOPE

/// The name of the current library registered with the plugin system. This
/// may be used to lookup the current library in the plugin registry.
/// This uses the value of the MFB_PACKAGE_NAME macro defined at compile-time
/// unless overridden.
#ifndef PLUG_THIS_PLUGIN_NAME
#define PLUG_THIS_PLUGIN_NAME MFB_PACKAGE_NAME
#endif

/// Returns a plugin registered with the name of the current library (as
/// defined by PLUG_THIS_PLUGIN_NAME). Note that plugin registration occurs as a
/// side effect of using this macro, at the point in time the code at the
/// macro site is invoked.
#define PLUG_THIS_PLUGIN \
    PlugRegistry::GetInstance().GetPluginWithName(\
        TF_PP_STRINGIZE(PLUG_THIS_PLUGIN_NAME))

PLUG_NAMESPACE_CLOSE_SCOPE

#endif // PXR_PLUG_THIS_PLUGIN_H
