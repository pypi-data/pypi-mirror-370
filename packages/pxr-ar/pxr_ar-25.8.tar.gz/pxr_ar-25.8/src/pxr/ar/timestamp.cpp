// Copyright 2021 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"

#include "pxr/ar/timestamp.h"
#include <pxr/tf/diagnostic.h>

AR_NAMESPACE_OPEN_SCOPE

void
ArTimestamp::_IssueInvalidGetTimeError() const
{
    TF_CODING_ERROR("Cannot call GetTime on an invalid ArTimestamp");
}

AR_NAMESPACE_CLOSE_SCOPE
