#ifndef X3CFLUX_MEASUREMENTCONVERTER_H
#define X3CFLUX_MEASUREMENTCONVERTER_H

#include "CumomerMethod.h"
#include "EMUMethod.h"
#include <model/data/Measurement.h>

template <class CastType, typename StoreType> static bool isInstanceOf(const std::shared_ptr<StoreType> &pointer) {
    return std::dynamic_pointer_cast<CastType>(pointer) != nullptr;
}

namespace x3cflux {

/// \brief Default measurement converter (cannot be used)
/// \tparam T modeling method
///
/// For certain state variables labeling networks can be reduced based
/// on their state type. To do so the state variables identified by measurement
/// need to be extracted using the underlying modeling method.
template <typename T> struct MeasurementConverter;

/// \brief Measurement converter check (default false)
/// \tparam T modeling method
///
/// Check should be implemented for types that have a
/// sensible measurement converter implementation.
template <typename T> struct HasMeasurementConverter : public std::false_type {};

/// \brief Measurement converter implementation for the Cumomer method
template <> struct MeasurementConverter<CumomerMethod> {
    typedef typename CumomerMethod::StateType State;

    /// \param mask measured atom positions
    /// \return Cumomer state variables
    static std::vector<State> getMSStates(const State &mask) {
        std::size_t numAtoms = mask.size(), numFragmentAtoms = mask.count(), numStates = 1 << mask.count();

        // Calculate labeling patterns, omit 0-cumomer
        std::vector<State> states;
        for (std::size_t labelingIndex = 1; labelingIndex < numStates; ++labelingIndex) {
            boost::dynamic_bitset<> labeling(numAtoms, false);

            // Insert fragment cumomer labeling into measured positions
            boost::dynamic_bitset<> fragmentLabeling(numFragmentAtoms, labelingIndex);
            std::size_t measuredPos = mask.find_first();
            for (std::size_t fragmentPos = 0; fragmentPos < numFragmentAtoms; ++fragmentPos) {
                labeling[measuredPos] = fragmentLabeling[fragmentPos];
                measuredPos = mask.find_next(measuredPos);
            }

            states.emplace_back(labeling);
        }

        return states;
    }

    /// \param mask measured atom positions
    /// \return Cumomer state variables
    static std::vector<State> getMIMSStates(const State &mask) { return getMSStates(mask); }

    /// \param firstMask measured atom positions of parent
    /// \param secondMask measured atom positions of child
    /// \return Cumomer state variables
    static std::vector<State> getMSMSStates(const State &firstMask, const State &secondMask) {
        std::ignore = secondMask;
        return getMSStates(firstMask);
    }

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \return Cumomer state variables
    static std::vector<State> getHNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions) {
        std::vector<State> states;

        for (const auto &position : atomPositions) {
            states.emplace_back(numAtoms, false);
            states.back().set(position - 1);
        }

        return states;
    }

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \param types labeling neighborhood information
    /// \return Cumomer state variables
    static std::vector<State> getCNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions,
                                            const std::vector<CNMRSpecification::CNMRType> &types) {
        std::vector<State> states;

        for (std::size_t posIndex = 0; posIndex < atomPositions.size(); ++posIndex) {
            std::size_t position = atomPositions[posIndex] - 1; // todo: fix list indices to be 0-based
            boost::dynamic_bitset<> state(numAtoms);

            switch (types[posIndex]) {
            case CNMRSpecification::CNMRType::SINGLET: {
                // ..010.. = ..x1x.. - ..11x.. - ..x11.. + ..111..
                state.set(position);
                states.push_back(state);

                if (position > 0) {
                    state.set(position - 1);
                    states.push_back(state);
                }

                if (numAtoms > position + 1) {
                    state.set(position + 1);
                    states.push_back(state);

                    if (position > 0) {
                        state.reset(position - 1);
                        states.push_back(state);
                    }
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                X3CFLUX_CHECK(position != 0);

                // ..110.. = ..11x.. - 111
                state.set(position);
                state.set(position - 1);
                states.push_back(state);

                if (numAtoms > position + 1) {
                    state.set(position + 1);
                    states.push_back(state);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                X3CFLUX_CHECK(position != numAtoms - 1);

                // ..011.. = ..x11.. - 111
                state.set(position);
                state.set(position + 1);
                states.push_back(state);

                if (position > 0) {
                    state.set(position - 1);
                    states.push_back(state);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
            case CNMRSpecification::CNMRType::TRIPLETS: {
                X3CFLUX_CHECK(numAtoms >= 3 and position != 0 and position != numAtoms - 1);

                state.set(position - 1);
                state.set(position);
                state.set(position + 1);
                states.push_back(state);
            } break;
            }
        }

        return states;
    }

    /// \param labeledMask surely labeled atom positions
    /// \param wildcardMask not surely labeled atom positions
    /// \return Cumomer state variables
    static std::vector<State> getCumomerStates(const State &labeledMask, const State &wildcardMask) {
        return getMSStates(labeledMask | ~(labeledMask | wildcardMask));
    }

    /// Calculate Cumomer state variables from measurement setup information.
    /// \param measurement metabolite labeling measurement
    /// \return Cumomer state variables
    static std::vector<State> calculateStates(const std::shared_ptr<LabelingMeasurement> &measurement) {
        if (isInstanceOf<MSMeasurement>(measurement)) {
            auto msMeasurement = std::dynamic_pointer_cast<MSMeasurement>(measurement);
            return getMSStates(msMeasurement->getSpecification().getMask());
        } else if (isInstanceOf<MIMSMeasurement>(measurement)) {
            auto mimsMeasurement = std::dynamic_pointer_cast<MIMSMeasurement>(measurement);
            return getMIMSStates(mimsMeasurement->getSpecification().getMask());
        } else if (isInstanceOf<MSMSMeasurement>(measurement)) {
            auto msmsMeasurement = std::dynamic_pointer_cast<MSMSMeasurement>(measurement);
            const auto &specification = msmsMeasurement->getSpecification();
            return getMSMSStates(specification.getFirstMask(), specification.getSecondMask());
        } else if (isInstanceOf<HNMRMeasurement>(measurement)) {
            auto hnmrMeasurement = std::dynamic_pointer_cast<HNMRMeasurement>(measurement);
            return getHNMRStates(hnmrMeasurement->getNumAtoms(),
                                 hnmrMeasurement->getSpecification().getAtomPositions());
        } else if (isInstanceOf<CNMRMeasurement>(measurement)) {
            auto cnmrMeasurement = std::dynamic_pointer_cast<CNMRMeasurement>(measurement);
            const auto &specification = cnmrMeasurement->getSpecification();
            return getCNMRStates(cnmrMeasurement->getNumAtoms(), specification.getAtomPositions(),
                                 specification.getTypes());
        } else if (isInstanceOf<CumomerMeasurement>(measurement)) {
            auto cumomerMeasurement = std::dynamic_pointer_cast<CumomerMeasurement>(measurement);
            const auto &specification = cumomerMeasurement->getSpecification();
            return getCumomerStates(specification.getLabeledMask(), specification.getWildcardMask());
        }

        X3CFLUX_THROW(std::logic_error, "Unknown measurement type passed");
    }
};

/// \brief Measurement converter check for Cumomer method
template <> struct HasMeasurementConverter<CumomerMethod> : public std::true_type {};

/// \brief Measurement converter implementation for EMU method
template <> struct MeasurementConverter<EMUMethod> {
    typedef typename EMUMethod::StateType State;

    /// \param mask measured atom positions
    /// \return EMU state variables
    static std::vector<State> getMSStates(const State &mask) {
        std::vector<State> states;

        states.push_back(mask);
        return states;
    }

    /// \param mask measured atom positions
    /// \return EMU state variables
    static std::vector<State> getMIMSStates(const State &mask) {
        std::size_t numAtoms = mask.size(), numFragmentAtoms = mask.count(), numStates = 1 << mask.count();

        // Calculate labeling patterns, omit 0-EMU
        std::vector<State> states;
        for (std::size_t labelingIndex = 1; labelingIndex < numStates; ++labelingIndex) {
            boost::dynamic_bitset<> labeling(numAtoms, false);

            // Insert fragment EMU labeling into measured positions
            boost::dynamic_bitset<> fragmentLabeling(numFragmentAtoms, labelingIndex);
            std::size_t measuredPos = mask.find_first();
            for (std::size_t fragmentPos = 0; fragmentPos < numFragmentAtoms; ++fragmentPos) {
                labeling[measuredPos] = fragmentLabeling[fragmentPos];
                measuredPos = mask.find_next(measuredPos);
            }

            states.emplace_back(labeling);
        }

        return states;
    }

    /// \param firstMask measured atom positions of parent
    /// \param secondMask measured atom positions of child
    /// \return EMU state variables
    static std::vector<State> getMSMSStates(const State &firstMask, const State &secondMask) {
        std::ignore = secondMask;

        std::size_t numAtoms = firstMask.size(), numFragmentAtoms = firstMask.count(),
                    numStates = 1 << firstMask.count();

        // Calculate labeling patterns, omit 0-EMU
        std::vector<State> states;
        for (std::size_t labelingIndex = 1; labelingIndex < numStates; ++labelingIndex) {
            boost::dynamic_bitset<> labeling(numAtoms, false);

            // Insert fragment EMU labeling into measured positions
            boost::dynamic_bitset<> fragmentLabeling(numFragmentAtoms, labelingIndex);
            std::size_t measuredPos = firstMask.find_first();
            for (std::size_t fragmentPos = 0; fragmentPos < numFragmentAtoms; ++fragmentPos) {
                labeling[measuredPos] = fragmentLabeling[fragmentPos];
                measuredPos = firstMask.find_next(measuredPos);
            }

            states.emplace_back(labeling);
        }

        return states;
    }

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \return EMU state variables
    static std::vector<State> getHNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions) {
        std::vector<State> states;

        for (const auto &position : atomPositions) {
            states.emplace_back(numAtoms, false);
            states.back().set(position - 1);
        }

        return states;
    }

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \param types labeling neighborhood information
    /// \return EMU state variables
    static std::vector<State> getCNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions,
                                            const std::vector<CNMRSpecification::CNMRType> &types) {
        std::vector<State> states;

        for (std::size_t posIndex = 0; posIndex < atomPositions.size(); ++posIndex) {
            std::size_t position = atomPositions[posIndex] - 1; // todo: fix list indices to be 0-based
            boost::dynamic_bitset<> state(numAtoms);

            switch (types[posIndex]) {
            case CNMRSpecification::CNMRType::SINGLET: {
                // ..010.. = ..x1x.. - ..11x.. - ..x11.. + ..111..
                state.set(position);
                states.push_back(state);

                if (position > 0) {
                    state.set(position - 1);
                    states.push_back(state);
                }

                if (numAtoms > position + 1) {
                    state.set(position + 1);
                    states.push_back(state);

                    if (position > 0) {
                        state.reset(position - 1);
                        states.push_back(state);
                    }
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                X3CFLUX_CHECK(position != 0);

                // ..110.. = ..11x.. - 111
                state.set(position);
                state.set(position - 1);
                states.push_back(state);

                if (numAtoms > position + 1) {
                    state.set(position + 1);
                    states.push_back(state);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                X3CFLUX_CHECK(position != numAtoms - 1);

                // ..011.. = ..x11.. - 111
                state.set(position);
                state.set(position + 1);
                states.push_back(state);

                if (position > 0) {
                    state.set(position - 1);
                    states.push_back(state);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
            case CNMRSpecification::CNMRType::TRIPLETS: {
                X3CFLUX_CHECK(numAtoms >= 3 and position != 0 and position != numAtoms - 1);

                state.set(position - 1);
                state.set(position);
                state.set(position + 1);
                states.push_back(state);
            } break;
            }
        }

        return states;
    }

    /// \param labeledMask surely labeled atom positions
    /// \param wildcardMask not surely labeled atom positions
    /// \return EMU state variables
    static std::vector<State> getCumomerStates(const State &labeledMask, const State &wildcardMask) {
        auto mask = labeledMask | ~(labeledMask | wildcardMask);
        std::size_t numAtoms = mask.size(), numFragmentAtoms = mask.count(), numStates = 1 << mask.count();

        // Calculate labeling patterns, omit 0-EMU
        std::vector<State> states;
        for (std::size_t labelingIndex = 1; labelingIndex < numStates; ++labelingIndex) {
            boost::dynamic_bitset<> labeling(numAtoms, false);

            // Insert fragment EMU labeling into measured positions
            boost::dynamic_bitset<> fragmentLabeling(numFragmentAtoms, labelingIndex);
            std::size_t measuredPos = mask.find_first();
            for (std::size_t fragmentPos = 0; fragmentPos < numFragmentAtoms; ++fragmentPos) {
                labeling[measuredPos] = fragmentLabeling[fragmentPos];
                measuredPos = mask.find_next(measuredPos);
            }

            states.emplace_back(labeling);
        }

        return states;
    }

    /// Calculate EMU state variables from measurement setup information.
    /// \param measurement metabolite labeling measurement
    /// \return EMU state variables
    static std::vector<State> calculateStates(const std::shared_ptr<LabelingMeasurement> &measurement) {
        if (isInstanceOf<MSMeasurement>(measurement)) {
            auto msMeasurement = std::dynamic_pointer_cast<MSMeasurement>(measurement);
            return getMSStates(msMeasurement->getSpecification().getMask());
        } else if (isInstanceOf<MIMSMeasurement>(measurement)) {
            auto mimsMeasurement = std::dynamic_pointer_cast<MIMSMeasurement>(measurement);
            return getMIMSStates(mimsMeasurement->getSpecification().getMask());
        } else if (isInstanceOf<MSMSMeasurement>(measurement)) {
            auto msmsMeasurement = std::dynamic_pointer_cast<MSMSMeasurement>(measurement);
            const auto &specification = msmsMeasurement->getSpecification();
            return getMSMSStates(specification.getFirstMask(), specification.getSecondMask());
        } else if (isInstanceOf<HNMRMeasurement>(measurement)) {
            auto hnmrMeasurement = std::dynamic_pointer_cast<HNMRMeasurement>(measurement);
            return getHNMRStates(hnmrMeasurement->getNumAtoms(),
                                 hnmrMeasurement->getSpecification().getAtomPositions());
        } else if (isInstanceOf<CNMRMeasurement>(measurement)) {
            auto cnmrMeasurement = std::dynamic_pointer_cast<CNMRMeasurement>(measurement);
            const auto &specification = cnmrMeasurement->getSpecification();
            return getCNMRStates(cnmrMeasurement->getNumAtoms(), specification.getAtomPositions(),
                                 specification.getTypes());
        } else if (isInstanceOf<CumomerMeasurement>(measurement)) {
            auto cumomerMeasurement = std::dynamic_pointer_cast<CumomerMeasurement>(measurement);
            const auto &specification = cumomerMeasurement->getSpecification();
            return getCumomerStates(specification.getLabeledMask(), specification.getWildcardMask());
        }

        X3CFLUX_THROW(AssertionError, "Unknown measurement type passed");
    }
};

/// \brief Measurement converter check for EMU method
template <> struct HasMeasurementConverter<EMUMethod> : public std::true_type {};

} // namespace x3cflux

#endif // X3CFLUX_MEASUREMENTCONVERTER_H
