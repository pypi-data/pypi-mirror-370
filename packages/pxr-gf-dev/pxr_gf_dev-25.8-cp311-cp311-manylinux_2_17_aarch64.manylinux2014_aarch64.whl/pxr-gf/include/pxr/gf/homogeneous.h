// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_GF_HOMOGENEOUS_H
#define PXR_GF_HOMOGENEOUS_H

/// \file gf/homogeneous.h
/// \ingroup group_gf_LinearAlgebra
/// Utility functions for GfVec4f and GfVec4d as homogeneous vectors

#include "pxr/gf/pxr.h"
#include "pxr/gf/vec3d.h"
#include "pxr/gf/vec3f.h"
#include "pxr/gf/vec4d.h"
#include "pxr/gf/vec4f.h"
#include "pxr/gf/api.h"

GF_NAMESPACE_OPEN_SCOPE

/// Returns a vector which is \p v homogenized.  If the fourth element of \p v
/// is 0, it is set to 1.
/// \ingroup group_gf_LinearAlgebra
GF_API
GfVec4f GfGetHomogenized(const GfVec4f &v);

/// Homogenizes \p a and \p b and then performs the cross product on the first
/// three elements of each.  Returns the cross product as a homogenized
/// vector.
/// \ingroup group_gf_LinearAlgebra
GF_API
GfVec4f GfHomogeneousCross(const GfVec4f &a, const GfVec4f &b);

GF_API
GfVec4d GfGetHomogenized(const GfVec4d &v);

/// Homogenizes \p a and \p b and then performs the cross product on the first
/// three elements of each.  Returns the cross product as a homogenized
/// vector.
/// \ingroup group_gf_LinearAlgebra
GF_API
GfVec4d GfHomogeneousCross(const GfVec4d &a, const GfVec4d &b);

/// Projects homogeneous \p v into Euclidean space and returns the result as a
/// Vec3f.
inline GfVec3f GfProject(const GfVec4f &v) {
    float inv = (v[3] != 0.0f) ? 1.0f/v[3] : 1.0f;
    return GfVec3f(inv * v[0], inv * v[1], inv * v[2]);
}

/// Projects homogeneous \p v into Euclidean space and returns the result as a
/// Vec3d.
inline GfVec3d GfProject(const GfVec4d &v) {
    double inv = (v[3] != 0.0) ? 1.0/v[3] : 1.0;
    return GfVec3d(inv * v[0], inv * v[1], inv * v[2]);
}

GF_NAMESPACE_CLOSE_SCOPE

#endif /* PXR_GF_HOMOGENEOUS_H */
