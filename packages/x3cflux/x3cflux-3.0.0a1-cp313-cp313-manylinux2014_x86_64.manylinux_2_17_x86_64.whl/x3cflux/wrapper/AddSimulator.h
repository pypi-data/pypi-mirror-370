#ifndef X3CFLUX_ADDSIMULATOR_H
#define X3CFLUX_ADDSIMULATOR_H

#include <model/measurement/WeightedLeastSquaresLossFunction.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

template <typename Method, bool Stationary, bool Multi>
using LossFunction = x3cflux::WeightedLeastSquaresLossFunction<Method, Stationary, Multi>;

std::unique_ptr<x3cflux::SimulatorBase> create(const x3cflux::NetworkData &networkData,
                                               const std::vector<x3cflux::MeasurementConfiguration> &configurations,
                                               const std::string &simulationMethod) {
    if (configurations.empty()) {
        X3CFLUX_THROW(x3cflux::ParseError, "No configuration supplied");
    } else if (configurations.size() == 1) {
        const auto &firstConfig = configurations.front();
        if (simulationMethod == "cumomer") {
            if (firstConfig.isStationary()) {
                return std::make_unique<LossFunction<x3cflux::CumomerMethod, true, false>>(networkData, configurations);
            } else {
                return std::make_unique<LossFunction<x3cflux::CumomerMethod, false, false>>(networkData,
                                                                                            configurations);
            }
        } else if (simulationMethod == "emu") {
            if (firstConfig.isStationary()) {
                return std::make_unique<LossFunction<x3cflux::EMUMethod, true, false>>(networkData, configurations);
            } else {
                return std::make_unique<LossFunction<x3cflux::EMUMethod, false, false>>(networkData, configurations);
            }
        } else if (simulationMethod == "auto") {
            std::size_t numMeasCumomers = 0, numMeasEMUs = 0;
            for (const auto &measurement : firstConfig.getMeasurements()) {
                if (isInstanceOf<x3cflux::LabelingMeasurement>(measurement)) {
                    auto labelingMeasurement = std::dynamic_pointer_cast<x3cflux::LabelingMeasurement>(measurement);
                    numMeasCumomers +=
                        x3cflux::MeasurementConverter<x3cflux::CumomerMethod>::calculateStates(labelingMeasurement)
                            .size();
                    numMeasEMUs +=
                        x3cflux::MeasurementConverter<x3cflux::EMUMethod>::calculateStates(labelingMeasurement).size();
                }
            }

            if (numMeasCumomers <= numMeasEMUs) {
                if (firstConfig.isStationary()) {
                    return std::make_unique<LossFunction<x3cflux::CumomerMethod, true, false>>(networkData,
                                                                                               configurations);
                } else {
                    return std::make_unique<LossFunction<x3cflux::CumomerMethod, false, false>>(networkData,
                                                                                                configurations);
                }
            } else {
                if (firstConfig.isStationary()) {
                    return std::make_unique<LossFunction<x3cflux::EMUMethod, true, false>>(networkData, configurations);
                } else {
                    return std::make_unique<LossFunction<x3cflux::EMUMethod, false, false>>(networkData,
                                                                                            configurations);
                }
            }
        } else {
            X3CFLUX_THROW(x3cflux::ParseError, "Invalid simulation method selected");
        }
    } else {
        bool stationary = configurations.front().isStationary();
        auto isStatDifferent = [&](const x3cflux::MeasurementConfiguration &config) -> bool {
            return config.isStationary() != stationary;
        };

        if (std::any_of(configurations.begin(), configurations.end(), isStatDifferent)) {
            X3CFLUX_THROW(x3cflux::ParseError, "Multi-experiment configurations cannot be "
                                               "stationary and non-stationary");
        }

        if (simulationMethod == "cumomer") {
            if (stationary) {
                return std::make_unique<LossFunction<x3cflux::CumomerMethod, true, true>>(networkData, configurations);
            } else {
                return std::make_unique<LossFunction<x3cflux::CumomerMethod, false, true>>(networkData, configurations);
            }
        } else if (simulationMethod == "emu") {
            if (stationary) {
                return std::make_unique<LossFunction<x3cflux::EMUMethod, true, true>>(networkData, configurations);
            } else {
                return std::make_unique<LossFunction<x3cflux::EMUMethod, false, true>>(networkData, configurations);
            }
        } else if (simulationMethod == "auto") {
            std::size_t numMeasCumomers = 0, numMeasEMUs = 0;
            for (const auto &config : configurations) {
                for (const auto &measurement : config.getMeasurements()) {
                    if (isInstanceOf<x3cflux::LabelingMeasurement>(measurement)) {
                        auto labelingMeasurement = std::dynamic_pointer_cast<x3cflux::LabelingMeasurement>(measurement);
                        numMeasCumomers +=
                            x3cflux::MeasurementConverter<x3cflux::CumomerMethod>::calculateStates(labelingMeasurement)
                                .size();
                        numMeasEMUs +=
                            x3cflux::MeasurementConverter<x3cflux::EMUMethod>::calculateStates(labelingMeasurement)
                                .size();
                    }
                }
            }

            if (numMeasCumomers < numMeasEMUs) {
                if (stationary) {
                    return std::make_unique<LossFunction<x3cflux::CumomerMethod, true, true>>(networkData,
                                                                                              configurations);
                } else {
                    return std::make_unique<LossFunction<x3cflux::CumomerMethod, false, true>>(networkData,
                                                                                               configurations);
                }
            } else {
                if (stationary) {
                    return std::make_unique<LossFunction<x3cflux::EMUMethod, true, true>>(networkData, configurations);
                } else {
                    return std::make_unique<LossFunction<x3cflux::EMUMethod, false, true>>(networkData, configurations);
                }
            }
        } else {
            X3CFLUX_THROW(x3cflux::ParseError, "Invalid simulation method selected");
        }
    }
}

