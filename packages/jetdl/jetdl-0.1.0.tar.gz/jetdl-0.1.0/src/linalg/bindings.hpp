#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace linalg {
    void bind_submodule(py::module_& m);
}