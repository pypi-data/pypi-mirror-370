// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/kind/pxr.h>
#include <pxr/kind/registry.h>
#include <pxr/tf/pyResultConversions.h>
#include <pxr/tf/pySingleton.h>

#include <pxr/boost/python.hpp>

KIND_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void wrapRegistry()
{
    typedef KindRegistry This;
    typedef TfWeakPtr<KindRegistry> ThisPtr;

   class_<This, ThisPtr, noncopyable>("Registry", no_init)
        .def(TfPySingleton())
        .def("HasKind", &This::HasKind)
        .staticmethod("HasKind")
        .def("GetAllKinds", &This::GetAllKinds,
             return_value_policy<TfPySequenceToList>())
        .staticmethod("GetAllKinds")
        .def("GetBaseKind", &This::GetBaseKind)
        .staticmethod("GetBaseKind")
        .def("IsA", &This::IsA)
        .def("IsModel", &This::IsModel)
        .def("IsGroup", &This::IsGroup)
        .def("IsAssembly", &This::IsAssembly)
        .def("IsComponent", &This::IsComponent)
        .def("IsSubComponent", &This::IsSubComponent)
        .staticmethod("IsA")
        ;
}
