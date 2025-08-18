// Copyright 2024 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TS_DEBUG_CODES_H
#define PXR_TS_DEBUG_CODES_H

#include "pxr/ts/pxr.h"
#include <pxr/tf/debug.h>

TS_NAMESPACE_OPEN_SCOPE


TF_CONDITIONALLY_COMPILE_TIME_ENABLED_DEBUG_CODES(
    false,
    TS_DEBUG_LOOPS,
    TS_DEBUG_SAMPLE
);


TS_NAMESPACE_CLOSE_SCOPE

#endif
