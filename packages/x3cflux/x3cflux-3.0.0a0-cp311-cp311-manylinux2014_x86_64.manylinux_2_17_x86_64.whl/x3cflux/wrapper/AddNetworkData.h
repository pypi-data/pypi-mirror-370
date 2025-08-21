#ifndef X3CFLUX_ADDNETWORKDATA_H
#define X3CFLUX_ADDNETWORKDATA_H

#include <model/data/NetworkData.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static void addNetworkData(py::module &m) {
    py::enum_<x3cflux::TracerElement>(m, "TracerElement", "Traceable natural element")
        .value("Carbon", x3cflux::TracerElement::CARBON)
        .value("Nitrogen", x3cflux::TracerElement::NITROGEN)
        .value("Hydrogen", x3cflux::TracerElement::HYDROGEN)
        .value("Oxygen", x3cflux::TracerElement::OXYGEN)
        .export_values();

    py::class_<x3cflux::Metabolite>(m, "Metabolite", "Metabolite data class")
        .def(py::init<std::string, std::size_t, std::map<x3cflux::TracerElement, std::size_t>>(), R"pbdoc()pbdoc",
             py::arg("name"), py::arg("num_atoms"), py::arg("elems_num_atoms"), "Create metabolite")
        .def_property_readonly("name", &x3cflux::Metabolite::getName, "Metabolite name")
        .def_property_readonly("num_atoms", &x3cflux::Metabolite::getNumAtoms, "Number of traceable atoms")
        .def_property_readonly("num_isotopes", &x3cflux::Metabolite::getNumIsotopes,
                               "Numbers of atoms of each tracer element")
        .def(py::pickle(
            [](const x3cflux::Metabolite &metabolite) {
                return py::make_tuple(metabolite.getName(), metabolite.getNumAtoms(), metabolite.getNumIsotopes());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::Metabolite(t[0].cast<std::string>(), t[1].cast<std::size_t>(),
                                           t[2].cast<std::map<x3cflux::TracerElement, std::size_t>>());
            }));

    py::class_<x3cflux::Permutation>(m, "Permutation", "Atom permutation")
        .def(py::init<std::size_t>(), py::arg("num_indices"), "Create identical permutation")
        .def(py::init<std::valarray<std::size_t>>(), py::arg("perm_indices"), "Create permutation from indices")
        .def("__call__", &x3cflux::Permutation::operator(), py::arg("idx"), R"doc(
            Apply permutation to index

            :param int idx:
                Index to permute

            :return:
                permuted index
)doc")
        .def("__eq__", &x3cflux::Permutation::operator==, py::arg("other"), R"doc(
            Compare two permutations

            :param x3cflux.Permutation other:
                Other permutation to compare

            :return:
                True if permutations match, else False
)doc")
        .def_property_readonly("num_indices", &x3cflux::Permutation::getNumIndices, "Indices defining the permutation")
        .def(
            py::pickle([](const x3cflux::Permutation &permutation) { return py::make_tuple(permutation.getIndices()); },
                       [](py::tuple t) {
                           if (t.size() != 1)
                               throw std::runtime_error("Invalid state");
                           return x3cflux::Permutation(t[0].cast<std::valarray<std::size_t>>());
                       }));

    py::class_<x3cflux::Reaction>(m, "Reaction", "Reaction data class")
        .def(py::init<std::string, std::size_t, bool, x3cflux::Permutation, std::vector<std::string>,
                      std::vector<std::string>>(),
             py::arg("name"), py::arg("num_atoms"), py::arg("bidirectional"), py::arg("atom_permutation"),
             py::arg("educt_names"), py::arg("product_names"), "Create reaction")
        .def_property_readonly("name", &x3cflux::Reaction::getName, "Name of the reaction")
        .def_property_readonly("num_atoms", &x3cflux::Reaction::getNumAtoms, "Number of traceable atoms partaking")
        .def_property_readonly("bidirectional", &x3cflux::Reaction::isBidirectional, "Bidirectional or unidirectional")
        .def_property_readonly("atom_permutation", &x3cflux::Reaction::getAtomPermutation,
                               "Permutation of traceable atoms")
        .def_property_readonly("educt_names", &x3cflux::Reaction::getEductNames, "Names of reaction educts")
        .def_property_readonly("product_names", &x3cflux::Reaction::getProductNames, "Names of reaction products")
        .def(py::pickle(
            [](const x3cflux::Reaction &reaction) {
                return py::make_tuple(reaction.getName(), reaction.getNumAtoms(), reaction.isBidirectional(),
                                      reaction.getAtomPermutation(), reaction.getEductNames(),
                                      reaction.getProductNames());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::Reaction(t[0].cast<std::string>(), t[1].cast<std::size_t>(), t[2].cast<bool>(),
                                         t[3].cast<x3cflux::Permutation>(), t[4].cast<std::vector<std::string>>(),
                                         t[5].cast<std::vector<std::string>>());
            }));

    py::class_<x3cflux::NetworkData>(m, "NetworkData", "Network and atom transition data class")
        .def(py::init<std::vector<x3cflux::Metabolite>, std::vector<x3cflux::Reaction>>(), py::arg("metabolites"),
             py::arg("reactions"), "Create network data")
        .def_property_readonly("metabolites", &x3cflux::NetworkData::getMetabolites, "metabolite data")
        .def_property_readonly("reactions", &x3cflux::NetworkData::getReactions, "reaction data")
        .def(py::pickle(
            [](const x3cflux::NetworkData &networkData) {
                return py::make_tuple(networkData.getMetabolites(), networkData.getReactions());
            },
            [](py::tuple t) {
                if (t.size() != 2)
                    throw std::runtime_error("Invalid state");
                return x3cflux::NetworkData(t[0].cast<std::vector<x3cflux::Metabolite>>(),
                                            t[1].cast<std::vector<x3cflux::Reaction>>());
            }));
}

#endif // X3CFLUX_ADDNETWORKDATA_H