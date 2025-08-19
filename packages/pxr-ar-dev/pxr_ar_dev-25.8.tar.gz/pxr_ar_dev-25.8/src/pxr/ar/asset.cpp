// Copyright 2021 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/ar/pxr.h"
#include "pxr/ar/asset.h"
#include "pxr/ar/inMemoryAsset.h"

AR_NAMESPACE_OPEN_SCOPE

ArAsset::ArAsset()
{
}

ArAsset::~ArAsset()
{
}

std::shared_ptr<ArAsset>
ArAsset::GetDetachedAsset() const
{
    return ArInMemoryAsset::FromAsset(*this);
}

AR_NAMESPACE_CLOSE_SCOPE
