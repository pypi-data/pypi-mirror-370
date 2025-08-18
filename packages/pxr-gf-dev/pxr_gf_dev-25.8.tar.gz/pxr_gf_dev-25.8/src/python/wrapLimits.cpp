// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/boost/python/scope.hpp>

#include <pxr/gf/pxr.h>
#include <pxr/gf/limits.h>

GF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapLimits()
{
    scope().attr("MIN_VECTOR_LENGTH") = GF_MIN_VECTOR_LENGTH;
    scope().attr("MIN_ORTHO_TOLERANCE") = GF_MIN_ORTHO_TOLERANCE;
}
