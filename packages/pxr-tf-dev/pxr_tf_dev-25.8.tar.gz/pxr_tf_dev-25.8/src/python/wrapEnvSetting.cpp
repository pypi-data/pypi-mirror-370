// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <locale>

#include <pxr/boost/python/def.hpp>
#include <pxr/boost/python/object.hpp>

#include <string>
#include <variant>

#include <pxr/tf/envSetting.h>

TF_NAMESPACE_OPEN_SCOPE

extern std::variant<int, bool, std::string> const *
Tf_GetEnvSettingByName(std::string const&);

static pxr_boost::python::object
_GetEnvSettingByName(std::string const& name) {
    std::variant<int, bool, std::string> const *
        variantValue = Tf_GetEnvSettingByName(name);

    if (!variantValue) {
        return pxr_boost::python::object();
    } 

    if (std::string const *value = std::get_if<std::string>(variantValue)) {
        return pxr_boost::python::object(*value); 
    } else if (bool const *value = std::get_if<bool>(variantValue)) {
        return pxr_boost::python::object(*value); 
    } else if (int const *value = std::get_if<int>(variantValue)) {
        return pxr_boost::python::object(*value); 
    } 
            
    return pxr_boost::python::object();
}

TF_NAMESPACE_CLOSE_SCOPE

TF_NAMESPACE_USING_DIRECTIVE

void wrapEnvSetting() {
    def("GetEnvSetting", &_GetEnvSettingByName);
}
