#ifndef X3CFLUX_ADDLABELINGNETWORK_H
#define X3CFLUX_ADDLABELINGNETWORK_H

#include <model/network/LabelingNetwork.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

template <typename Method> void addUnreducedNetwork(py::module &m) {
    typedef x3cflux::LabelingNetwork<Method> Network;

    auto type = std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU");
    auto name = type + "Network";
    py::class_<Network>(m, name.c_str(), ("Labeling network using " + type + " state variables").c_str());
}

template <typename Method> void addReducedNetwork(py::module &m) {
    typedef x3cflux::ReducedLabelingNetwork<Method> Network;

    auto type = std::string(std::is_same<Method, x3cflux::CumomerMethod>::value ? "Cumomer" : "EMU");
    auto name = std::string("Reduced") + type + "Network";
    py::class_<Network>(m, name.c_str(), ("Reduced labeling network using " + type + " state variables").c_str());
}

static void addLabelingNetwork(py::module &m) {
    addUnreducedNetwork<x3cflux::CumomerMethod>(m);
    addUnreducedNetwork<x3cflux::EMUMethod>(m);

    addReducedNetwork<x3cflux::CumomerMethod>(m);
    addReducedNetwork<x3cflux::EMUMethod>(m);
}

#endif // X3CFLUX_ADDLABELINGNETWORK_H
