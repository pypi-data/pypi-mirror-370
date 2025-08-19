// Copyright 2018 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/boost/python/class.hpp>
#include <pxr/boost/python/operators.hpp>
#include <pxr/boost/python/return_by_value.hpp>
#include <pxr/boost/python/return_value_policy.hpp>

#include <pxr/ar/pxr.h>
#include <pxr/ar/defaultResolverContext.h>
#include <pxr/ar/pyResolverContext.h>
#include <pxr/tf/pyUtils.h>

AR_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

static std::string
_Repr(const ArDefaultResolverContext& ctx)
{
    std::string repr = TF_PY_REPR_PREFIX;
    repr += "DefaultResolverContext(";
    if (!ctx.GetSearchPath().empty()) {
        repr += TfPyRepr(ctx.GetSearchPath());
    }
    repr += ")";
    return repr;
}

static size_t
_Hash(const ArDefaultResolverContext& ctx)
{
    return hash_value(ctx);
}

void
wrapDefaultResolverContext()
{
    using This = ArDefaultResolverContext;

    class_<This>
        ("DefaultResolverContext", no_init)
        .def(init<>())
        .def(init<const std::vector<std::string>&>(
                arg("searchPaths")))

        .def(self == self)
        .def(self != self)

        .def("GetSearchPath", &This::GetSearchPath,
             return_value_policy<return_by_value>())

        .def("__str__", &This::GetAsString)
        .def("__repr__", &_Repr)
        .def("__hash__", &_Hash)
        ;

    ArWrapResolverContextForPython<This>();
}
