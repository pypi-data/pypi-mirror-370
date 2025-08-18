// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/kind/pxr.h>
#include <pxr/kind/registry.h>
#include <pxr/tf/pyStaticTokens.h>

KIND_NAMESPACE_USING_DIRECTIVE

void wrapTokens()
{
    TF_PY_WRAP_PUBLIC_TOKENS("Tokens", KindTokens,
                             KIND_TOKENS);
}
