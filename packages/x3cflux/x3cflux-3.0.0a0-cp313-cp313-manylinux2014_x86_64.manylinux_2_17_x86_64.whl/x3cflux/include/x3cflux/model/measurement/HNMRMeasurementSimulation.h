#ifndef X3CFLUX_HNMRMEASUREMENTSIMULATION_H
#define X3CFLUX_HNMRMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class HNMRMeasurementSimulation;

template <bool Multi>
class HNMRMeasurementSimulation<EMUMethod, Multi> : public LabelingMeasurementSimulation<EMUMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<EMUMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<EMUMethod, Multi> StateVarOps;
    typedef MeasurementConverter<EMUMethod> Converter;

  private:
    HNMRSpecification specification_;
    Index numAtoms_;
    std::vector<Index> systemIndices_;

  public:
    template <typename Network>
    HNMRMeasurementSimulation(const HNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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
        for (const auto &state : Converter::getHNMRStates(numAtoms_, specification_.getAtomPositions())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            Index systemIndex = ordering.getSystemIndex({poolIndex, state});

            systemIndices_.push_back(systemIndex);
        }
    }

    std::size_t getSize() const override { return systemIndices_.size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        RealVector measurement(systemIndices_.size());
        for (Index i = 0; i < measurement.size(); ++i) {
            auto multiEmu = StateVarOps::get(solution[0], systemIndices_[i]);
            measurement(i) = multiEmu(2 * this->getMultiIndex() + 1);
        }

        return measurement;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        std::vector<RealVector> measurements;
        for (Real timeStamp : this->getTimeStamps()) {
            RealVector measurement(systemIndices_.size());
            for (Index i = 0; i < measurement.size(); ++i) {
                auto multiEmu = solution[0](timeStamp, systemIndices_[i]);
                measurement(i) = multiEmu(2 * this->getMultiIndex() + 1);
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
class HNMRMeasurementSimulation<CumomerMethod, Multi> : public LabelingMeasurementSimulation<CumomerMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<CumomerMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<CumomerMethod, Multi> StateVarOps;
    typedef MeasurementConverter<CumomerMethod> Converter;

  private:
    HNMRSpecification specification_;
    Index numAtoms_;
    std::vector<Index> systemIndices_;

  public:
    template <typename Network>
    HNMRMeasurementSimulation(const HNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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
        for (const auto &state : Converter::getHNMRStates(numAtoms_, specification_.getAtomPositions())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            Index systemIndex = ordering.getSystemIndex({poolIndex, state});

            systemIndices_.push_back(systemIndex);
        }
    }

    std::size_t getSize() const override { return systemIndices_.size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        RealVector measurement(systemIndices_.size());
        for (Index i = 0; i < measurement.size(); ++i) {
            auto multiCumomer = StateVarOps::get(solution[0], systemIndices_[i]);
            if constexpr (Multi) {
                measurement(i) = multiCumomer[this->getMultiIndex()];
            } else {
                measurement(i) = multiCumomer;
            }
        }

        return measurement;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        std::vector<RealVector> measurements;
        for (Real timeStamp : this->getTimeStamps()) {
            RealVector measurement(systemIndices_.size());
            for (Index i = 0; i < measurement.size(); ++i) {
                auto multiCumomer = solution[0](timeStamp, systemIndices_[i]);
                if constexpr (Multi) {
                    measurement(i) = multiCumomer[this->getMultiIndex()];
                } else {
                    measurement(i) = multiCumomer;
                }
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

} // namespace x3cflux

#endif // X3CFLUX_HNMRMEASUREMENTSIMULATION_H
