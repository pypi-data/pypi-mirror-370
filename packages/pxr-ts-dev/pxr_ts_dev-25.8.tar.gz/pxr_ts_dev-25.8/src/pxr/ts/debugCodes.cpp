// Copyright 2024 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ts/pxr.h"
#include "pxr/ts/debugCodes.h"
#include <pxr/tf/registryManager.h>

TS_NAMESPACE_OPEN_SCOPE


TF_REGISTRY_FUNCTION(TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        TS_DEBUG_LOOPS,
        "Diagnostic output for looping splines");
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        TS_DEBUG_SAMPLE,
        "Diagnostic output for sampling splines");
}


TS_NAMESPACE_CLOSE_SCOPE
