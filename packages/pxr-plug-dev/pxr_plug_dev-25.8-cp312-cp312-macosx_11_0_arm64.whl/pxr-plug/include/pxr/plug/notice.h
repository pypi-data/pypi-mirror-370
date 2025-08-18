// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_PLUG_NOTICE_H
#define PXR_PLUG_NOTICE_H

#include "pxr/plug/pxr.h"
#include "pxr/plug/api.h"
#include <pxr/tf/declarePtrs.h>
#include <pxr/tf/notice.h>

PLUG_NAMESPACE_OPEN_SCOPE

TF_DECLARE_WEAK_PTRS(PlugPlugin);

/// \class PlugNotice
/// Notifications sent by the Plug library.
class PlugNotice
{
public:
    /// Base class for all Plug notices.
    class Base : public TfNotice
    {
    public:
        PLUG_API virtual ~Base();
    };

    /// Notice sent after new plugins have been registered with the Plug
    /// registry.
    class DidRegisterPlugins : public Base
    {
    public:
        explicit DidRegisterPlugins(const PlugPluginPtrVector& newPlugins);
        PLUG_API virtual ~DidRegisterPlugins();

        const PlugPluginPtrVector& GetNewPlugins() const
        { return _plugins; }

    private:
        PlugPluginPtrVector _plugins;
    };

private:
    PlugNotice();
};

PLUG_NAMESPACE_CLOSE_SCOPE

#endif // PXR_PLUG_NOTICE_H
