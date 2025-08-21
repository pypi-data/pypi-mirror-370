#ifndef X3CFLUX_ADDSYSTEMBUILDER_H
#define X3CFLUX_ADDSYSTEMBUILDER_H

#include <model/system/CascadeSystemBuilder.h>
#include <pybind11/operators.h>
#include <pybind11/smart_holder.h>

template <typename StateType> void addLinearEquationSystem(py::module &m) {
    typedef x3cflux::LinearEquationSystem<x3cflux::RealSparseMatrix, StateType> System;

    auto name =
        std::string(std::is_same<StateType, x3cflux::RealVector>::value ? "Vector" : "Matrix") + "LinearEquationSystem";
    py::class_<System>(m, name.c_str(), "System of linear equations")
        .def_property_readonly("matrix", &System::getMatrix, "LHS matrix of the equation")
        .def_property_readonly("rhs", &System::getRhs, "RHS of the equation");
}

template <typename StateType> void addLinearInitialValueProblem(py::module &m) {
    typedef x3cflux::LinearIVPBase<StateType, x3cflux::RealSparseMatrix> System;

    auto name = std::string(std::is_same<StateType, x3cflux::RealVector>::value ? "Vector" : "Matrix") + "LinearIVP";
    py::class_<System>(m, name.c_str(), "System of linear initial value problems")
        .def_property_readonly("initial_value", &System::getInitialValue, "Initial values")
        .def_property_readonly("jacobian", &System::getJacobiMatrix, "Jacobi matrix of the equation")
        .def("evaluate_inhomogeneity", &System::evaluateInhomogeneity, py::arg("time"), R"doc(
            Evaluates the inhomogeneity of the equation

            :param float time:
                time point
            :return:
                evaluated inhomogeneity as vector
            )doc")
        .def("__call__", &System::operator(), py::arg("time"), py::arg("state"), R"doc(
            Evaluates the RHS of the differential equation

            :param float time:
                time point
            :param np.ndarray state:
                system state
            :return:
                evaluated RHS as vector
            )doc");
}

template <typename Method, bool Multi> void addStationaryCascadeLevelSystem(py::module &m) {
    typedef x3cflux::CascadeLevelSystem<Method, true, Multi> LevelSystem;

    auto name = std::string(Multi ? "Multi" : "") + std::string("Stationary") +
                std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU") + "LevelSystem";
    py::class_<LevelSystem, x3cflux::LinearEquationSystem<x3cflux::RealSparseMatrix, typename LevelSystem::RhsType>>(
        m, name.c_str(), R"doc(
    Level system of a IST cascade system
    )doc");
}

template <typename Method, bool Multi> void addNonStationaryCascadeLevelSystem(py::module &m) {
    typedef x3cflux::CascadeLevelSystem<Method, false, Multi> LevelSystem;

    auto name = std::string(Multi ? "Multi" : "") + std::string("NonStationary") +
                std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU") + "LevelSystem";
    py::class_<LevelSystem, x3cflux::LinearIVPBase<typename LevelSystem::State, x3cflux::RealSparseMatrix>>(
        m, name.c_str(), R"doc(
    Level system of a INST cascade system
    )doc");
}

template <typename ValueType> void addCubicHermiteSpline(py::module &m) {
    typedef x3cflux::CubicHermiteSpline<ValueType> Spline;

    auto name =
        std::string(std::is_same<ValueType, x3cflux::RealVector>::value ? "Vector" : "Matrix") + "CubicHermiteSpline";
    py::class_<Spline>(m, name.c_str(), "Cubic splines defined by Hermite conditions")
        .def_property_readonly("domain", &Spline::getDomain, "Interpolation interval")
        .def_property_readonly("places", &Spline::getPlaces, "Observed time points")
        .def_property_readonly("function_values", &Spline::getFunctionValues, "Observed function values")
        .def_property_readonly("derivative_values", &Spline::getDerivativeValues, "Observed derivative values")
        .def("__call__", py::overload_cast<x3cflux::Real>(&Spline::operator(), py::const_), py::arg("place"), R"doc(
            Evaluates splines on an arbitrary point in time.

            Extrapolation is done using the first and the last spline. CAUTION: Evaluating the spline outside of the domain
            might lead to non-sensible results!

            :param float place:
                time point
            :return:
                evaluated function as vector
            )doc")
        .def("__call__", py::overload_cast<x3cflux::Real, x3cflux::Index>(&Spline::operator(), py::const_),
             py::arg("place"), py::arg("index"), R"doc(
            Evaluates splines interpolating one function compound on an arbitrary point in time.

            Extrapolation is done using the first and the last spline. CAUTION: Evaluating the spline outside of the domain
            might lead to non-sensible results!

            :param float place:
                time point
            :param int index:
                index of the compound (must be > 0)
            :return:
                evaluated function as float
            )doc");
}

