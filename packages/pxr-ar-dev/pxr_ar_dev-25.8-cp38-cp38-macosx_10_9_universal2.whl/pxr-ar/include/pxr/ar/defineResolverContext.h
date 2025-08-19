// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_AR_DEFINE_RESOLVER_CONTEXT_H
#define PXR_AR_DEFINE_RESOLVER_CONTEXT_H

#include "pxr/ar/pxr.h"
#include "pxr/ar/api.h"
#include "pxr/ar/resolverContext.h"

/// \file ar/defineResolverContext.h
/// Macros for defining an object for use with ArResolverContext

AR_NAMESPACE_OPEN_SCOPE

/// \def AR_DECLARE_RESOLVER_CONTEXT
///
/// Declare that the specified ContextObject type may be used as an asset
/// resolver context object for ArResolverContext. This typically
/// would be invoked in the header where the ContextObject is
/// declared.
///
#ifdef doxygen
#define AR_DECLARE_RESOLVER_CONTEXT(ContextObject)
#else
#define AR_DECLARE_RESOLVER_CONTEXT(context)           \
template <>                                            \
struct ArIsContextObject<context>                      \
{                                                      \
    static const bool value = true;                    \
}
#endif

AR_NAMESPACE_CLOSE_SCOPE

#endif // PXR_AR_DEFINE_RESOLVER_CONTEXT_H