std::vector<x3cflux::MeasurementConfiguration>
selectConfigurations(const std::vector<x3cflux::MeasurementConfiguration> &configurations,
                     const std::vector<std::string> &configurationNames) {
    std::vector<x3cflux::MeasurementConfiguration> selectedConfigs;
    for (const auto &name : configurationNames) {
        auto it = std::find_if(
            configurations.begin(), configurations.end(),
            [&](const x3cflux::MeasurementConfiguration &config) -> bool { return config.getName() == name; });
        if (it != configurations.end()) {
            selectedConfigs.push_back(*it);
        } else {
            X3CFLUX_THROW(x3cflux::ParseError, "Configuration with name \"" + name + "\n does not exist");
        }
    }

    return selectedConfigs;
}

std::unique_ptr<x3cflux::SimulatorBase> createSimulatorFromData(const x3cflux::NetworkData &networkData,
                                                                const x3cflux::MeasurementConfiguration &configuration,
                                                                const std::string &simulationMethod) {
    return create(networkData, {configuration}, simulationMethod);
}

std::unique_ptr<x3cflux::SimulatorBase>
createMultiSimulatorFromData(const x3cflux::NetworkData &networkData,
                             const std::vector<x3cflux::MeasurementConfiguration> &configurations,
                             const std::string &simulationMethod) {
    return create(networkData, configurations, simulationMethod);
}

std::unique_ptr<x3cflux::SimulatorBase> create(const std::string &fmlFilePath,
                                               const std::vector<std::string> &configurationNames = {"default"},
                                               const std::string &simulationMethod = "auto") {
    auto model = x3cflux::FluxMLParser::getInstance().parse(fmlFilePath);

    const auto &networkData = model.getNetworkData();
    auto configurations = selectConfigurations(model.getConfigurations(), configurationNames);

    return create(networkData, configurations, simulationMethod);
}

std::unique_ptr<x3cflux::SimulatorBase> createSimulatorFromFML(const std::string &fmlFilePath,
                                                               const std::string &configurationName,
                                                               const std::string &simulationMethod) {
    return create(fmlFilePath, {configurationName}, simulationMethod);
}

std::unique_ptr<x3cflux::SimulatorBase> createMultiSimulatorFromFML(const std::string &fmlFilePath,
                                                                    const std::vector<std::string> &configurationNames,
                                                                    const std::string &simulationMethod) {
    return create(fmlFilePath, configurationNames, simulationMethod);
}