template <typename Method, bool Stationary, bool Multi> void addCascadeSystem(py::module &m) {
    typedef x3cflux::CascadeSystem<Method, Stationary, Multi> System;

    auto name = std::string(Multi ? "Multi" : "") + std::string(Stationary ? "Stationary" : "NonStationary") +
                std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU") + "System";
    py::class_<System>(m, name.c_str(), "Cascade system")
        .def("get_level_system", &System::getLevelSystem, py::arg("index"),
             R"doc(
            Generates level system of given index.

            :param int index:
                index of the cascade level
            :return:
                level system
            )doc")
        .def("solve", &System::solve, R"doc(
            Solves the cascade system.

            Internally, the level systems are successively solved by the configured solver and
            the solutions propagated to next level.

            :return:
                list of level solution
            )doc");
}

PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LESSolver<x3cflux::RealSparseMatrix, x3cflux::RealVector>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LESSolver<x3cflux::RealSparseMatrix, x3cflux::RealMatrix>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LUSolver<x3cflux::RealSparseMatrix, x3cflux::RealVector>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LUSolver<x3cflux::RealSparseMatrix, x3cflux::RealMatrix>)

template <typename StateType> void addLESSolver(py::module &m) {
    typedef x3cflux::LESSolver<x3cflux::RealSparseMatrix, StateType> Solver;

    class PySolver : public Solver, public py::trampoline_self_life_support {
      public:
        using typename Solver::MatrixType;
        using typename Solver::RhsType;
        using typename Solver::SolutionType;
        typedef x3cflux::LinearEquationSystem<MatrixType, RhsType> Problem;

        using Solver::Solver;
        inline SolutionType solve(const Problem &problem) const override {
            PYBIND11_OVERRIDE_PURE(SolutionType, Solver, solve, problem);
        };
        std::unique_ptr<Solver> copy() const override {
            PYBIND11_OVERRIDE_PURE(std::unique_ptr<Solver>, Solver, copy);
        };
    };

    std::string value(std::is_same<StateType, x3cflux::RealVector>::value ? "Vector" : "Matrix");

    auto solverBaseName = value + "LESSolver";
    py::classh<Solver, PySolver>(m, solverBaseName.c_str(), "Python interface for linear equation system solvers")
        .def(py::init<x3cflux::Real>(), py::arg("tolerance") = 1e-9, "Creates Python LES solver.")
        .def_property("tolerance", &Solver::getTolerance, &Solver::setTolerance)
        .def("solve", &Solver::solve, py::arg("problem"), R"doc(
            Solves linear equation system.

            :param problem:
                Linear equation system
            :return:
                Solution vector/matrix
            )doc")
        .def("copy", &Solver::copy);

    auto luName = value + "LUSolver";
    typedef x3cflux::LUSolver<x3cflux::RealSparseMatrix, StateType> LUSolver;
    py::classh<LUSolver, Solver>(m, luName.c_str(), "Linear equation system solver using LU decomposition")
        .def(py::init<x3cflux::Real>(), py::arg("tolerance") = 1e-9, "Creates Python LU solver for LES.")
        .def("solve", &LUSolver::solve, R"doc(
            Solves linear equation system.

            :param problem:
                Linear equation system
            :return:
                Solution vector/matrix
            )doc");
}

PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearIVPSolver<x3cflux::RealVector, x3cflux::RealSparseMatrix>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearIVPSolver<x3cflux::RealMatrix, x3cflux::RealSparseMatrix>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearSDIRK43Solver<x3cflux::RealVector, x3cflux::RealSparseMatrix>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearSDIRK43Solver<x3cflux::RealMatrix, x3cflux::RealSparseMatrix>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearCVODESolver<x3cflux::RealVector>)
PYBIND11_SMART_HOLDER_TYPE_CASTERS(x3cflux::LinearCVODESolver<x3cflux::RealMatrix>)

