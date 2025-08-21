#ifndef X3CFLUX_ADDMEASUREMENTS_H
#define X3CFLUX_ADDMEASUREMENTS_H

#include <model/data/Measurement.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static void addMeasurements(py::module &m) {
    py::class_<x3cflux::Measurement, std::shared_ptr<x3cflux::Measurement>>(m, "Measurement",
                                                                            "Base class for measurement")
        .def_property_readonly("name", &x3cflux::Measurement::getName, "Name of the measurement")
        .def_property_readonly("auto_scalable", &x3cflux::Measurement::isAutoScalable, "Rescaling flag");

    py::class_<x3cflux::MeasurementDataSet>(m, "MeasurementDataSet",
                                            "Measured data with time stamps and standard deviations")
        .def(py::init<std::vector<x3cflux::Real>, std::vector<x3cflux::RealVector>, std::vector<x3cflux::RealVector>,
                      std::vector<flux::symb::ExprTree>>(),
             py::arg("time_stamps"), py::arg("values"), py::arg("standard_deviations"), py::arg("error_models"),
             "Create measurement data")
        .def_property_readonly("time_stamps", &x3cflux::MeasurementDataSet::getTimeStamps, "Measurement time points")
        .def_property_readonly("values", &x3cflux::MeasurementDataSet::getValues, "Measured values")
        .def_property_readonly("standard_deviations", &x3cflux::MeasurementDataSet::getStandardDeviations,
                               "Standard deviation of each value")
        .def_property_readonly("error_models", &x3cflux::MeasurementDataSet::getErrorModels, "Statistical error models")
        .def(py::pickle(
            [](const x3cflux::MeasurementDataSet &dataSet) {
                std::vector<std::string> errorModels;
                for (const auto &expr : dataSet.getErrorModels()) {
                    errorModels.push_back(expr.toString());
                }

                return py::make_tuple(dataSet.getTimeStamps(), dataSet.getValues(), dataSet.getStandardDeviations(),
                                      errorModels);
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");

                std::vector<flux::symb::ExprTree> errorModels;
                for (const auto &exprString : t[3].cast<std::vector<std::string>>()) {
                    errorModels.push_back(*flux::symb::ExprTree::parse(exprString.c_str()));
                }

                return x3cflux::MeasurementDataSet(t[0].cast<std::vector<x3cflux::Real>>(),
                                                   t[1].cast<std::vector<x3cflux::RealVector>>(),
                                                   t[2].cast<std::vector<x3cflux::RealVector>>(), errorModels);
            }));

    py::class_<x3cflux::LabelingMeasurement, std::shared_ptr<x3cflux::LabelingMeasurement>, x3cflux::Measurement>(
        m, "LabelingMeasurement", "Base class for labeling measurements")
        .def_property_readonly("metabolite_name", &x3cflux::LabelingMeasurement::getMetaboliteName,
                               "Name of the measured metabolite")
        .def_property_readonly("num_atoms", &x3cflux::LabelingMeasurement::getNumAtoms,
                               "Number of traceable atoms in the metabolite")
        .def_property_readonly("data", &x3cflux::LabelingMeasurement::getData, "Measurement data");

    py::class_<x3cflux::MSSpecification>(m, "MSSpecification", "Specification of MS measurement")
        .def(py::init<boost::dynamic_bitset<>, std::vector<std::size_t>>(), py::arg("mask"), py::arg("weights"),
             "Create MS measurement specification")
        .def_property_readonly("mask", &x3cflux::MSSpecification::getMask, "Mask of considered carbon atoms")
        .def_property_readonly("weights", &x3cflux::MSSpecification::getWeights, "Measured weights")
        .def(py::pickle(
            [](const x3cflux::MSSpecification &specification) {
                return py::make_tuple(specification.getMask().to_ulong(), specification.getMask().size(),
                                      specification.getWeights());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MSSpecification(
                    boost::dynamic_bitset<>(t[1].cast<std::size_t>(), t[0].cast<unsigned long>()),
                    t[2].cast<std::vector<std::size_t>>());
            }));

    py::class_<x3cflux::MSMeasurement, std::shared_ptr<x3cflux::MSMeasurement>, x3cflux::LabelingMeasurement>(
        m, "MSMeasurement", "Mass spectrometry measurement")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::MSSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create MS measurement")
        .def_property_readonly("specification", &x3cflux::MSMeasurement::getSpecification, "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::MSMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MSMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(),
                                              t[3].cast<std::size_t>(), t[4].cast<x3cflux::MSSpecification>(),
                                              t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::MIMSSpecification>(m, "MIMSSpecification", "Specification of MIMS measurement")
        .def(py::init<boost::dynamic_bitset<>, std::vector<std::vector<std::size_t>>>(), py::arg("mask"),
             py::arg("weights"), "Create MIMS measurement specification")
        .def_property_readonly("mask", &x3cflux::MIMSSpecification::getMask, "Mask of considered atom positions")
        .def_property_readonly("weights", &x3cflux::MIMSSpecification::getWeights, "Measured weights")
        .def(py::pickle(
            [](const x3cflux::MIMSSpecification &specification) {
                return py::make_tuple(specification.getMask().to_ulong(), specification.getMask().size(),
                                      specification.getWeights());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MIMSSpecification(
                    boost::dynamic_bitset<>(t[1].cast<std::size_t>(), t[0].cast<unsigned long>()),
                    t[2].cast<std::vector<std::vector<std::size_t>>>());
            }));

    py::class_<x3cflux::MIMSMeasurement, std::shared_ptr<x3cflux::MIMSMeasurement>, x3cflux::LabelingMeasurement>(
        m, "MIMSMeasurement", "Multi-Isotope mass spectrometry measurement")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::MIMSSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create MIMS measurement")
        .def_property_readonly("specification", &x3cflux::MIMSMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::MIMSMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MIMSMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(),
                                                t[3].cast<std::size_t>(), t[4].cast<x3cflux::MIMSSpecification>(),
                                                t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::MSMSSpecification>(m, "MSMSSpecification", "Specification of MSMS measurement")
        .def(py::init<boost::dynamic_bitset<>, boost::dynamic_bitset<>, std::vector<std::size_t>,
                      std::vector<std::size_t>>(),
             py::arg("first_mask"), py::arg("second_mask"), py::arg("first_weights"), py::arg("second_weights"),
             "Create MSMS measurement specification")
        .def_property_readonly("first_mask", &x3cflux::MSMSSpecification::getFirstMask,
                               "Mask of considered pre-cursor carbon atoms")
        .def_property_readonly("second_mask", &x3cflux::MSMSSpecification::getSecondMask,
                               "Mask of considered cursor carbon atoms")
        .def_property_readonly("first_weights", &x3cflux::MSMSSpecification::getFirstWeights,
                               "Measured pre-cursor weights")
        .def_property_readonly("second_weights", &x3cflux::MSMSSpecification::getSecondWeights,
                               "Measured cursor weights")
        .def(py::pickle(
            [](const x3cflux::MSMSSpecification &specification) {
                return py::make_tuple(specification.getFirstMask().to_ulong(), specification.getFirstMask().size(),
                                      specification.getSecondMask().to_ulong(), specification.getSecondMask().size(),
                                      specification.getFirstWeights(), specification.getSecondWeights());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MSMSSpecification(
                    boost::dynamic_bitset<>(t[1].cast<std::size_t>(), t[0].cast<unsigned long>()),
                    boost::dynamic_bitset<>(t[3].cast<std::size_t>(), t[2].cast<unsigned long>()),
                    t[4].cast<std::vector<std::size_t>>(), t[5].cast<std::vector<std::size_t>>());
            }));

    py::class_<x3cflux::MSMSMeasurement, std::shared_ptr<x3cflux::MSMSMeasurement>, x3cflux::LabelingMeasurement>(
        m, "MSMSMeasurement", "Tandem mass spectrometry measurement")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::MSMSSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create MSMS measurement")
        .def_property_readonly("specification", &x3cflux::MSMSMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::MSMSMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::MSMSMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(),
                                                t[3].cast<std::size_t>(), t[4].cast<x3cflux::MSMSSpecification>(),
                                                t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::HNMRSpecification>(m, "HNMRSpecification", "Specification of 1H-NMR measurement")
        .def(py::init<std::vector<std::size_t>>(), py::arg("atom_positions"))
        .def_property_readonly("atom_positions", &x3cflux::HNMRSpecification::getAtomPositions,
                               "Measured carbon positions")
        .def(py::pickle(
            [](const x3cflux::HNMRSpecification &specification) {
                return py::make_tuple(specification.getAtomPositions());
            },
            [](py::tuple t) {
                if (t.size() != 1)
                    throw std::runtime_error("Invalid state");
                return x3cflux::HNMRSpecification(t[0].cast<std::vector<std::size_t>>());
            }));

    py::class_<x3cflux::HNMRMeasurement, std::shared_ptr<x3cflux::HNMRMeasurement>, x3cflux::LabelingMeasurement>(
        m, "HNMRMeasurement", "Nuclear magnetic resonance measurement with 1H")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::HNMRSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create 1H-NMR")
        .def_property_readonly("specification", &x3cflux::HNMRMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::HNMRMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::HNMRMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(),
                                                t[3].cast<std::size_t>(), t[4].cast<x3cflux::HNMRSpecification>(),
                                                t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::CNMRSpecification> cnmrSpecification(m, "CNMRSpecification",
                                                             "Specification for 13C-NMR measurement");
    cnmrSpecification
        .def(py::init<std::vector<std::size_t>, std::vector<x3cflux::CNMRSpecification::CNMRType>>(),
             py::arg("atom_positions"), py::arg("types"))
        .def_property_readonly("atom_positions", &x3cflux::CNMRSpecification::getAtomPositions,
                               "Measured carbon positions")
        .def_property_readonly("types", &x3cflux::CNMRSpecification::getTypes, "Observed peak types")
        .def(py::pickle(
            [](const x3cflux::CNMRSpecification &specification) {
                return py::make_tuple(specification.getAtomPositions(), specification.getTypes());
            },
            [](py::tuple t) {
                if (t.size() != 2)
                    throw std::runtime_error("Invalid state");
                return x3cflux::CNMRSpecification(t[0].cast<std::vector<std::size_t>>(),
                                                  t[1].cast<std::vector<x3cflux::CNMRSpecification::CNMRType>>());
            }));

    py::enum_<x3cflux::CNMRSpecification::CNMRType>(cnmrSpecification, "CNMRType", "Peak type of 13C-NMR measurement")
        .value("Singlet", x3cflux::CNMRSpecification::CNMRType::SINGLET)
        .value("DoubletLeft", x3cflux::CNMRSpecification::CNMRType::DOUBLET_LEFT)
        .value("DoubletRight", x3cflux::CNMRSpecification::CNMRType::DOUBLET_RIGHT)
        .value("DoubletOfDoublets", x3cflux::CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS)
        .value("Triplets", x3cflux::CNMRSpecification::CNMRType::TRIPLETS)
        .export_values();

    py::class_<x3cflux::CNMRMeasurement, std::shared_ptr<x3cflux::CNMRMeasurement>, x3cflux::LabelingMeasurement>(
        m, "CNMRMeasurement", "Nuclear magnetic resonance measurement with 13C")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::CNMRSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create 13C-NMR measurement")
        .def_property_readonly("specification", &x3cflux::CNMRMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::CNMRMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::CNMRMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(),
                                                t[3].cast<std::size_t>(), t[4].cast<x3cflux::CNMRSpecification>(),
                                                t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::CumomerSpecification>(m, "CumomerSpecification", "Specification of Cumomer measurement")
        .def(py::init<boost::dynamic_bitset<>, boost::dynamic_bitset<>>(), py::arg("labeled_mask"),
             py::arg("wildcard_mask"))
        .def_property_readonly("labeled_mask", &x3cflux::CumomerSpecification::getLabeledMask, "Labeled atom positions")
        .def_property_readonly("wildcard_mask", &x3cflux::CumomerSpecification::getWildcardMask,
                               "Labeled or non-labeled atom positions")
        .def(py::pickle(
            [](const x3cflux::CumomerSpecification &specification) {
                return py::make_tuple(specification.getLabeledMask().to_ulong(), specification.getLabeledMask().size(),
                                      specification.getWildcardMask().to_ulong(),
                                      specification.getWildcardMask().size());
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");
                return x3cflux::CumomerSpecification(
                    boost::dynamic_bitset<>(t[1].cast<std::size_t>(), t[0].cast<unsigned long>()),
                    boost::dynamic_bitset<>(t[3].cast<std::size_t>(), t[2].cast<unsigned long>()));
            }));

    py::class_<x3cflux::CumomerMeasurement, std::shared_ptr<x3cflux::CumomerMeasurement>, x3cflux::LabelingMeasurement>(
        m, "CumomerMeasurement", R"doc(
            Artificial state variable measurement

            Can be used to specify measurements of Isotopomer and Cumomer states. Cumomer states can also be specified with fixed
            labeled and unlabeled positions.
    )doc")
        .def(py::init<std::string, bool, std::string, std::size_t, x3cflux::CumomerSpecification,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("metabolite_name"), py::arg("num_atoms"),
             py::arg("specification"), py::arg("data"), "Create state variable measurement")
        .def_property_readonly("specification", &x3cflux::CumomerMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::CumomerMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMetaboliteName(), measurement.getNumAtoms(),
                                      measurement.getSpecification(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 6)
                    throw std::runtime_error("Invalid state");
                return x3cflux::CumomerMeasurement(
                    t[0].cast<std::string>(), t[1].cast<bool>(), t[2].cast<std::string>(), t[3].cast<std::size_t>(),
                    t[4].cast<x3cflux::CumomerSpecification>(), t[5].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::ParameterMeasurement, std::shared_ptr<x3cflux::ParameterMeasurement>, x3cflux::Measurement>(
        m, "ParameterMeasurement",
        R"doc(
    Base class for parameter measurements

    Parameter measurements are defined by measurement formula. In its simplest case, the formula only states the name of one measured
    metabolic parameter. However, it is also possible to enter arbitrarily complex (differentiable) formulas containing the names of
    multiple metabolic parameters.
    )doc")
        .def_property_readonly("measurement_formula", &x3cflux::ParameterMeasurement::getMeasurementFormula,
                               "Formula describing the measurement")
        .def_property_readonly("value", &x3cflux::ParameterMeasurement::getValue, "Measured value")
        .def_property_readonly("standard_deviation", &x3cflux::ParameterMeasurement::getStandardDeviation,
                               "Standard of the measurement")
        .def_property_readonly("error_model", &x3cflux::ParameterMeasurement::getErrorModel, "Statistical error model");

    py::class_<x3cflux::FluxSpecification>(m, "FluxSpecification", "Specification of flux measurement")
        .def(py::init<std::vector<std::string>, bool>(), py::arg("flux_names"), py::arg("net"),
             "Create flux measurement specification")
        .def_property_readonly("flux_names", &x3cflux::FluxSpecification::getFluxNames,
                               "Names of fluxes contained in measurement formula")
        .def_property_readonly("net", &x3cflux::FluxSpecification::isNet, "Netto or exchange flux measurement")
        .def(py::pickle(
            [](const x3cflux::FluxSpecification &specification) {
                return py::make_tuple(specification.getFluxNames(), specification.isNet());
            },
            [](py::tuple t) {
                if (t.size() != 2)
                    throw std::runtime_error("Invalid state");
                return x3cflux::FluxSpecification(t[0].cast<std::vector<std::string>>(), t[1].cast<bool>());
            }));

    py::class_<x3cflux::FluxMeasurement, std::shared_ptr<x3cflux::FluxMeasurement>, x3cflux::ParameterMeasurement>(
        m, "FluxMeasurement", "Measurement of metabolic fluxes")
        .def(py::init<std::string, bool, flux::symb::ExprTree, x3cflux::FluxSpecification, x3cflux::Real, x3cflux::Real,
                      flux::symb::ExprTree>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("measurement_formula"), py::arg("specification"),
             py::arg("value"), py::arg("standard_deviation"), py::arg("error_model"), "Create flux measurement")
        .def_property_readonly("specification", &x3cflux::FluxMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::FluxMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMeasurementFormula().toString(), measurement.getSpecification(),
                                      measurement.getValue(), measurement.getStandardDeviation(),
                                      measurement.getErrorModel().toString());
            },
            [](py::tuple t) {
                if (t.size() != 7)
                    throw std::runtime_error("Invalid state");
                return x3cflux::FluxMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(),
                                                *flux::symb::ExprTree::parse(t[2].cast<std::string>().c_str()),
                                                t[3].cast<x3cflux::FluxSpecification>(), t[4].cast<x3cflux::Real>(),
                                                t[5].cast<x3cflux::Real>(),
                                                *flux::symb::ExprTree::parse(t[6].cast<std::string>().c_str()));
            }));

    py::class_<x3cflux::PoolSizeSpecification>(m, "PoolSizeSpecification", "Specification of pool size measurement")
        .def(py::init<std::vector<std::string>>(), py::arg("pool_names"), "Create pool size measurement specification")
        .def_property_readonly("pool_names", &x3cflux::PoolSizeSpecification::getPoolNames,
                               "Names of metabolic pools contained in measurement formula")
        .def(py::pickle(
            [](const x3cflux::PoolSizeSpecification &specification) {
                return py::make_tuple(specification.getPoolNames());
            },
            [](py::tuple t) {
                if (t.size() != 1)
                    throw std::runtime_error("Invalid state");
                return x3cflux::PoolSizeSpecification(t[0].cast<std::vector<std::string>>());
            }));

    py::class_<x3cflux::PoolSizeMeasurement, std::shared_ptr<x3cflux::PoolSizeMeasurement>,
               x3cflux::ParameterMeasurement>(m, "PoolSizeMeasurement", "Measurement of metabolic pool sizes")
        .def(py::init<std::string, bool, flux::symb::ExprTree, x3cflux::PoolSizeSpecification, x3cflux::Real,
                      x3cflux::Real, flux::symb::ExprTree>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("measurement_formula"), py::arg("specification"),
             py::arg("value"), py::arg("standard_deviation"), py::arg("error_model"),
             "Create metabolite pool size measurement")
        .def_property_readonly("specification", &x3cflux::PoolSizeMeasurement::getSpecification,
                               "Measurement specification")
        .def(py::pickle(
            [](const x3cflux::PoolSizeMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getMeasurementFormula().toString(), measurement.getSpecification(),
                                      measurement.getValue(), measurement.getStandardDeviation(),
                                      measurement.getErrorModel().toString());
            },
            [](py::tuple t) {
                if (t.size() != 7)
                    throw std::runtime_error("Invalid state");
                return x3cflux::PoolSizeMeasurement(t[0].cast<std::string>(), t[1].cast<bool>(),
                                                    *flux::symb::ExprTree::parse(t[2].cast<std::string>().c_str()),
                                                    t[3].cast<x3cflux::PoolSizeSpecification>(),
                                                    t[4].cast<x3cflux::Real>(), t[5].cast<x3cflux::Real>(),
                                                    *flux::symb::ExprTree::parse(t[6].cast<std::string>().c_str()));
            }));

    py::class_<x3cflux::GenericMeasurement, std::shared_ptr<x3cflux::GenericMeasurement>, x3cflux::Measurement>
        genericMeasurement(m, "GenericMeasurement", R"doc(
            Combinations of labeling measurements

            Suitable if observed labeling measurements are actually composed of multiple measurements. This is e.g. the case
            for Leucin and Isoleucin, whose MS peaks are hard to differentiate. Instead of specifying two noisy measurements, generic
            measurements allow to specify one appropriate measurement.

            Generic measurements are specified in multiple components. These components are called sub-measurements and are defined
            by a measurement formula containing references to scalar labeling measurements. By specifying multiple sub-measurements,
            it is possible to define combinations of vector-valued labeling measurements (e.g. when combining MS measurements).
    )doc");
    genericMeasurement
        .def(py::init<std::string, bool, std::vector<x3cflux::GenericMeasurement::SubMeasurement>,
                      x3cflux::MeasurementDataSet>(),
             py::arg("name"), py::arg("auto_scaling"), py::arg("sub_measurements"), py::arg("data"),
             "Create generic measurement")
        .def_property_readonly("sub_measurements", &x3cflux::GenericMeasurement::getSubMeasurements,
                               "Component measurements")
        .def_property_readonly("data", &x3cflux::GenericMeasurement::getData, "Measurement data")
        .def(py::pickle(
            [](const x3cflux::GenericMeasurement &measurement) {
                return py::make_tuple(measurement.getName(), measurement.isAutoScalable(),
                                      measurement.getSubMeasurements(), measurement.getData());
            },
            [](py::tuple t) {
                if (t.size() != 4)
                    throw std::runtime_error("Invalid state");
                return x3cflux::GenericMeasurement(
                    t[0].cast<std::string>(), t[1].cast<bool>(),
                    t[2].cast<std::vector<x3cflux::GenericMeasurement::SubMeasurement>>(),
                    t[3].cast<x3cflux::MeasurementDataSet>());
            }));

    py::class_<x3cflux::GenericMeasurement::SubMeasurement>(genericMeasurement, "SubMeasurement",
                                                            "Component of a generic measurement")
        .def(py::init<const flux::symb::ExprTree &, std::vector<std::string>,
                      std::vector<std::shared_ptr<x3cflux::LabelingMeasurement>>>(),
             py::arg("formula"), py::arg("variable_names"), py::arg("measurements"))
        .def_property_readonly("formula", &x3cflux::GenericMeasurement::SubMeasurement::getFormula,
                               "Formula describing the measurement")
        .def_property_readonly("variable_names", &x3cflux::GenericMeasurement::SubMeasurement::getVariableNames,
                               "Names representing labeling measurements in the formula")
        .def_property_readonly("measurements", &x3cflux::GenericMeasurement::SubMeasurement::getMeasurements,
                               "Labeling measurements contained in the formula")
        .def(py::pickle(
            [](const x3cflux::GenericMeasurement::SubMeasurement &measurement) {
                return py::make_tuple(measurement.getFormula().toString(), measurement.getVariableNames(),
                                      measurement.getMeasurements());
            },
            [](py::tuple t) {
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state");

                std::vector<std::shared_ptr<x3cflux::LabelingMeasurement>> measurements;
                for (auto meas : t[2].cast<std::vector<std::shared_ptr<x3cflux::LabelingMeasurement>>>()) {
                    measurements.emplace_back(dynamic_cast<x3cflux::LabelingMeasurement *>(meas->copy().release()));
                }

                return x3cflux::GenericMeasurement::SubMeasurement(
                    *flux::symb::ExprTree::parse(t[0].cast<std::string>().c_str(), et_lex_mm),
                    t[1].cast<std::vector<std::string>>(), measurements);
            }));
}

#endif // X3CFLUX_ADDMEASUREMENTS_H
