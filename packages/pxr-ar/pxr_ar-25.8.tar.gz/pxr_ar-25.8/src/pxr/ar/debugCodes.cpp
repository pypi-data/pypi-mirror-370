// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"
#include "pxr/ar/debugCodes.h"

#include <pxr/tf/registryManager.h>

AR_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(
        AR_RESOLVER_INIT, 
        "Print debug output during asset resolver initialization");
}

AR_NAMESPACE_CLOSE_SCOPE
