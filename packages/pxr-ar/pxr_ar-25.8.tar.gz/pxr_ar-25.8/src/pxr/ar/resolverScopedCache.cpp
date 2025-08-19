// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"
#include "pxr/ar/resolverScopedCache.h"
#include "pxr/ar/resolver.h"

AR_NAMESPACE_OPEN_SCOPE

ArResolverScopedCache::ArResolverScopedCache()
{
    ArGetResolver().BeginCacheScope(&_cacheScopeData);
}

ArResolverScopedCache::ArResolverScopedCache(const ArResolverScopedCache* parent)
    : _cacheScopeData(parent->_cacheScopeData)
{
    ArGetResolver().BeginCacheScope(&_cacheScopeData);
}

ArResolverScopedCache::~ArResolverScopedCache()
{
    ArGetResolver().EndCacheScope(&_cacheScopeData);
}

AR_NAMESPACE_CLOSE_SCOPE
