// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/gf/half.h"
#include <pxr/tf/registryManager.h>
#include <pxr/tf/type.h>

GF_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType) {
    TfType::Define<GfHalf>();
}

GF_NAMESPACE_CLOSE_SCOPE