template <typename Method, bool Stationary, bool Multi> void addWeightedLeastSquaresLossFunction(py::module &m) {
    typedef LossFunction<Method, Stationary, Multi> Simulator;

    auto name = std::string(Multi ? "Multi" : "") + std::string(Stationary ? "Stationary" : "NonStationary") +
                std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU") + "Simulator";
    py::class_<Simulator, x3cflux::SimulatorBase>(m, name.c_str(), R"doc(
            Labeling simulator
            )doc")
        .def_property_readonly("network_data", &Simulator::getNetworkData)
        .def_property_readonly("configurations", &Simulator::getConfigurations)
        .def_property_readonly("measurement_names", &Simulator::getMeasurementNames, "Names of measurements")
        .def_property_readonly("measurement_multi_indices", &Simulator::getMeasurementMultiIndices)
        .def_property_readonly("measurement_time_stamps", &Simulator::getMeasurementTimeStamps,
                               "Time stamps of labeling measurements")
        .def_property_readonly("measurement_data", &Simulator::getMeasurementData)
        .def_property_readonly("measurement_standard_deviations", &Simulator::getMeasurementStandardDeviations,
                               "Standard deviations of measurements")
        .def_property_readonly("parameter_space", py::overload_cast<>(&Simulator::getParameterSpace), "Parameter space")
        .def_property_readonly("network", py::overload_cast<>(&Simulator::getLabelingNetwork), "Labeling network")
        .def_property_readonly("builder", py::overload_cast<>(&Simulator::getSystemBuilder), "Labeling system builder")
        .def("compute_measurements", &Simulator::computeMeasurements, py::arg("params"),
             py::arg("time_stamps") = std::vector<x3cflux::Real>{},
             R"doc(
                 Computes measurements from free parameters.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    pair of labeling and parameter measurements
                 )doc")
        .def("compute_scaled_measurements", &Simulator::computeScaledMeasurements, py::arg("params"),
             R"doc(
                 Computes measurements with group scaling factors from free parameters.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    pair of scaled labeling measurements and parameter measurements
                 )doc")
        .def("compute_loss", py::overload_cast<const x3cflux::RealVector &>(&Simulator::computeLoss, py::const_),
             py::arg("params"),
             R"doc(
                 Computes weighted least squares loss to experimental data.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    scalar loss
                 )doc")
        .def("compute_loss", py::overload_cast<const x3cflux::RealMatrix &>(&Simulator::computeLoss, py::const_),
             py::arg("params"),
             R"doc(
                 Computes weighted least squares loss to experimental data.

                 :param np.ndarray params:
                    matrix of free parameters
                 :return:
                    vector of loss values
                 )doc")
        .def("compute_multi_losses", &Simulator::computeMultiLosses, py::arg("params"),
             R"doc(
                 Computes weighted least squares losses to multiple experimental data.

                 :param np.ndarray params:
                    matrix of free parameters
                 :return:
                    vector of loss values
                 )doc")
        .def("compute_loss_gradient",
             py::overload_cast<const x3cflux::RealVector &>(&Simulator::computeLossGradient, py::const_),
             py::arg("params"),
             R"doc(
                 Computes gradient of weighted least squares loss to experimental data.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    loss gradient
                 )doc")
        .def("compute_loss_gradient",
             py::overload_cast<const x3cflux::RealMatrix &>(&Simulator::computeLossGradient, py::const_),
             py::arg("params"),
             R"doc(
                 Computes gradients of weighted least squares loss to experimental data.

                 :param np.ndarray params:
                    matrix of free parameters
                 :return:
                    matrix of loss gradients
                 )doc")
        .def("compute_multi_loss_gradients", &Simulator::computeMultiLossGradients, py::arg("params"),
             R"doc(
                 Computes gradients of weighted least squares loss to multiple experimental data.

                 :param np.ndarray params:
                    matrix of free parameters
                 :return:
                    matrix of loss gradients
                 )doc")
        .def("compute_jacobian", &Simulator::computeJacobian, py::arg("params"),
             R"doc(
                 Computes Jacobian of measurement simulation.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    Jacobian matrix
                 )doc")
        .def("compute_multi_jacobians", &Simulator::computeMultiJacobians, py::arg("params"),
             R"doc(
                 Computes Jacobians of multiple measurement simulations.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    list of Jacobian matrices
                 )doc")
        .def("compute_linearized_hessian", &Simulator::computeLinearizedHessian, py::arg("params"),
             R"doc(
                 Computes linearized Hessian of weighted least squares loss to experimental data.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    linearized Hessian matrix
                 )doc")
        .def("compute_multi_linearized_hessians", &Simulator::computeMultiLinearizedHessians, py::arg("params"),
             R"doc(
                 Computes linearized Hessians of weighted least squares losses to multiple experimental data.

                 :param np.ndarray params:
                    free parameter vector
                 :return:
                    list of linearized Hessian matrices
                 )doc")
        .def(py::pickle(
            [](const Simulator &simulator) {
                std::tuple<x3cflux::Real, x3cflux::Real, x3cflux::Real, std::size_t, x3cflux::Real, x3cflux::Real,
                           std::size_t>
                    numericalSettings;

                std::get<0>(numericalSettings) = simulator.getParameterSpace().getConstraintViolationTolerance();
                if constexpr (not Stationary) {
                    const auto &solver = simulator.getSystemBuilder().getSolver();
                    std::get<1>(numericalSettings) = solver.getRelativeTolerance();
                    std::get<2>(numericalSettings) = solver.getAbsoluteTolerance();
                    std::get<3>(numericalSettings) = solver.getNumMaxSteps();

                    const auto &derivativSolver = simulator.getSystemBuilder().getDerivativeSolver();
                    std::get<4>(numericalSettings) = derivativSolver.getRelativeTolerance();
                    std::get<5>(numericalSettings) = derivativSolver.getAbsoluteTolerance();
                    std::get<6>(numericalSettings) = derivativSolver.getNumMaxSteps();
                }

                return py::make_tuple(simulator.getNetworkData(), simulator.getConfigurations(), numericalSettings);
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");

                auto simulator = std::make_unique<Simulator>(
                    t[0].cast<x3cflux::NetworkData>(), t[1].cast<std::vector<x3cflux::MeasurementConfiguration>>());

                auto numericalSettings = t[2].cast<std::tuple<x3cflux::Real, x3cflux::Real, x3cflux::Real, std::size_t,
                                                              x3cflux::Real, x3cflux::Real, std::size_t>>();
                simulator->getParameterSpace().setConstraintViolationTolerance(std::get<0>(numericalSettings));
                if constexpr (not Stationary) {
                    auto &solver = simulator->getSystemBuilder().getSolver();
                    solver.setRelativeTolerance(std::get<1>(numericalSettings));
                    solver.setAbsoluteTolerance(std::get<2>(numericalSettings));
                    solver.setNumMaxSteps(std::get<3>(numericalSettings));

                    auto &derivativeSolver = simulator->getSystemBuilder().getDerivativeSolver();
                    derivativeSolver.setRelativeTolerance(std::get<4>(numericalSettings));
                    derivativeSolver.setAbsoluteTolerance(std::get<5>(numericalSettings));
                    derivativeSolver.setNumMaxSteps(std::get<6>(numericalSettings));
                }

                return simulator;
            }));
}

