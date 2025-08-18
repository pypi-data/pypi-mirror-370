// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_GF_PY_BUFFER_UTILS_H
#define PXR_GF_PY_BUFFER_UTILS_H

#include "pxr/gf/pxr.h"
#include "pxr/gf/api.h"

GF_NAMESPACE_OPEN_SCOPE

////////////////////////////////////////////////////////////////////////
// Format strings matching Python buffer proto / struct module scheme.

// This function template is explicitly instantiated for T =
//    bool, [unsigned] (char, short, int, long), half, float, and double.
template <class T>
char *Gf_GetPyBufferFmtFor();

GF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_GF_PY_BUFFER_UTILS_H
