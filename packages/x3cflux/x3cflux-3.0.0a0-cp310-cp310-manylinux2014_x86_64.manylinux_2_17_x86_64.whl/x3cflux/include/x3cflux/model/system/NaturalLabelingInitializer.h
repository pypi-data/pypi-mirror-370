#ifndef X3CFLUX_NATURALLABELINGINITIALIZER_H
#define X3CFLUX_NATURALLABELINGINITIALIZER_H

#include <math/NumericTypes.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/IsotopomerMethod.h>
#include <model/network/MetaboliteNetwork.h>
#include <model/network/StateTransporter.h>

namespace x3cflux {

template <typename Method> struct NaturalLabelingInitializer;

template <> struct NaturalLabelingInitializer<IsotopomerMethod> {
    typedef StateVariableImpl<IsotopomerMethod::StateType> Isotopomer;

    static Real computeFraction(const Isotopomer &isotopomer, const std::map<TracerElement, std::size_t> &numIsotopes) {
        const static Real NATURAL_ABUNDANCE_CARBON = 0.01109;
        const static Real NATURAL_ABUNDANCE_NITROGEN = 0.00115;
        const static Real NATURAL_ABUNDANCE_HYDROGEN = 0.00368;
        const static Real NATURAL_ABUNDANCE_OXYGEN = 0.00205;

        const auto &state = isotopomer.getState();

        Real naturalFraction = 1.;
        std::size_t position = 0;
        std::size_t numLabeled, numAtoms;
        for (auto pair : numIsotopes) {
            numAtoms = pair.second;
            numLabeled = 0;
            for (std::size_t i = position; i < position + numAtoms; ++i) {
                if (state[i]) {
                    ++numLabeled;
                }
            }

            switch (pair.first) {
            case TracerElement::CARBON:
                naturalFraction *= std::pow(1. - NATURAL_ABUNDANCE_CARBON, numAtoms - numLabeled) *
                                   std::pow(NATURAL_ABUNDANCE_CARBON, numLabeled);
                break;
            case TracerElement::NITROGEN:
                naturalFraction *= std::pow(1. - NATURAL_ABUNDANCE_NITROGEN, numAtoms - numLabeled) *
                                   std::pow(NATURAL_ABUNDANCE_NITROGEN, numLabeled);
                break;
            case TracerElement::HYDROGEN:
                naturalFraction *= std::pow(1. - NATURAL_ABUNDANCE_HYDROGEN, numAtoms - numLabeled) *
                                   std::pow(NATURAL_ABUNDANCE_HYDROGEN, numLabeled);
                break;
            case TracerElement::OXYGEN:
                naturalFraction *= std::pow(1. - NATURAL_ABUNDANCE_OXYGEN, numAtoms - numLabeled) *
                                   std::pow(NATURAL_ABUNDANCE_OXYGEN, numLabeled);
                break;
            }

            position += numAtoms;
        }

        return naturalFraction;
    }

    template <typename Ordering>
    static RealVector computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering) {
        Index size = ordering.getNumStateVariables();

        RealVector initialValue(size);
        for (Index sysPos = 0; sysPos < size; ++sysPos) {
            auto isotopomer = ordering.getStateVariable(sysPos);
            const auto &poolInfo = network.getPoolInformation(isotopomer.getPoolIndex());
            initialValue[sysPos] = computeFraction(isotopomer, poolInfo.getNumIsotopes());
        }

        return initialValue;
    }
};

template <> struct NaturalLabelingInitializer<CumomerMethod> {
    typedef typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType Cumomer;
    typedef NaturalLabelingInitializer<IsotopomerMethod> IsotopomerNaturalLabeling;
    typedef typename IsotopomerNaturalLabeling::Isotopomer Isotopomer;

    static Real computeFraction(const Cumomer &cumomer, const std::map<TracerElement, std::size_t> &isotopesNumAtoms) {
        const auto &state = cumomer.getState();
        std::size_t numAtoms = state.size();

        // Get positions for which both labeled/not labeled is accepted
        std::vector<std::size_t> cumuPositions;
        for (std::size_t atomPos = 0; atomPos < numAtoms; ++atomPos) {
            if (not state[atomPos]) {
                cumuPositions.push_back(atomPos);
            }
        }

        // Calculate fraction value by adding fraction values of dependent isotopomers
        Real fractionValue = 0.;
        std::size_t numCumuLabeled = cumuPositions.size();
        std::size_t numCombinations = 1 << numCumuLabeled;
        for (std::size_t cumuLabelRaw = 0; cumuLabelRaw < numCombinations; ++cumuLabelRaw) {
            boost::dynamic_bitset<> cumuLabeling(numCumuLabeled, cumuLabelRaw);

            boost::dynamic_bitset<> isotopomerLabeling(state);
            for (std::size_t cumuIndex = 0; cumuIndex < numCumuLabeled; ++cumuIndex) {
                isotopomerLabeling[cumuPositions[cumuIndex]] = cumuLabeling[cumuIndex];
            }

            Isotopomer isotopomer(cumomer.getPoolIndex(), isotopomerLabeling);
            fractionValue += IsotopomerNaturalLabeling::computeFraction(isotopomer, isotopesNumAtoms);
        }

        return fractionValue;
    }

    template <typename Ordering>
    static RealVector computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering) {
        Index size = ordering.getNumStateVariables();

        RealVector initialValue(size);
        for (Index sysPos = 0; sysPos < size; ++sysPos) {
            auto cumomer = ordering.getStateVariable(sysPos);
            const auto &poolInfo = network.getPoolInformation(cumomer.getPoolIndex());
            initialValue[sysPos] = computeFraction(cumomer, poolInfo.getNumIsotopes());
        }

        return initialValue;
    }
};

template <> struct NaturalLabelingInitializer<EMUMethod> {
    typedef typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType EMU;
    typedef NaturalLabelingInitializer<IsotopomerMethod> IsotopomerNaturalLabeling;
    typedef typename IsotopomerNaturalLabeling::Isotopomer Isotopomer;

    static RealVector computeFraction(const EMU &emu, const std::map<TracerElement, std::size_t> &isotopesNumAtoms) {
        const auto &state = emu.getState();
        std::size_t numAtoms = state.size();
        Index emuSize = static_cast<Index>(state.count()) + 1;

        // Calculate EMU
        RealVector fractionValue = RealVector::Zero(emuSize);
        std::size_t numCombinations = 1 << numAtoms;
        for (std::size_t isoLabelRaw = 0; isoLabelRaw < numCombinations; ++isoLabelRaw) {
            boost::dynamic_bitset<> isotopomerLabeling(numAtoms, isoLabelRaw);
            Isotopomer isotopomer(emu.getPoolIndex(), isotopomerLabeling);

            fractionValue[static_cast<int>((state & isotopomerLabeling).count())] +=
                IsotopomerNaturalLabeling::computeFraction(isotopomer, isotopesNumAtoms);
        }

        return fractionValue;
    }

    template <typename Ordering>
    static RealMatrix computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering) {
        Index size = ordering.getNumStateVariables();

        RealMatrix initialValue(size, ordering.getLevel() + 1);
        for (Index sysPos = 0; sysPos < size; ++sysPos) {
            auto emu = ordering.getStateVariable(sysPos);
            const auto &poolInfo = network.getPoolInformation(emu.getPoolIndex());
            initialValue.row(sysPos) = computeFraction(emu, poolInfo.getNumIsotopes());
        }

        return initialValue;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_NATURALLABELINGINITIALIZER_H
