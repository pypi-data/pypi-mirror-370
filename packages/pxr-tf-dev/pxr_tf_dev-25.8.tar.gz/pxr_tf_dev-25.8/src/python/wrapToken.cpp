// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/tf/token.h>

#include <pxr/tf/pyContainerConversions.h>
#include <pxr/tf/pyOptional.h>

#include <pxr/boost/python/def.hpp>
#include <pxr/boost/python/to_python_converter.hpp>
#include <pxr/boost/python/str.hpp>
#include <pxr/boost/python/object.hpp>

#include <set>
#include <string>
#include <utility>

TF_NAMESPACE_USING_DIRECTIVE

namespace bp = pxr_boost::python;

TF_NAMESPACE_OPEN_SCOPE

void TfDumpTokenStats(); // Defined in token.cpp.

TF_NAMESPACE_CLOSE_SCOPE

namespace {

struct Tf_TokenFromPythonString
{
    Tf_TokenFromPythonString() {
        bp::converter::registry::insert
            (&convertible, &construct, bp::type_id<TfToken>());
    }
    static void *convertible(PyObject *obj) {
        bp::extract<std::string> s(obj);
        return s.check() ? obj : 0;
    }
    static void construct(PyObject *src,
                          bp::converter::rvalue_from_python_stage1_data *data) {
        bp::extract<std::string> s(src);
        void *storage =
            ((bp::converter::
              rvalue_from_python_storage<TfToken> *)data)->storage.bytes;
        new (storage) TfToken( s() );
        data->convertible = storage;
    }
};

struct Tf_TokenToPythonString {
    static PyObject* convert(TfToken const &val) {
        return bp::incref(bp::str(val.GetString()).ptr());
    }
};

} // anonymous namespace 

void wrapToken()
{    
    TfPyContainerConversions::from_python_sequence<
        std::set<TfToken> , 
        TfPyContainerConversions::set_policy >();
    bp::to_python_converter<
        std::set<TfToken>, 
        TfPySequenceToPythonSet<std::set<TfToken> > >();

    TfPyContainerConversions::from_python_sequence<
        std::vector<TfToken>,
        TfPyContainerConversions::variable_capacity_policy >();
    bp::to_python_converter<
        std::vector<TfToken>, 
        TfPySequenceToPython<std::vector<TfToken> > >();

    // Tokens are represented directly as Python strings in Python.
    Tf_TokenFromPythonString();
    bp::to_python_converter<TfToken, Tf_TokenToPythonString>();

    TfPyContainerConversions::from_python_tuple_pair<
        std::pair<TfToken, TfToken>>();
    bp::to_python_converter<
        std::pair<TfToken, TfToken>,
        TfPyContainerConversions::to_tuple<std::pair<TfToken, TfToken>>>();

    TfPyOptional::python_optional<TfToken>();

    // Stats.
    bp::def("DumpTokenStats", TfDumpTokenStats);
}
