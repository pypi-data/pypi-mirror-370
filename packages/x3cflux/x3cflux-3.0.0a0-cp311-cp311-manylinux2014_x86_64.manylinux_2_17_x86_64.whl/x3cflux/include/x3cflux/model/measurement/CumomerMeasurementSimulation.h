#ifndef X3CFLUX_CUMOMERMEASUREMENTSIMULATION_H
#define X3CFLUX_CUMOMERMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false>
class CumomerMeasurementSimulation : public LabelingMeasurementSimulation<Method, Multi> {
  public:
    typedef LabelingMeasurementSimulation<Method, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<Method, Multi> StateVarOps;
    typedef MeasurementConverter<Method> Converter;

  private:
    CumomerSpecification specification_;
    std::size_t numAtoms_;
    std::vector<std::tuple<std::size_t, Index, Index>> conversionMapping_;

  public:
    template <typename Network>
    CumomerMeasurementSimulation(const CumomerMeasurement &measurement, const Network &network,
                                 std::size_t multiIndex = 0)
        : Base(measurement.getName(), measurement.isAutoScalable(), measurement.getData().getTimeStamps(), multiIndex,
               measurement.getMetaboliteName()),
          specification_(measurement.getSpecification()) {
        // Find pool index
        std::size_t poolIndex = -1;
        for (std::size_t i = 0; i < network.getNumPools(); ++i) {
            if (network.getPoolInformation(i).getName() == measurement.getMetaboliteName()) {
                poolIndex = i;
                break;
            }
        }
        X3CFLUX_CHECK(poolIndex != std::size_t(-1));

        numAtoms_ = network.getPoolInformation(poolIndex).getNumAtoms();
        for (const auto &state :
             Converter::getCumomerStates(specification_.getLabeledMask(), specification_.getWildcardMask())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            std::size_t systemIndex = ordering.getSystemIndex({poolIndex, state});

            conversionMapping_.emplace_back(levelIndex, systemIndex, static_cast<Index>(state.to_ulong()));
        }
    }

    std::size_t getSize() const override { return 1; }

    RealVector evaluate(const StationarySolution &solution) const override {
        typedef typename SystemTraits<Method, false>::FractionType SingleFraction;

        RealVector cumomers = RealVector::Zero(1 << numAtoms_);
        cumomers(0) = 1.;

        for (const auto &convMap : conversionMapping_) {
            auto parStateVar = StateVarOps::get(solution[std::get<0>(convMap)], std::get<1>(convMap));
            auto stateVar = StateVarOps::get(parStateVar, this->getMultiIndex(), std::get<0>(convMap));
            if constexpr (std::is_same_v<SingleFraction, Real>) {
                cumomers(std::get<2>(convMap)) = stateVar;
            } else {
                cumomers(std::get<2>(convMap)) = stateVar[std::get<0>(convMap) + 1];
            }
        }

        return evaluateIsotopomers(IsotopomerTransformation<CumomerMethod>::apply(cumomers));
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        typedef typename SystemTraits<Method, false>::FractionType SingleFraction;

        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << numAtoms_);
            cumomers(0) = 1.;

            for (const auto &convMap : conversionMapping_) {
                auto parStateVar = solution[std::get<0>(convMap)](timeStamp, std::get<1>(convMap));
                auto stateVar = StateVarOps::get(parStateVar, this->getMultiIndex(), std::get<0>(convMap));
                if constexpr (std::is_same_v<SingleFraction, Real>) {
                    cumomers(std::get<2>(convMap)) = stateVar;
                } else {
                    cumomers(std::get<2>(convMap)) = stateVar[std::get<0>(convMap) + 1];
                }
            }

            measurements.push_back(evaluateIsotopomers(IsotopomerTransformation<CumomerMethod>::apply(cumomers)));
        }

        return measurements;
    }

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override {
        typedef typename SystemTraits<Method, false>::FractionType SingleFraction;

        RealVector cumomers = RealVector::Zero(1 << numAtoms_);
        cumomers(0) = 0.;

        for (const auto &convMap : conversionMapping_) {
            auto parStateVar = StateVarOps::get(derivSolution[std::get<0>(convMap)], std::get<1>(convMap));
            auto stateVar = StateVarOps::get(parStateVar, this->getMultiIndex(), std::get<0>(convMap));
            if constexpr (std::is_same_v<SingleFraction, Real>) {
                cumomers(std::get<2>(convMap)) = stateVar;
            } else {
                cumomers(std::get<2>(convMap)) = stateVar[std::get<0>(convMap) + 1];
            }
        }

        return evaluateIsotopomers(IsotopomerTransformation<CumomerMethod>::apply(cumomers));
    }

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override {
        typedef typename SystemTraits<Method, false>::FractionType SingleFraction;

        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << numAtoms_);
            cumomers(0) = 0.;

            for (const auto &convMap : conversionMapping_) {
                auto parStateVar = derivSolution[std::get<0>(convMap)](timeStamp, std::get<1>(convMap));
                auto stateVar = StateVarOps::get(parStateVar, this->getMultiIndex(), std::get<0>(convMap));
                if constexpr (std::is_same_v<SingleFraction, Real>) {
                    cumomers(std::get<2>(convMap)) = stateVar;
                } else {
                    cumomers(std::get<2>(convMap)) = stateVar[std::get<0>(convMap) + 1];
                }
            }

            measurements.push_back(evaluateIsotopomers(IsotopomerTransformation<CumomerMethod>::apply(cumomers)));
        }

        return measurements;
    }

  private:
    RealVector evaluateIsotopomers(const RealVector &isotopomers) const {
        const auto &labeledMask = specification_.getLabeledMask();
        auto mask = ~(labeledMask | specification_.getWildcardMask());

        RealVector measurement = RealVector::Zero(1);
        for (Index i = 0; i < isotopomers.size(); ++i) {
            boost::dynamic_bitset<> labeling(mask.size(), i);

            if ((~labeling & mask) == mask and (labeling & labeledMask) == labeledMask) {
                measurement(0) += isotopomers(i);
            }
        }
        return measurement;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_CUMOMERMEASUREMENTSIMULATION_H
