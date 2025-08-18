// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/plug/pxr.h"
#include "pxr/plug/notice.h"
#include <pxr/tf/type.h>
#include <pxr/tf/registryManager.h>

PLUG_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType)
{
    TfType::Define< PlugNotice::Base,
                    TfType::Bases<TfNotice> >();
    TfType::Define< PlugNotice::DidRegisterPlugins,
                    TfType::Bases<PlugNotice::Base> >();
}

////////////////////////////////////////////////////////////

PlugNotice::Base::~Base() 
{ 
}

////////////////////////////////////////////////////////////

PlugNotice::
DidRegisterPlugins::DidRegisterPlugins(const PlugPluginPtrVector& newPlugins)
    : _plugins(newPlugins)
{
}

PlugNotice::
DidRegisterPlugins::~DidRegisterPlugins()
{
}

PLUG_NAMESPACE_CLOSE_SCOPE
