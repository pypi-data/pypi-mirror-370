// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_GF_OSTREAM_HELPERS_H
#define PXR_GF_OSTREAM_HELPERS_H

/// \file gf/ostreamHelpers.h
/// \ingroup group_gf_DebuggingOutput
///
/// Helpers for Gf stream operators.
///
/// These functions are useful to help with writing stream operators for
/// Gf types.  Please do not include this file in any header.

#include "pxr/gf/pxr.h"
#include <pxr/tf/stringUtils.h>

GF_NAMESPACE_OPEN_SCOPE

// Make the template class general so that we can use the same class
// (Gf_OstreamHelperP) on all variables and not worry about making a mistake
template <class T>
T Gf_OstreamHelperP(T v) { return v; }

inline TfStreamFloat Gf_OstreamHelperP(float v) { 
    return TfStreamFloat(v); 
}
inline TfStreamDouble Gf_OstreamHelperP(double v) { 
    return TfStreamDouble(v); 
}

GF_NAMESPACE_CLOSE_SCOPE

#endif // GF_OSTREAM_HELPERS 
