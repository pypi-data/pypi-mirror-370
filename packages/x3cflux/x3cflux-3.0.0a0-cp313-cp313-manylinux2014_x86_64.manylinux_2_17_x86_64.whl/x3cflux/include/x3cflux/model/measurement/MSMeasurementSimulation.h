#ifndef X3CFLUX_MSMEASUREMENTSIMULATION_H
#define X3CFLUX_MSMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class MSMeasurementSimulation;

template <bool Multi>
class MSMeasurementSimulation<EMUMethod, Multi> : public LabelingMeasurementSimulation<EMUMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<EMUMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<EMUMethod, Multi> StateVarOps;

  private:
    MSSpecification specification_;
    std::size_t levelIndex_;
    Index systemIndex_;

  public:
    template <typename Network>
    MSMeasurementSimulation(const MSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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

        // Level index of an EMU fraction is equal to number of considered atoms - 1
        const auto &posMask = specification_.getMask();
        std::size_t numAtoms = posMask.count();
        levelIndex_ = numAtoms - 1;

        // Get system index of EMU fraction from network ordering
        typename Network::Ordering ordering(network, levelIndex_ + 1);
        systemIndex_ = ordering.getSystemIndex({poolIndex, posMask});
    }

    std::size_t getSize() const override { return specification_.getWeights().size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        const auto &weights = specification_.getWeights();
        const auto &mask = specification_.getMask();
        RealVector measurement(weights.size());
        Index emuSize = mask.count() + 1;

        auto multiEmu = StateVarOps::get(solution[levelIndex_], systemIndex_);
        auto emu = multiEmu.segment(this->getMultiIndex() * emuSize, emuSize);
        for (Index i = 0; i < measurement.size(); ++i) {
            measurement(i) = emu(weights[i]);
        }

        return measurement;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        const auto &weights = specification_.getWeights();
        const auto &mask = specification_.getMask();
        std::vector<RealVector> measurements;
        Index emuSize = mask.count() + 1;

        for (Real timeStamp : this->getTimeStamps()) {
            auto multiEmu = solution[levelIndex_](timeStamp, systemIndex_);
            auto emu = multiEmu.segment(this->getMultiIndex() * emuSize, emuSize);

            RealVector measurement(weights.size());
            for (Index i = 0; i < measurement.size(); ++i) {
                measurement(i) = emu(weights[i]);
            }

            measurements.push_back(measurement);
        }

        return measurements;
    }

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override {
        return evaluate(derivSolution);
    }

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override {
        return evaluate(derivSolution);
    }
};

template <bool Multi>
class MSMeasurementSimulation<CumomerMethod, Multi> : public LabelingMeasurementSimulation<CumomerMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<CumomerMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<CumomerMethod, Multi> StateVarOps;
    typedef MeasurementConverter<CumomerMethod> Converter;
    typedef IsotopomerTransformation<CumomerMethod> IsotopomerTrafo;

  private:
    MSSpecification specification_;
    std::vector<std::tuple<std::size_t, Index, Index>> conversionMapping_;

  public:
    template <typename Network>
    MSMeasurementSimulation(const MSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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

        for (const auto &state : Converter::getMSStates(specification_.getMask())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            Index systemIndex = ordering.getSystemIndex({poolIndex, state});

            conversionMapping_.emplace_back(levelIndex, systemIndex, static_cast<Index>(state.to_ulong()));
        }
    }

    std::size_t getSize() const override { return specification_.getWeights().size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        const auto &mask = specification_.getMask();
        RealVector cumomers = RealVector::Zero(1 << mask.size());
        cumomers(0) = 1.;

        for (const auto &convMap : conversionMapping_) {
            auto multiCumomer = StateVarOps::get(solution[std::get<0>(convMap)], std::get<1>(convMap));
            if constexpr (Multi) {
                cumomers(std::get<2>(convMap)) = multiCumomer[this->getMultiIndex()];
            } else {
                cumomers(std::get<2>(convMap)) = multiCumomer;
            }
        }

        return evaluateIsotopomers(IsotopomerTrafo::apply(cumomers));
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        const auto &mask = specification_.getMask();
        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << mask.size());
            cumomers(0) = 1.;

            for (const auto &convMap : conversionMapping_) {
                auto multiCumomer = solution[std::get<0>(convMap)](timeStamp, std::get<1>(convMap));
                if constexpr (Multi) {
                    cumomers(std::get<2>(convMap)) = multiCumomer[this->getMultiIndex()];
                } else {
                    cumomers(std::get<2>(convMap)) = multiCumomer;
                }
            }

            measurements.push_back(evaluateIsotopomers(IsotopomerTrafo::apply(cumomers)));
        }

        return measurements;
    }

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override {
        const auto &mask = specification_.getMask();
        RealVector cumomers = RealVector::Zero(1 << mask.size());
        cumomers(0) = 0.;

        for (const auto &convMap : conversionMapping_) {
            auto multiCumomer = StateVarOps::get(derivSolution[std::get<0>(convMap)], std::get<1>(convMap));
            if constexpr (Multi) {
                cumomers(std::get<2>(convMap)) = multiCumomer[this->getMultiIndex()];
            } else {
                cumomers(std::get<2>(convMap)) = multiCumomer;
            }
        }

        return evaluateIsotopomers(IsotopomerTrafo::apply(cumomers));
    }

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override {
        const auto &mask = specification_.getMask();
        std::vector<RealVector> measurements;

        for (Real timeStamp : this->getTimeStamps()) {
            RealVector cumomers = RealVector::Zero(1 << mask.size());
            cumomers(0) = 0.;

            for (const auto &convMap : conversionMapping_) {
                auto multiCumomer = derivSolution[std::get<0>(convMap)](timeStamp, std::get<1>(convMap));
                if constexpr (Multi) {
                    cumomers(std::get<2>(convMap)) = multiCumomer[this->getMultiIndex()];
                } else {
                    cumomers(std::get<2>(convMap)) = multiCumomer;
                }
            }

            measurements.push_back(evaluateIsotopomers(IsotopomerTrafo::apply(cumomers)));
        }

        return measurements;
    }

  private:
    RealVector evaluateIsotopomers(const RealVector &isotopomers) const {
        const auto &weights = specification_.getWeights();
        const auto &mask = specification_.getMask();

        Index mdvSize = static_cast<Index>(mask.count()) + 1;
        RealVector mdv = RealVector::Zero(mdvSize);
        for (Index i = 0; i < isotopomers.size(); ++i) {
            mdv((mask & boost::dynamic_bitset<>(mask.size(), i)).count()) += isotopomers(i);
        }

        RealVector measurement(weights.size());
        for (Index i = 0; i < measurement.size(); ++i) {
            measurement(i) = mdv(weights[i]);
        }

        return measurement;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_MSMEASUREMENTSIMULATION_H
