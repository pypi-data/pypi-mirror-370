// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"

#include "pxr/ar/packageResolver.h"

#include <pxr/tf/registryManager.h>
#include <pxr/tf/type.h>

AR_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfType)
{
    TfType::Define<ArPackageResolver>();
}

ArPackageResolver::ArPackageResolver()
{
}

ArPackageResolver::~ArPackageResolver()
{
}

AR_NAMESPACE_CLOSE_SCOPE
