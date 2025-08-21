#ifndef X3CFLUX_MSMSMEASUREMENTSIMULATION_H
#define X3CFLUX_MSMSMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false>
class MSMSMeasurementSimulation : public LabelingMeasurementSimulation<Method, Multi> {
  public:
    typedef LabelingMeasurementSimulation<Method, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<Method, Multi> StateVarOps;
    typedef MeasurementConverter<Method> Converter;

  private:
    MSMSSpecification specification_;
    std::vector<std::tuple<std::size_t, Index, Index>> conversionMapping_;

  public:
    template <typename Network>
    MSMSMeasurementSimulation(const MSMSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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

        for (const auto &state :
             Converter::getMSMSStates(specification_.getFirstMask(), specification_.getSecondMask())) {
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

    std::size_t getSize() const override { return specification_.getFirstWeights().size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        typedef typename SystemTraits<Method, false>::FractionType SingleFraction;

        const auto &mask = specification_.getFirstMask();
        RealVector cumomers = RealVector::Zero(1 << mask.size());
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

        const auto &mask = specification_.getFirstMask();
        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << mask.size());
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

        const auto &mask = specification_.getFirstMask();
        RealVector cumomers = RealVector::Zero(1 << mask.size());
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

        const auto &mask = specification_.getFirstMask();
        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << mask.size());
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
        const auto &firstWeights = specification_.getFirstWeights();
        const auto &secondWeights = specification_.getSecondWeights();
        const auto &firstMask = specification_.getFirstMask();
        const auto &secondMask = specification_.getSecondMask();

        Index mdmRows = static_cast<Index>(firstMask.count()) + 1, mdmCols = static_cast<Index>(secondMask.count()) + 1;
        RealMatrix mdm = RealMatrix::Zero(mdmRows, mdmCols);
        for (Index i = 0; i < isotopomers.size(); ++i) {
            mdm((firstMask & boost::dynamic_bitset<>(firstMask.size(), i)).count(),
                (secondMask & boost::dynamic_bitset<>(secondMask.size(), i)).count()) += isotopomers(i);
        }

        RealVector measurement(firstWeights.size());
        for (Index i = 0; i < measurement.size(); ++i) {
            measurement(i) = mdm(firstWeights[i], secondWeights[i]);
        }

        return measurement;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_MSMSMEASUREMENTSIMULATION_H
