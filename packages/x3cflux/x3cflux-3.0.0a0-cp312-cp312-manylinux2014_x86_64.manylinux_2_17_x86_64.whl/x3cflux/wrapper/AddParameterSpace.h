#ifndef X3CFLUX_ADDPARAMETERSPACE_H
#define X3CFLUX_ADDPARAMETERSPACE_H

#include <model/parameter/ParameterSpaceAdapter.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

template <bool Stationary> void addParameterSpaceAdapter(py::module &m) {
    typedef x3cflux::ParameterSpaceAdapter<Stationary> ParameterSpace;

    auto name = std::string(Stationary ? "Stationary" : "NonStationary") + "ParameterSpace";

    py::class_<ParameterSpace> psDecl(
        m, name.c_str(),
        ("Parameter space for " + std::string(Stationary ? "isotopically stationary" : "isotopically non-stationary") +
         " 13C-MFA")
            .c_str());
    psDecl
        .def_property("constraint_violation_tolerance", &ParameterSpace::getConstraintViolationTolerance,
                      &ParameterSpace::setConstraintViolationTolerance)
        .def_property_readonly("num_free_parameters", &ParameterSpace::getNumFreeParameters)
        .def_property_readonly("num_parameters", &ParameterSpace::getNumParameters)
        .def_property_readonly("free_parameter_names", &ParameterSpace::getFreeParameterNames)
        .def_property_readonly("parameter_names", &ParameterSpace::getParameterNames)
        .def_property_readonly("stoichiometry", &ParameterSpace::getStoichiometry, "Stoichiometry of the network model")
        .def_property_readonly("net_flux_solution_space", &ParameterSpace::getNetFluxSolutionSpace,
                               "Reduced net flux space")
        .def_property_readonly("net_flux_classification", &ParameterSpace::getNetFluxClassification,
                               "Information on net flux parameters")
        .def_property_readonly("exchange_flux_solution_space", &ParameterSpace::getExchangeFluxSolutionSpace,
                               "Reduced exchange flux space")
        .def_property_readonly("exchange_flux_classification", &ParameterSpace::getExchangeFluxClassification,
                               "Information on exchange flux parameters")
        .def_property_readonly("inequality_system", &ParameterSpace::getInequalitySystem,
                               "System of linear inequality constraints in terms of free parameters")
        .def("compute_parameters", &ParameterSpace::computeParameters, py::arg("params"), R"doc(
            Compute all metabolic parameters from free parameters

            :param np.ndarray params:
                free parameter vector

            :return:
                full parameter vector
            )doc")
        .def("contains", &ParameterSpace::contains, py::arg("params"))
        .def("compute_stoichiometry_error", &ParameterSpace::computeStoichiometryError, py::arg("params"))
        .def("is_feasible", &ParameterSpace::isFeasible, py::arg("params"),
             py::arg("tol") = std::numeric_limits<x3cflux::Real>::epsilon())
        .def(py::pickle(
            [](const ParameterSpace &paramSpace) {
                return py::make_tuple(paramSpace.getStoichiometry(), paramSpace.getNetFluxSolutionSpace(),
                                      paramSpace.getExchangeFluxSolutionSpace(), paramSpace.getPoolSizeSolutionSpace(),
                                      paramSpace.getNetFluxClassification(), paramSpace.getExchangeFluxClassification(),
                                      paramSpace.getPoolSizeClassification(), paramSpace.getNetFluxInequalitySystem(),
                                      paramSpace.getExchangeFluxInequalitySystem(),
                                      paramSpace.getPoolSizeInequalitySystem(),
                                      paramSpace.getConstraintViolationTolerance());
            },
            [](py::tuple t) {
                if (t.size() != 11)
                    throw std::runtime_error("Invalid state");
                return ParameterSpace(
                    x3cflux::ParameterSpace(
                        t[0].cast<x3cflux::Stoichiometry>(), t[1].cast<x3cflux::SolutionSpace>(),
                        t[2].cast<x3cflux::SolutionSpace>(), t[3].cast<x3cflux::SolutionSpace>(),
                        t[4].cast<x3cflux::ParameterClassification>(), t[5].cast<x3cflux::ParameterClassification>(),
                        t[6].cast<x3cflux::ParameterClassification>(), t[7].cast<x3cflux::InequalitySystem>(),
                        t[8].cast<x3cflux::InequalitySystem>(), t[9].cast<x3cflux::InequalitySystem>()),
                    t[10].cast<x3cflux::Real>());
            }));

    if (not Stationary) {
        psDecl
            .def_property_readonly("pool_size_solution_space", &ParameterSpace::getPoolSizeSolutionSpace,
                                   "Reduced pool size space")
            .def_property_readonly("pool_size_classification", &ParameterSpace::getPoolSizeClassification,
                                   "Information on pool size parameters");
    }
}

