#ifndef X3CFLUX_CNMRMEASUREMENTSIMULATION_H
#define X3CFLUX_CNMRMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class CNMRMeasurementSimulation;

template <bool Multi>
class CNMRMeasurementSimulation<EMUMethod, Multi> : public LabelingMeasurementSimulation<EMUMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<EMUMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<EMUMethod, Multi> StateVarOps;
    typedef MeasurementConverter<EMUMethod> Converter;

  private:
    CNMRSpecification specification_;
    std::size_t numAtoms_;
    std::vector<std::size_t> levelIndices_;
    std::vector<Index> systemIndices_;

  public:
    template <typename Network>
    CNMRMeasurementSimulation(const CNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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
        for (auto state :
             Converter::getCNMRStates(numAtoms_, specification_.getAtomPositions(), specification_.getTypes())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            Index systemIndex = ordering.getSystemIndex({poolIndex, state});

            levelIndices_.push_back(levelIndex);
            systemIndices_.push_back(systemIndex);
        }
    }

    std::size_t getSize() const override { return specification_.getAtomPositions().size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        const auto &positions = specification_.getAtomPositions();
        const auto &types = specification_.getTypes();
        // Returns cumomer fraction with same state pattern (last entry of EMU fraction)
        auto getFraction = [&](Index statePos) {
            auto multiEmu = StateVarOps::get(solution[levelIndices_[statePos]], systemIndices_[statePos]);
            return multiEmu((levelIndices_[statePos] + 1) * this->getMultiIndex() + +(levelIndices_[statePos] + 1));
        };

        RealVector measurement(positions.size());
        Index statePos = 0;
        for (Index posIndex = 0; posIndex < static_cast<Index>(positions.size()); ++posIndex) {
            std::size_t position = positions[posIndex] - 1;

            switch (types[posIndex]) {
            case CNMRSpecification::CNMRType::SINGLET: {
                // ..010.. = ..x1x..
                // - ..11x.. -
                // ..x11.. + ..111..
                measurement(posIndex) = getFraction(statePos++);

                if (position > 0) {
                    measurement(posIndex) -= getFraction(statePos++);
                }

                if (numAtoms_ > position + 1) {
                    measurement(posIndex) -= getFraction(statePos++);

                    if (position > 0) {
                        measurement(posIndex) += getFraction(statePos++);
                    }
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                // ..110.. = ..11x..
                // - 111
                std::vector<std::pair<std::size_t, Index>> locations;
                measurement(posIndex) = getFraction(statePos++);

                if (numAtoms_ > position + 1) {
                    measurement(posIndex) -= getFraction(statePos++);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                // ..011.. = ..x11..
                // - 111
                measurement(posIndex) = getFraction(statePos++);

                if (position > 0) {
                    measurement(posIndex) -= getFraction(statePos++);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
            case CNMRSpecification::CNMRType::TRIPLETS: {
                measurement(posIndex) = getFraction(statePos++);
            } break;
            }
        }

        return measurement;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        const auto &positions = specification_.getAtomPositions();
        const auto &types = specification_.getTypes();
        // Returns cumomer fraction with same state pattern (last entry of EMU fraction)
        auto getFraction = [&](Index statePos, Real time) {
            auto multiEmu = solution[levelIndices_[statePos]](time, systemIndices_[statePos]);
            return multiEmu((levelIndices_[statePos] + 1) * this->getMultiIndex() + (levelIndices_[statePos] + 1));
        };

        std::vector<RealVector> measurements;
        for (Real timeStamp : this->getTimeStamps()) {
            RealVector measurement(positions.size());
            Index statePos = 0;
            for (Index posIndex = 0; posIndex < static_cast<Index>(positions.size()); ++posIndex) {
                std::size_t position = positions[posIndex] - 1;

                switch (types[posIndex]) {
                case CNMRSpecification::CNMRType::SINGLET: {
                    // ..010.. = ..x1x.. - ..11x.. - ..x11.. + ..111..
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (position > 0) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }

                    if (numAtoms_ > position + 1) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);

                        if (position > 0) {
                            measurement(posIndex) += getFraction(statePos++, timeStamp);
                        }
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                    // ..110.. = ..11x.. - 111
                    std::vector<std::pair<std::size_t, Index>> locations;
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (numAtoms_ > position + 1) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                    // ..011.. = ..x11.. - 111
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (position > 0) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
                case CNMRSpecification::CNMRType::TRIPLETS: {
                    measurement(posIndex) = getFraction(statePos++, timeStamp);
                } break;
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

template <bool Multi>
class CNMRMeasurementSimulation<CumomerMethod, Multi> : public LabelingMeasurementSimulation<CumomerMethod, Multi> {
  public:
    typedef LabelingMeasurementSimulation<CumomerMethod, Multi> Base;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    typedef StateVariableOperations<CumomerMethod, Multi> StateVarOps;
    typedef MeasurementConverter<CumomerMethod> Converter;

  private:
    CNMRSpecification specification_;
    std::size_t numAtoms_;
    std::vector<std::size_t> levelIndices_;
    std::vector<Index> systemIndices_;

  public:
    template <typename Network>
    CNMRMeasurementSimulation(const CNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0)
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
        for (auto state :
             Converter::getCNMRStates(numAtoms_, specification_.getAtomPositions(), specification_.getTypes())) {
            // Level index of Cumomer fraction are equal to number of
            // surely labeled atoms
            std::size_t numAtoms = state.count();
            std::size_t levelIndex = numAtoms - 1;

            // Get system index of Cumomer fraction from network
            // ordering
            typename Network::Ordering ordering(network, levelIndex + 1);
            Index systemIndex = ordering.getSystemIndex({poolIndex, state});

            levelIndices_.push_back(levelIndex);
            systemIndices_.push_back(systemIndex);
        }
    }

    std::size_t getSize() const override { return specification_.getAtomPositions().size(); }

    RealVector evaluate(const StationarySolution &solution) const override {
        const auto &positions = specification_.getAtomPositions();
        const auto &types = specification_.getTypes();
        auto getFraction = [&](Index statePos) {
            auto parStateVar = StateVarOps::get(solution[levelIndices_[statePos]], systemIndices_[statePos]);
            return StateVarOps::get(parStateVar, this->getMultiIndex(), levelIndices_[statePos]);
        };

        RealVector measurement(positions.size());
        Index statePos = 0;
        for (Index posIndex = 0; posIndex < static_cast<Index>(positions.size()); ++posIndex) {
            std::size_t position = positions[posIndex] - 1;

            switch (types[posIndex]) {
            case CNMRSpecification::CNMRType::SINGLET: {
                // ..010.. = ..x1x..
                // - ..11x.. -
                // ..x11.. + ..111..
                measurement(posIndex) = getFraction(statePos++);

                if (position > 0) {
                    measurement(posIndex) -= getFraction(statePos++);
                }

                if (numAtoms_ > position + 1) {
                    measurement(posIndex) -= getFraction(statePos++);

                    if (position > 0) {
                        measurement(posIndex) += getFraction(statePos++);
                    }
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                // ..110.. = ..11x..
                // - 111
                std::vector<std::pair<std::size_t, Index>> locations;
                measurement(posIndex) = getFraction(statePos++);

                if (numAtoms_ > position + 1) {
                    measurement(posIndex) -= getFraction(statePos++);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                // ..011.. = ..x11..
                // - 111
                measurement(posIndex) = getFraction(statePos++);

                if (position > 0) {
                    measurement(posIndex) -= getFraction(statePos++);
                }
            } break;
            case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
            case CNMRSpecification::CNMRType::TRIPLETS: {
                measurement(posIndex) = getFraction(statePos++);
            } break;
            }
        }

        return measurement;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override {
        const auto &positions = specification_.getAtomPositions();
        const auto &types = specification_.getTypes();
        auto getFraction = [&](Index statePos, Real time) {
            auto parStateVar = solution[levelIndices_[statePos]](time, systemIndices_[statePos]);
            return StateVarOps::get(parStateVar, this->getMultiIndex(), levelIndices_[statePos]);
        };

        std::vector<RealVector> measurements;
        for (Real timeStamp : this->getTimeStamps()) {
            RealVector measurement(positions.size());
            Index statePos = 0;
            for (Index posIndex = 0; posIndex < static_cast<Index>(positions.size()); ++posIndex) {
                std::size_t position = positions[posIndex] - 1;

                switch (types[posIndex]) {
                case CNMRSpecification::CNMRType::SINGLET: {
                    // ..010.. = ..x1x.. - ..11x.. - ..x11.. + ..111..
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (position > 0) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }

                    if (numAtoms_ > position + 1) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);

                        if (position > 0) {
                            measurement(posIndex) += getFraction(statePos++, timeStamp);
                        }
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_LEFT: {
                    // ..110.. = ..11x.. - 111
                    std::vector<std::pair<std::size_t, Index>> locations;
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (numAtoms_ > position + 1) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_RIGHT: {
                    // ..011.. = ..x11.. - 111
                    measurement(posIndex) = getFraction(statePos++, timeStamp);

                    if (position > 0) {
                        measurement(posIndex) -= getFraction(statePos++, timeStamp);
                    }
                } break;
                case CNMRSpecification::CNMRType::DOUBLET_OF_DOUBLETS:
                case CNMRSpecification::CNMRType::TRIPLETS: {
                    measurement(posIndex) = getFraction(statePos++, timeStamp);
                } break;
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

#endif // X3CFLUX_CNMRMEASUREMENTSIMULATION_H
