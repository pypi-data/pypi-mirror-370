// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_PLUG_DEBUG_CODES_H
#define PXR_PLUG_DEBUG_CODES_H

#include "pxr/plug/pxr.h"
#include <pxr/tf/debug.h>

PLUG_NAMESPACE_OPEN_SCOPE

TF_DEBUG_CODES(

    PLUG_LOAD,
    PLUG_REGISTRATION,
    PLUG_LOAD_IN_SECONDARY_THREAD,
    PLUG_INFO_SEARCH

);

PLUG_NAMESPACE_CLOSE_SCOPE

#endif // PXR_PLUG_DEBUG_CODES_H