static void addParameterSpace(py::module &m) {
    py::class_<x3cflux::Stoichiometry>(m, "Stoichiometry", R"doc(
            Steady-state stoichiometric equations

            Given by
            .. math :: \mathbf{S} \cdot \mathbf{\theta} = \mathbf{0}
            )doc")
        .def_property_readonly("matrix", &x3cflux::Stoichiometry::getStoichiometricMatrix, "Stoichiometric matrix")
        .def_property_readonly("metabolite_names", &x3cflux::Stoichiometry::getMetaboliteNames, "Names of metabolites")
        .def_property_readonly("reaction_names", &x3cflux::Stoichiometry::getReactionNames, "Names of reactions")
        .def(py::pickle(
            [](const x3cflux::Stoichiometry &stoichiometry) {
                return py::make_tuple(stoichiometry.getStoichiometricMatrix(), stoichiometry.getMetaboliteNames(),
                                      stoichiometry.getReactionNames());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::Stoichiometry(t[0].cast<x3cflux::IntegerMatrix>(),
                                              t[1].cast<std::vector<std::string>>(),
                                              t[2].cast<std::vector<std::string>>());
            }));

    py::class_<x3cflux::InequalitySystem>(m, "InequalitySystem", R"doc(
            System of linear inequality constraints

            Given by
            .. math \mathbf{C}_\text{ineq} \cdot \mathbf{\theta} = \mathbf{d}_\text{ineq}
            Each row of the inequality defines a half space whose intersections defines the
            solution space of the constraints, a (possibly not bounded) polytope.
            )doc")
        .def_property_readonly("matrix", &x3cflux::InequalitySystem::getMatrix,
                               "Linear coefficients of the constraints")
        .def_property_readonly("bound", &x3cflux::InequalitySystem::getBound, "Upper bounds of the constraints")
        .def(py::pickle(
            [](const x3cflux::InequalitySystem &ineqSystem) {
                return py::make_tuple(ineqSystem.getMatrix(), ineqSystem.getBound());
            },
            [](py::tuple t) {
                if (t.size() != 2)
                    throw std::runtime_error("Invalid state");
                return x3cflux::InequalitySystem(t[0].cast<x3cflux::RealMatrix>(), t[1].cast<x3cflux::RealVector>());
            }));

    py::class_<x3cflux::SolutionSpace>(m, "SolutionSpace", "Space defined by the solution of a linear equation system")
        .def("particular_solution", &x3cflux::SolutionSpace::getParticularSolution,
             "Particular solution of the equation")
        .def("kernel_basis", &x3cflux::SolutionSpace::getKernelBasis, "Basis of the kernel space")
        .def("permutation",
             [](const x3cflux::SolutionSpace &s) -> x3cflux::Matrix<int> {
                 return s.getPermutation().indices().matrix();
             })
        .def(py::pickle(
            [](const x3cflux::SolutionSpace &solutionSpace) {
                auto indices = solutionSpace.getPermutation().indices().array();
                return py::make_tuple(solutionSpace.getParticularSolution(), solutionSpace.getKernelBasis(),
                                      std::vector<int>{indices.data(), indices.data() + indices.size()});
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::SolutionSpace(t[0].cast<x3cflux::RealVector>(), t[1].cast<x3cflux::RealMatrix>(),
                                              x3cflux::PermutationMatrix(t[2].cast<x3cflux::Matrix<int>>()));
            }));

    py::class_<x3cflux::ParameterClassification>(m, "ParameterClassification", R"doc(
            Information on a set of parameter subjected to equality constraints

            This object is used to summarize the effects of equality on each type of parameters (netto, exchange, pool size). A full list
            of parameter names is provided as an attribute and referenced by the other attributes using indices. Generally, parameters divide into
            free, dependent and constrained parameters. Quasi-constrained parameters are dependent parameters that can be computed only by constrained
            parameters and are therefore effectively constrained.
            )doc")
        .def_property_readonly("names", &x3cflux::ParameterClassification::getParameterNames, "Names of all parameters")
        .def_property_readonly("free", &x3cflux::ParameterClassification::getFreeParameters,
                               "Indices of free parameters")
        .def_property_readonly("constraint", &x3cflux::ParameterClassification::getConstraintParameters,
                               "Explicitly constrained parameters")
        .def_property_readonly("dependent", &x3cflux::ParameterClassification::getDependentParameters,
                               "Dependent parameters")
        .def_property_readonly("quasi_constraint", &x3cflux::ParameterClassification::getQuasiConstraintParameters,
                               "Effectively constrained parameters")
        .def_property_readonly("bounds", &x3cflux::ParameterClassification::getParameterBounds)
        .def(py::pickle(
            [](const x3cflux::ParameterClassification &paramClass) {
                return py::make_tuple(paramClass.getParameterNames(), paramClass.getFreeParameters(),
                                      paramClass.getConstraintParameters(), paramClass.getDependentParameters(),
                                      paramClass.getQuasiConstraintParameters(), paramClass.getParameterBounds());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::ParameterClassification(
                    t[0].cast<std::vector<std::string>>(), t[1].cast<std::vector<x3cflux::Index>>(),
                    t[2].cast<std::vector<std::pair<x3cflux::Index, x3cflux::Real>>>(),
                    t[3].cast<std::vector<
                        std::pair<x3cflux::Index, std::vector<std::pair<x3cflux::Index, x3cflux::Real>>>>>(),
                    t[4].cast<std::vector<std::pair<x3cflux::Index, x3cflux::Real>>>(),
                    t[5].cast<std::map<x3cflux::Index, std::pair<x3cflux::Real, x3cflux::Real>>>());
            }));

    addParameterSpaceAdapter<false>(m);
    addParameterSpaceAdapter<true>(m);
}

#endif // X3CFLUX_ADDPARAMETERSPACE_H