template <typename StateType> void addLinearIVPSolver(py::module &m) {
    typedef x3cflux::LinearIVPSolver<StateType, x3cflux::RealSparseMatrix> Solver;
    class PySolver : public Solver, public py::trampoline_self_life_support {
      public:
        using typename Solver::ProblemBase;
        using typename Solver::Solution;

        using Solver::Solver;
        inline Solution solve(const ProblemBase &problem) const override {
            PYBIND11_OVERRIDE_PURE(Solution, Solver, solve, problem);
        };
        std::unique_ptr<Solver> copy() const override {
            PYBIND11_OVERRIDE_PURE(std::unique_ptr<Solver>, Solver, copy);
        };
    };

    std::string value(std::is_same<StateType, x3cflux::RealVector>::value ? "Vector" : "Matrix");

    auto solverBaseName = value + "LinearIVPSolver";
    py::classh<Solver, PySolver>(m, solverBaseName.c_str(), "Python interface for linear initial value problem solvers")
        .def(py::init<x3cflux::Real, x3cflux::Real, std::size_t>(), py::arg("relative_tolerance") = 1e-6,
             py::arg("absolute_tolerance") = 1e-9, py::arg("num_max_steps") = 500)
        .def_property("relative_tolerance", &Solver::getRelativeTolerance, &Solver::setRelativeTolerance)
        .def_property("absolute_tolerance", &Solver::getAbsoluteTolerance, &Solver::setAbsoluteTolerance)
        .def_property("num_max_steps", &Solver::getNumMaxSteps, &Solver::setNumMaxSteps)
        .def("solve", &Solver::solve, py::arg("problem"), R"doc(
            Solves linear initial value problem.

            :param problem:
                Initial value problem
            :return:
                Interpolated solution function
            )doc")
        .def("copy", &Solver::copy);

    auto sdirkName = value + "LinearSDIRK43Solver";
    typedef x3cflux::LinearSDIRK43Solver<StateType, x3cflux::RealSparseMatrix> SDIRKSolver;
    py::classh<SDIRKSolver, Solver>(m, sdirkName.c_str(), "Linear initial value problem solver using SDIRK43 scheme")
        .def(py::init<std::size_t, x3cflux::Real, x3cflux::Real, std::size_t>(), py::arg("num_max_step_attempts") = 100,
             py::arg("relative_tolerance") = 1e-6, py::arg("absolute_tolerance") = 1e-9, py::arg("num_max_steps") = 500)
        .def_property("num_max_step_attempts", &SDIRKSolver::getNumMaxStepAttempts, &SDIRKSolver::setNumMaxStepAttempts)
        .def("solve", &SDIRKSolver::solve, R"doc(
            Solves linear initial value problem.

            :param problem:
                Initial value problem
            :return:
                Interpolated solution function
            )doc");

    auto cvodeName = value + "LinearCVODESolver";
    typedef x3cflux::LinearCVODESolver<StateType> CVODESolver;
    py::classh<CVODESolver, Solver>(m, cvodeName.c_str(),
                                    "Linear initial value problem solver from SUNDIALS CVODE (BDF method)")
        .def(py::init<std::size_t, x3cflux::Real, x3cflux::Real, std::size_t>(), py::arg("num_max_step_attempts") = 100,
             py::arg("relative_tolerance") = 1e-6, py::arg("absolute_tolerance") = 1e-9, py::arg("num_max_steps") = 500)
        .def_property("num_max_step_attempts", &CVODESolver::getNumMaxStepAttempts, &CVODESolver::setNumMaxStepAttempts)
        .def("solve", &CVODESolver::solve, R"doc(
            Solves linear initial value problem.

            :param problem:
                Initial value problem
            :return:
                Interpolated solution function
            )doc");
}

