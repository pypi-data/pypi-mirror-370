// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_PY_OPTIONAL_H
#define PXR_TF_PY_OPTIONAL_H

/// \file tf/pyOptional.h

#include "pxr/tf/pxr.h"

#include "pxr/tf/pyUtils.h"
#include <pxr/boost/python/converter/from_python.hpp>
#include <pxr/boost/python/extract.hpp>
#include <pxr/boost/python/to_python_converter.hpp>
#include <pxr/boost/python/to_python_value.hpp>

#include <optional>

TF_NAMESPACE_OPEN_SCOPE

// Adapted from original at:
// http://mail.python.org/pipermail/cplusplus-sig/2007-May/012003.html

namespace TfPyOptional {

template <typename T, typename TfromPy>
struct object_from_python
{
    object_from_python() {
        pxr_boost::python::converter::registry::push_back
        (&TfromPy::convertible, &TfromPy::construct,
         pxr_boost::python::type_id<T>());
    }
};

template <typename T, typename TtoPy, typename TfromPy>
struct register_python_conversion
{
    register_python_conversion() {
        pxr_boost::python::to_python_converter<T, TtoPy>();
        object_from_python<T, TfromPy>();
    }
};

template <typename T>
struct python_optional
{
    python_optional(const python_optional&) = delete;
    python_optional& operator=(const python_optional&) = delete;
    template <typename Optional>
    struct optional_to_python
    {
        static PyObject * convert(const Optional& value)
        {
            if (value) {
                pxr_boost::python::object obj = TfPyObject(*value);
                Py_INCREF(obj.ptr());
                return obj.ptr();
            }
            return pxr_boost::python::detail::none();
        }
    };

    template <typename Optional>
    struct optional_from_python
    {
        static void * convertible(PyObject * source)
        {
            using namespace pxr_boost::python::converter;

            if ((source == Py_None) || pxr_boost::python::extract<T>(source).check())
                return source;

            return NULL;
        }

        static void construct(PyObject * source,
                              pxr_boost::python::converter::rvalue_from_python_stage1_data * data)
        {
            using namespace pxr_boost::python::converter;

            void * const storage =
                ((rvalue_from_python_storage<T> *)data)->storage.bytes;

            if (data->convertible == Py_None) {
                new (storage) Optional(); // An uninitialized optional
            } else {
                new (storage) Optional(pxr_boost::python::extract<T>(source));
            }

            data->convertible = storage;
        }
    };

    explicit python_optional() {
        register_python_conversion<
            std::optional<T>,
            optional_to_python<std::optional<T>>, 
            optional_from_python<std::optional<T>>>();
    }
};

} // namespace TfPyOptional

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_PY_OPTIONAL_H
