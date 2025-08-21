#ifndef X3CFLUX_ADDSUBSTRATE_H
#define X3CFLUX_ADDSUBSTRATE_H

#include <model/data/Substrate.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static void addSubstrate(py::module &m) {
    py::class_<x3cflux::Substrate, std::shared_ptr<x3cflux::Substrate>>(m, "Substrate", "Base class for substrate data")
        .def_property_readonly("name", &x3cflux::Substrate::getName, "Identifier name")
        .def_property_readonly("metabolite_name", &x3cflux::Substrate::getMetaboliteName, "Name of the metabolite")
        .def_property_readonly("costs", &x3cflux::Substrate::getCosts, "Costs");

    py::class_<x3cflux::ConstantSubstrate, std::shared_ptr<x3cflux::ConstantSubstrate>, x3cflux::Substrate>(
        m, "ConstantSubstrate", "Substrate with time-constant fractional labeling")
        .def(py::init<std::string, std::string, x3cflux::Real,
                      const std::map<boost::dynamic_bitset<>, x3cflux::Real> &>(),
             py::arg("name"), py::arg("pool_name"), py::arg("costs"), py::arg("profiles"),
             "Creates time-constant substrate")
        .def_property_readonly("profiles", &x3cflux::ConstantSubstrate::getProfiles,
                               "Fractional enrichment of labeling patterns")
        .def(py::pickle(
            [](const x3cflux::ConstantSubstrate &substrate) {
                std::vector<std::tuple<unsigned long, std::size_t, x3cflux::Real>> profiles;
                for (const auto &profile : substrate.getProfiles()) {
                    profiles.emplace_back(profile.first.to_ulong(), profile.first.size(), profile.second);
                }

                return py::make_tuple(substrate.getName(), substrate.getMetaboliteName(), substrate.getCosts(),
                                      profiles);
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");
                std::map<boost::dynamic_bitset<>, x3cflux::Real> profiles;
                for (const auto &profile :
                     t[3].cast<std::vector<std::tuple<unsigned long, std::size_t, x3cflux::Real>>>()) {
                    profiles.emplace(std::piecewise_construct,
                                     std::forward_as_tuple(std::get<1>(profile), std::get<0>(profile)),
                                     std::forward_as_tuple(std::get<2>(profile)));
                }

                return x3cflux::ConstantSubstrate(t[0].cast<std::string>(), t[1].cast<std::string>(),
                                                  t[2].cast<x3cflux::Real>(), profiles);
            }));

    py::class_<x3cflux::VariateSubstrate, std::shared_ptr<x3cflux::VariateSubstrate>, x3cflux::Substrate>(
        m, "VariateSubstrate", "Substrate with time-variate fractional labeling")
        .def(py::init<std::string, std::string, x3cflux::Real,
                      const std::map<boost::dynamic_bitset<>, x3cflux::VariateProfile> &>(),
             py::arg("name"), py::arg("metabolite_name"), py::arg("costs"), py::arg("profiles"),
             "Create time-variate substrate")
        .def_property_readonly("profiles", &x3cflux::VariateSubstrate::getProfiles, "Profiles of fractional labeling")
        .def(py::pickle(
            [](const x3cflux::VariateSubstrate &substrate) {
                std::vector<std::tuple<unsigned long, std::size_t,
                                       std::vector<std::tuple<x3cflux::Real, x3cflux::Real, std::string>>>>
                    profiles;
                for (const auto &profile : substrate.getProfiles()) {
                    std::vector<std::tuple<x3cflux::Real, x3cflux::Real, std::string>> subProfiles;
                    subProfiles.reserve(profile.second.size());
                    for (const auto &subProfile : profile.second) {
                        subProfiles.emplace_back(std::get<0>(subProfile), std::get<1>(subProfile),
                                                 std::get<2>(subProfile).toString());
                    }

                    profiles.emplace_back(profile.first.to_ulong(), profile.first.size(), subProfiles);
                }

                return py::make_tuple(substrate.getName(), substrate.getMetaboliteName(), substrate.getCosts(),
                                      profiles);
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");
                std::map<boost::dynamic_bitset<>, x3cflux::VariateProfile> profiles;
                for (const auto &profile :
                     t[3].cast<std::vector<
                         std::tuple<unsigned long, std::size_t,
                                    std::vector<std::tuple<x3cflux::Real, x3cflux::Real, std::string>>>>>()) {
                    std::vector<std::tuple<x3cflux::Real, x3cflux::Real, flux::symb::ExprTree>> subProfiles;
                    for (const auto &subProfile : std::get<2>(profile)) {
                        subProfiles.emplace_back(std::get<0>(subProfile), std::get<1>(subProfile),
                                                 *flux::symb::ExprTree::parse(std::get<2>(subProfile).c_str()));
                    }

                    profiles.emplace(std::piecewise_construct,
                                     std::forward_as_tuple(std::get<1>(profile), std::get<0>(profile)),
                                     std::forward_as_tuple(subProfiles));
                }

                return x3cflux::VariateSubstrate(t[0].cast<std::string>(), t[1].cast<std::string>(),
                                                 t[2].cast<x3cflux::Real>(), profiles);
            }));
}

#endif // X3CFLUX_ADDSUBSTRATE_H
