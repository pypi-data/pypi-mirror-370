// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"
#include "pxr/ar/assetInfo.h"

AR_NAMESPACE_OPEN_SCOPE

bool 
operator==(
    const ArAssetInfo& lhs, 
    const ArAssetInfo& rhs)
{
    return (lhs.version == rhs.version) 
        && (lhs.assetName == rhs.assetName)
        && (lhs.repoPath == rhs.repoPath)
        && (lhs.resolverInfo == rhs.resolverInfo);
}

bool 
operator!=(
    const ArAssetInfo& lhs, 
    const ArAssetInfo& rhs)
{
    return !(lhs == rhs);
}

AR_NAMESPACE_CLOSE_SCOPE
