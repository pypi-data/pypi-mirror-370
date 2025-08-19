// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/ar/pxr.h>
#include <pxr/ar/packageUtils.h>
#include <pxr/tf/pyResultConversions.h>

#include <pxr/boost/python/def.hpp>
#include <pxr/boost/python/return_value_policy.hpp>

AR_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void
wrapPackageUtils()
{
    def("IsPackageRelativePath", 
        &ArIsPackageRelativePath, arg("path"));

    def("JoinPackageRelativePath", 
        (std::string(*)(const std::vector<std::string>&))
            &ArJoinPackageRelativePath, 
        arg("paths"));

    def("JoinPackageRelativePath", 
        (std::string(*)(const std::pair<std::string, std::string>&))
            &ArJoinPackageRelativePath, 
        arg("paths"));

    def("JoinPackageRelativePath", 
        (std::string(*)(const std::string&, const std::string&))
            &ArJoinPackageRelativePath, 
        (arg("packagePath"), arg("packagedPath")));

    def("SplitPackageRelativePathOuter", 
        &ArSplitPackageRelativePathOuter, arg("path"));

    def("SplitPackageRelativePathInner", 
        &ArSplitPackageRelativePathInner, arg("path"));
}
