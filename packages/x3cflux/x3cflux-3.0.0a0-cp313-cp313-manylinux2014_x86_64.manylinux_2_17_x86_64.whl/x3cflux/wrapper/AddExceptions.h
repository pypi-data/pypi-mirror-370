#ifndef X3CFLUX_ADDEXCEPTIONS_H
#define X3CFLUX_ADDEXCEPTIONS_H

#include <stdexcept>

#include <math/MathError.h>
#include <model/data/ParseError.h>
#include <model/parameter/ParameterError.h>
#include <pybind11/pybind11.h>
#include <util/AssertionError.h>

namespace py = pybind11;

void addExceptions(py::module &m) {
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p)
                std::rethrow_exception(p);
        } catch (const x3cflux::AssertionError &e) {
            py::set_error(PyExc_AssertionError, e.what());
        }
    });
    py::register_exception<x3cflux::MathError>(m, "MathError");
    py::register_exception<x3cflux::ParseError>(m, "ParseError");
    py::register_exception<x3cflux::ParameterError>(m, "ParameterError");
}

#endif // X3CFLUX_ADDEXCEPTIONS_H