template <typename Method, bool Stationary, bool Multi> void addCascadeSystemBuilder(py::module &m) {
    typedef x3cflux::CascadeSystemBuilder<Method, Stationary, Multi> SystemBuilder;

    auto name = std::string(Multi ? "Multi" : "") + std::string(Stationary ? "Stationary" : "NonStationary") +
                std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU") + "SystemBuilder";
    py::class_<SystemBuilder> builder(m, name.c_str(), "Cascade system builder");
    builder.def_property_readonly("solver", py::overload_cast<>(&SystemBuilder::getSolver))
        .def_property("derivative_solver", py::overload_cast<>(&SystemBuilder::getDerivativeSolver),
                      &SystemBuilder::setDerivativeSolver)
        .def("set_solver", &SystemBuilder::setSolver, py::arg("solver"))
        .def("build", &SystemBuilder::build, py::arg("params"), R"doc(
            Builds cascade system from metabolic parameters.

            :param np.ndarray params:
                vector of all metabolic parameters (e.g. from compute_parameters)
            :return:
                cascade system
            )doc");

    if constexpr (not Stationary) {
        builder.def(
            "set_solver",
            [](SystemBuilder &self, const std::string &solverName) {
                if (solverName == "bdf") {
                    self.setSolver(x3cflux::LinearCVODESolver<typename SystemBuilder::SystemState>());
                } else if (solverName == "sdirk") {
                    self.setSolver(
                        x3cflux::LinearSDIRK43Solver<typename SystemBuilder::SystemState, x3cflux::RealSparseMatrix>());
                } else {
                    throw std::invalid_argument(std::string("Unknown solver \"") + solverName +
                                                "\" (options: \"bdf\", "
                                                "\"sdirk\"");
                }
            },
            py::arg("solver_name"));
    }
}

static void addSystemBuilder(py::module &m) {
    addLinearEquationSystem<x3cflux::RealVector>(m);
    addLinearEquationSystem<x3cflux::RealMatrix>(m);
    addLinearInitialValueProblem<x3cflux::RealVector>(m);
    addLinearInitialValueProblem<x3cflux::RealMatrix>(m);

    addCubicHermiteSpline<x3cflux::RealVector>(m);
    addCubicHermiteSpline<x3cflux::RealMatrix>(m);

    addLESSolver<x3cflux::RealVector>(m);
    addLESSolver<x3cflux::RealMatrix>(m);
    addLinearIVPSolver<x3cflux::RealVector>(m);
    addLinearIVPSolver<x3cflux::RealMatrix>(m);

    addStationaryCascadeLevelSystem<x3cflux::CumomerMethod, false>(m);
    addStationaryCascadeLevelSystem<x3cflux::CumomerMethod, true>(m);
    addStationaryCascadeLevelSystem<x3cflux::EMUMethod, false>(m);
    addStationaryCascadeLevelSystem<x3cflux::EMUMethod, true>(m);

    addNonStationaryCascadeLevelSystem<x3cflux::CumomerMethod, false>(m);
    addNonStationaryCascadeLevelSystem<x3cflux::CumomerMethod, true>(m);
    addNonStationaryCascadeLevelSystem<x3cflux::EMUMethod, false>(m);
    addNonStationaryCascadeLevelSystem<x3cflux::EMUMethod, true>(m);

    addCascadeSystem<x3cflux::CumomerMethod, true, false>(m);
    addCascadeSystem<x3cflux::CumomerMethod, true, true>(m);
    addCascadeSystem<x3cflux::CumomerMethod, false, false>(m);
    addCascadeSystem<x3cflux::CumomerMethod, false, true>(m);
    addCascadeSystem<x3cflux::EMUMethod, true, false>(m);
    addCascadeSystem<x3cflux::EMUMethod, true, true>(m);
    addCascadeSystem<x3cflux::EMUMethod, false, false>(m);
    addCascadeSystem<x3cflux::EMUMethod, false, true>(m);

    addCascadeSystemBuilder<x3cflux::CumomerMethod, true, false>(m);
    addCascadeSystemBuilder<x3cflux::CumomerMethod, true, true>(m);
    addCascadeSystemBuilder<x3cflux::CumomerMethod, false, false>(m);
    addCascadeSystemBuilder<x3cflux::CumomerMethod, false, true>(m);
    addCascadeSystemBuilder<x3cflux::EMUMethod, true, false>(m);
    addCascadeSystemBuilder<x3cflux::EMUMethod, true, true>(m);
    addCascadeSystemBuilder<x3cflux::EMUMethod, false, false>(m);
    addCascadeSystemBuilder<x3cflux::EMUMethod, false, true>(m);
}

#endif // X3CFLUX_ADDSYSTEMBUILDER_H
