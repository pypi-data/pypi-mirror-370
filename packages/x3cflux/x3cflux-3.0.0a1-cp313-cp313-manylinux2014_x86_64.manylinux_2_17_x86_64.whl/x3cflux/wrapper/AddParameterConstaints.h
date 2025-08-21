#ifndef X3CFLUX_ADDPARAMETERCONSTRAINTS_H
#define X3CFLUX_ADDPARAMETERCONSTRAINTS_H

#include <model/data/ParameterConstraints.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static void addParameterConstraints(py::module &m) {
    py::class_<x3cflux::DefinitionConstraint>(m, "DefinitionConstraint",
                                              "Constraint that defines the value of a parameter")
        .def(py::init<const std::string &, std::string, x3cflux::Real>(), py::arg("name"), py::arg("parameter_name"),
             py::arg("parameter_value"), "Creates definition constraint")
        .def_property_readonly("name", &x3cflux::DefinitionConstraint::getName, "Name of the constraint")
        .def_property_readonly("parameter_name", &x3cflux::DefinitionConstraint::getParameterName,
                               "Name of the parameter")
        .def_property_readonly("parameter_value", &x3cflux::DefinitionConstraint::getParameterValue,
                               "Value of the parameter")
        .def(py::pickle(
            [](const x3cflux::DefinitionConstraint &constraint) {
                return py::make_tuple(constraint.getName(), constraint.getParameterName(),
                                      constraint.getParameterValue());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::DefinitionConstraint(t[0].cast<std::string>(), t[1].cast<std::string>(),
                                                     t[2].cast<x3cflux::Real>());
            }));

    py::class_<x3cflux::LinearConstraint>(m, "LinearConstraint", R"doc(
            Constraint that evolves linear combinations of parameter

            Can be used for either linear equality or inequality constraints. The constant is on the left hand side
            of the equality/inequality.
            Equality constraint:
            .. math :: \sum_{i} c_i \cdot \text{parameter}_i = \text{constant}
            Inequality constraint:
            .. math :: \sum_{i} c_i \cdot \text{parameter}_i \le \text{constant}
            )doc")
        .def(py::init<const std::string &, std::vector<std::string>, std::vector<x3cflux::Real>, x3cflux::Real>(),
             py::arg("name"), py::arg("parameter_names"), py::arg("parameter_coefficients"), py::arg("constant"),
             "Creates linear constraint")
        .def_property_readonly("name", &x3cflux::LinearConstraint::getName, "Name of the constraint")
        .def_property_readonly("parameter_names", &x3cflux::LinearConstraint::getParameterNames,
                               "Names of the involved parameters")
        .def_property_readonly("parameter_coefficients", &x3cflux::LinearConstraint::getParameterCoefficients,
                               "Coefficients of the parameters")
        .def_property_readonly("constant", &x3cflux::LinearConstraint::getConstant, "LHS constant")
        .def(py::pickle(
            [](const x3cflux::LinearConstraint &constraint) {
                return py::make_tuple(constraint.getName(), constraint.getParameterNames(),
                                      constraint.getParameterCoefficients(), constraint.getConstant());
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");
                return x3cflux::LinearConstraint(t[0].cast<std::string>(), t[1].cast<std::vector<std::string>>(),
                                                 t[2].cast<std::vector<x3cflux::Real>>(), t[3].cast<x3cflux::Real>());
            }));

    py::class_<x3cflux::ParameterConstraints>(m, "ParameterConstraints", "Collection of all supported constraint types")
        .def(py::init<std::vector<x3cflux::DefinitionConstraint>, std::vector<x3cflux::LinearConstraint>,
                      std::vector<x3cflux::LinearConstraint>>(),
             py::arg("definition_constraints"), py::arg("equality_constraints"), py::arg("inequality_constraints"))
        .def_property_readonly("definition_constraints", &x3cflux::ParameterConstraints::getDefinitionConstraints,
                               "parameter defining constraints")
        .def_property_readonly("equality_constraints", &x3cflux::ParameterConstraints::getEqualityConstraints,
                               "linear equality constraints")
        .def_property_readonly("inequality_constraints", &x3cflux::ParameterConstraints::getInequalityConstraints,
                               "linear inequality constraints")
        .def(py::pickle(
            [](const x3cflux::ParameterConstraints &constraints) {
                return py::make_tuple(constraints.getDefinitionConstraints(), constraints.getEqualityConstraints(),
                                      constraints.getInequalityConstraints());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::ParameterConstraints(t[0].cast<std::vector<x3cflux::DefinitionConstraint>>(),
                                                     t[1].cast<std::vector<x3cflux::LinearConstraint>>(),
                                                     t[2].cast<std::vector<x3cflux::LinearConstraint>>());
            }));
}

#endif // X3CFLUX_ADDPARAMETERCONSTRAINTS_H