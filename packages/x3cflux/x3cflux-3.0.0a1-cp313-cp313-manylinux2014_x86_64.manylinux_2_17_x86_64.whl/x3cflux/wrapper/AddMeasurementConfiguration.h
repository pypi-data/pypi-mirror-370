#ifndef X3CFLUX_ADDMEASUREMENTCONFIGURATION_H
#define X3CFLUX_ADDMEASUREMENTCONFIGURATION_H

#include <model/data/MeasurementConfiguration.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static void addMeasurementConfiguration(py::module &m) {
    py::enum_<x3cflux::ParameterType>(m, "ParameterType", "Type of metabolic network parameter")
        .value("NetFlux", x3cflux::ParameterType::NET_FLUX)
        .value("ExchangeFlux", x3cflux::ParameterType::EXCHANGE_FLUX)
        .value("PoolSize", x3cflux::ParameterType::POOL_SIZE)
        .export_values();

    py::class_<x3cflux::ParameterEntry>(m, "ParameterEntry", "Configuration of a metabolic network parameter")
        .def(py::init<std::string, x3cflux::ParameterType, x3cflux::Real>(), py::arg("name"), py::arg("type"),
             py::arg("value"), "Create entry for parameter")
        .def_property_readonly("name", &x3cflux::ParameterEntry::getName, "parameter name")
        .def_property_readonly("type", &x3cflux::ParameterEntry::getType, "parameter type")
        .def_property_readonly("value", &x3cflux::ParameterEntry::getValue, "parameter value")
        .def(py::pickle(
            [](const x3cflux::ParameterEntry &entry) {
                return py::make_tuple(entry.getName(), entry.getType(), entry.getValue());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::ParameterEntry(t[0].cast<std::string>(), t[1].cast<x3cflux::ParameterType>(),
                                               t[2].cast<x3cflux::Real>());
            }));

    py::class_<x3cflux::MeasurementConfiguration>(m, "MeasurementConfiguration", "Measurement setup and data")
        .def(py::init<std::string, std::string, bool, std::vector<std::shared_ptr<x3cflux::Substrate>>,
                      std::vector<std::shared_ptr<x3cflux::Measurement>>, x3cflux::ParameterConstraints,
                      x3cflux::ParameterConstraints, x3cflux::ParameterConstraints,
                      std::vector<x3cflux::ParameterEntry>>(),
             py::arg("name"), py::arg("comment"), py::arg("stationary"), py::arg("substrates"), py::arg("measurements"),
             py::arg("net_flux_constraints"), py::arg("exchange_flux_constraints"), py::arg("pool_size_constraints"),
             py::arg("parameter_entries"), "Create measurement setup and data")
        .def_property_readonly("name", &x3cflux::MeasurementConfiguration::getName, "Name of the configuration")
        .def_property_readonly("comment", &x3cflux::MeasurementConfiguration::getComment, "Modeler comment")
        .def_property_readonly("stationary", &x3cflux::MeasurementConfiguration::isStationary,
                               "Stationary or non-stationary")
        .def_property_readonly("substrates", &x3cflux::MeasurementConfiguration::getSubstrates,
                               "Substrates of the experiment")
        .def_property_readonly("measurements", &x3cflux::MeasurementConfiguration::getMeasurements,
                               "Measurement definitions and data")
        .def_property_readonly("net_flux_constraints", &x3cflux::MeasurementConfiguration::getNetFluxConstraints,
                               "Constraints of netto fluxes")
        .def_property_readonly("exchange_flux_constraints",
                               &x3cflux::MeasurementConfiguration::getExchangeFluxConstraints,
                               "Constraints of exchange fluxes")
        .def_property_readonly("pool_size_constraints", &x3cflux::MeasurementConfiguration::getPoolSizeConstraints,
                               "Constraints of pool sizes")
        .def_property_readonly("parameter_entries", &x3cflux::MeasurementConfiguration::getParameterEntries,
                               "Pre-calculated parameter configuration")
        .def(py::pickle(
            [](const x3cflux::MeasurementConfiguration &config) {
                return py::make_tuple(config.getName(), config.getComment(), config.isStationary(),
                                      config.getSubstrates(), config.getMeasurements(), config.getNetFluxConstraints(),
                                      config.getExchangeFluxConstraints(), config.getPoolSizeConstraints(),
                                      config.getParameterEntries());
            },
            [](py::tuple t) {
                if (t.size() != 9)
                    throw std::runtime_error("Invalid state");

                std::vector<std::shared_ptr<x3cflux::Substrate>> substrates;
                for (auto substrate : t[3].cast<std::vector<std::shared_ptr<x3cflux::Substrate>>>()) {
                    substrates.emplace_back(substrate->copy().release());
                }

                std::vector<std::shared_ptr<x3cflux::Measurement>> measurements;
                for (auto measurement : t[4].cast<std::vector<std::shared_ptr<x3cflux::Measurement>>>()) {
                    measurements.emplace_back(measurement->copy().release());
                }

                return x3cflux::MeasurementConfiguration(
                    t[0].cast<std::string>(), t[1].cast<std::string>(), t[2].cast<bool>(), substrates, measurements,
                    t[5].cast<x3cflux::ParameterConstraints>(), t[6].cast<x3cflux::ParameterConstraints>(),
                    t[7].cast<x3cflux::ParameterConstraints>(), t[8].cast<std::vector<x3cflux::ParameterEntry>>());
            }));
}

#endif // X3CFLUX_ADDMEASUREMENTCONFIGURATION_H