static void addSimulator(py::module &m) {
    m.def("create_simulator_from_fml", &createSimulatorFromFML, py::arg("fml_file_path"),
          py::arg("config_name") = "default", py::arg("sim_method") = "auto", R"doc(
    Creates simulator from FluxML file.

    Automatically reduces the network by performing backtracking of the simulation state variable required for
    simulating the measurements.

    :param str fml_file_path:
        Absolute or relative path to FluxML file
    :param str config_name:
        Name of the measurement configuration to simulate. Default: "default"
    :param str sim_method:
        Simulation state variable (Cumomer, EMU) to be used. Valid options are: "cumomer", "emu", "auto".
        Automatic variable selection will select the state variable type that results in the lowest number
        of initial state variables.
    :return:
        simulator object
    )doc");
    m.def("create_simulator_from_fml", &createMultiSimulatorFromFML, py::arg("fml_file_path"), py::arg("config_names"),
          py::arg("sim_method") = "auto", R"doc(
    Creates multi experiment simulator from FluxML file.

    Automatically reduces the network by performing backtracking of the simulation state variable required for
    simulating the measurements.

    :param str fml_file_path:
        Absolute or relative path to FluxML file
    :param List[str] config_names:
        Names of the measurement configurations  to simulate
    :param str sim_method:
        Simulation state variable (Cumomer, EMU) to be used. Valid options are: "cumomer", "emu", "auto".
        Automatic variable selection will select the state variable type that results in the lowest number
        of initial state variables.
    :return:
        simulator object
    )doc");
    m.def("create_simulator_from_data", &createSimulatorFromData, py::arg("network_data"), py::arg("configuration"),
          py::arg("sim_method") = "auto", R"doc(
    Creates simulator from FluxML data objects.

    Automatically reduces the network by performing backtracking of the simulation state variable required for
    simulating the measurements.

    :param x3cflux.NetworkData network_data:
        Structural network data and atom transitions
    :param x3cflux.MeasurementConfiguration configuration:
        Measurement configuration object to simulate
    :param str sim_method:
        Simulation state variable (Cumomer, EMU) to be used. Valid options are: "cumomer", "emu", "auto".
        Automatic variable selection will select the state variable type that results in the lowest number
        of initial state variables.
    :return:
        simulator object
)doc");
    m.def("create_simulator_from_data", &createMultiSimulatorFromData, py::arg("network_data"),
          py::arg("configurations"), py::arg("sim_method") = "auto", R"doc(
    Creates multi experiment simulator from FluxML data objects.

    Automatically reduces the network by performing backtracking of the simulation state variable required for
    simulating the measurements.

    :param x3cflux.NetworkData network_data:
        Structural network data and atom transitions
    :param List[x3cflux.MeasurementConfiguration] configurations:
        Measurement configuration object to simulate
    :param str sim_method:
        Simulation state variable (Cumomer, EMU) to be used. Valid options are: "cumomer", "emu", "auto".
        Automatic variable selection will select the state variable type that results in the lowest number
        of initial state variables.
    :return:
        simulator object
)doc");

    py::class_<x3cflux::SimulatorBase>(m, "_SimulatorBase", "Base class for labeling simulators");

    addWeightedLeastSquaresLossFunction<x3cflux::CumomerMethod, false, false>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::CumomerMethod, false, true>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::CumomerMethod, true, false>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::CumomerMethod, true, true>(m);

    addWeightedLeastSquaresLossFunction<x3cflux::EMUMethod, false, false>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::EMUMethod, false, true>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::EMUMethod, true, false>(m);
    addWeightedLeastSquaresLossFunction<x3cflux::EMUMethod, true, true>(m);

    m.def("get_parameters", &x3cflux::getParameters<true>, py::arg("parameter_space"), py::arg("parameter_entries"),
          R"doc(
    Gets parameter configuration from x3cflux.FluxMLData object.

    Intended to use with a simulator object to generate a valid parameter vector from previous configuration. Unset flux parameters
    will be set to 0, unset pool size parameters will be set to 1.

    :param x3cflux.StationaryParameterSpace parameter_space:
        parameter space of the simulator
    :param List[x3cflux.ParameterEntry] parameter_entries:
        the names, types and values of specified parameters
    :return:
        parameter vector
    )doc");
    m.def("get_parameters", &x3cflux::getParameters<false>, py::arg("parameter_space"), py::arg("parameter_entries"),
          R"doc(
    Gets parameter configuration from x3cflux.FluxMLData object.

    Intended to use with a simulator object to generate a valid parameter vector from previous configuration. Unset flux parameters
    will be set to 0, unset pool size parameters will be set to 1.

    :param x3cflux.NonStationaryParameterSpace parameter_space:
        parameter space of the simulator
    :param List[x3cflux.ParameterEntry] parameter_entries:
        the names, types and values of specified parameters
    :return:
        parameter vector
    )doc");
}

#endif // X3CFLUX_ADDSIMULATOR_H
