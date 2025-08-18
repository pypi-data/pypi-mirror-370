// Copyright 2024 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/ts/pxr.h>
#include <pxr/tf/pyModule.h>

TS_NAMESPACE_USING_DIRECTIVE

TF_WRAP_MODULE
{
    TF_WRAP(Types);
    TF_WRAP(Knot);
    TF_WRAP(KnotMap);
    TF_WRAP(Raii);
    TF_WRAP(RegressionPreventer);
    TF_WRAP(Spline);
    TF_WRAP(TangentConversions);
}
