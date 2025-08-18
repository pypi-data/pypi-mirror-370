// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/plug/pxr.h>
#include <pxr/tf/pyModule.h>

PLUG_NAMESPACE_USING_DIRECTIVE

TF_WRAP_MODULE
{
    TF_WRAP( Notice );
    TF_WRAP( Plugin );    
    TF_WRAP( Registry );
}
