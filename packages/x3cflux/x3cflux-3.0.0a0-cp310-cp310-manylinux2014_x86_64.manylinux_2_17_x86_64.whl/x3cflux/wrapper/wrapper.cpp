#include <AddExceptions.h>
#include <AddFluxMLParser.h>
#include <AddLabelingNetwork.h>
#include <AddMeasurementConfiguration.h>
#include <AddMeasurements.h>
#include <AddNetworkData.h>
#include <AddParameterConstaints.h>
#include <AddParameterSpace.h>
#include <AddSimulator.h>
#include <AddSubstrate.h>
#include <AddSystemBuilder.h>
#include <TypeCasts.h>
#include <boost/log/trivial.hpp>
#include <pybind11/detail/common.h>
#include <pybind11/eigen.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <util/Logging.h>

class LogDummy {
  public:
    static int level;
};
int LogDummy::level = 3;

class OMPDummy {
  public:
    static int numThreads;
};
int OMPDummy::numThreads = 1;

PYBIND11_MODULE(core, m) {
    X3CFLUX_LOG_INIT();
    py::class_<LogDummy>(m, "logging")
        .def_property_static(
            "level", [](py::object) { return LogDummy::level; },
            [](py::object, int level) {
                if (level > 4) {
                    X3CFLUX_INFO() << "Given log level (" + std::to_string(level) +
                                          ") exceeds the allowed range (0-4). "
                                          "It was set to 4 (full logging).";
                    level = 4;
                } else if (level < 0) {
                    X3CFLUX_INFO() << "Given log level (" + std::to_string(level) +
                                          ") exceeds the allowed range (0-4). "
                                          "It was set to 0 (no logging).";
                    level = 0;
                }
                LogDummy::level = 4 - level;
                auto boostLevel = static_cast<boost::log::trivial::severity_level>(LogDummy::level);
                boost::log::core::get()->set_filter(boost::log::trivial::severity >= boostLevel);
            });

    OMPDummy::numThreads = omp_get_max_threads();
    py::class_<OMPDummy>(m, "omp").def_property_static(
        "num_threads", [](py::object) { return OMPDummy::numThreads; },
        [](py::object, int numMaxThreads) {
            OMPDummy::numThreads = numMaxThreads;
            omp_set_num_threads(numMaxThreads);
        });

    addNetworkData(m);
    addParameterConstraints(m);
    addSubstrate(m);
    addMeasurements(m);
    addMeasurementConfiguration(m);
    addFluxMLParser(m);
    addParameterSpace(m);
    addLabelingNetwork(m);
    addSystemBuilder(m);
    addSimulator(m);
    addExceptions(m);
}
