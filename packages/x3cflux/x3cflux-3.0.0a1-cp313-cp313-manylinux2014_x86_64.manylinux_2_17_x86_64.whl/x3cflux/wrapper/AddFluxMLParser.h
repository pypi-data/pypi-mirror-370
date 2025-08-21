#ifndef X3CFLUX_ADDFLUXMLPARSER_H
#define X3CFLUX_ADDFLUXMLPARSER_H

#include <model/data/FluxMLParser.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

class PyFluxMLParser {
  private:
    x3cflux::FluxMLParser parser_;

  public:
    PyFluxMLParser() : parser_(x3cflux::FluxMLParser::getInstance()) {}

    [[nodiscard]] x3cflux::FluxMLData parse(const std::string &filePath) const { return parser_.parse(filePath); }
};

static void addFluxMLParser(py::module &m) {
    py::class_<x3cflux::FluxMLData>(m, "FluxMLData",
                                    R"doc(Data class containing all information for 13C-MFA

                                                           This particularly includes network structure and atom transitions, but also
                                                           measurement setup with substrate labeling, parameter constraints and labeling
                                                           measurements. Information corresponds to a FluxML file.)doc")
        .def(py::init<std::string, std::string, std::string, std::string, boost::posix_time::ptime,
                      x3cflux::NetworkData, std::vector<x3cflux::MeasurementConfiguration>>(),
             py::arg("name"), py::arg("modeler_name"), py::arg("version"), py::arg("comment"), py::arg("date"),
             py::arg("network_data"), py::arg("configurations"), R"doc(Creates )doc")
        .def_property_readonly("name", &x3cflux::FluxMLData::getName, "Model name")
        .def_property_readonly("modeler_name", &x3cflux::FluxMLData::getModelerName, "Name of the modeler")
        .def_property_readonly("version", &x3cflux::FluxMLData::getVersion, "Model version")
        .def_property_readonly("comment", &x3cflux::FluxMLData::getComment, "Comments to the model")
        .def_property_readonly("date", &x3cflux::FluxMLData::getDate, "Date and time of last edit")
        .def_property_readonly("network_data", &x3cflux::FluxMLData::getNetworkData,
                               "Network structure and atom transitions")
        .def_property_readonly("configurations", &x3cflux::FluxMLData::getConfigurations,
                               "13C measurement configurations");

    py::class_<PyFluxMLParser>(m, "FluxMLParser", "Parser object designed to parse FluxML files")
        .def(py::init(), "Create FluxMLParser")
        .def("parse", &PyFluxMLParser::parse, py::arg("file_path"), R"doc(
Parse FluxML data object from a given FluxML file

:param str file_path:
    File path of FluxML file
)doc");
}

#endif // X3CFLUX_ADDFLUXMLPARSER_H
