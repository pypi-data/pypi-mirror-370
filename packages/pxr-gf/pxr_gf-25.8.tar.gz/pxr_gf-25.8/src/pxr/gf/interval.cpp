// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/gf/pxr.h"
#include "pxr/gf/interval.h"
#include "pxr/gf/ostreamHelpers.h"
#include <pxr/tf/type.h>

#include <ostream>

GF_NAMESPACE_OPEN_SCOPE

// CODE_COVERAGE_OFF_GCOV_BUG  you know the drill.
TF_REGISTRY_FUNCTION(TfType) {
    TfType::Define<GfInterval>();
}
// CODE_COVERAGE_ON_GCOV_BUG

std::ostream &
operator<<(std::ostream &out, const GfInterval &i)
{
    out << (i.IsMinClosed() ? "[" : "(");
    out << Gf_OstreamHelperP(i.GetMin()) << ", ";
    out << Gf_OstreamHelperP(i.GetMax());
    out << (i.IsMaxClosed() ? "]" : ")");
    return out;
}

GF_NAMESPACE_CLOSE_SCOPE
