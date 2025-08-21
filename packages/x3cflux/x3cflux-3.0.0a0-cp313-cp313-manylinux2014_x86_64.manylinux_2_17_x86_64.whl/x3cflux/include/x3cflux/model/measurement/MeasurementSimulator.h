#ifndef X3CFLUX_MEASUREMENTSIMULATOR_H
#define X3CFLUX_MEASUREMENTSIMULATOR_H

#include <omp.h>

#include <model/data/FluxMLParser.h>
#include <model/measurement/CNMRMeasurementSimulation.h>
#include <model/measurement/GenericMeasurementSimulation.h>
#include <model/measurement/HNMRMeasurementSimulation.h>
#include <model/measurement/MIMSMeasurementSimulation.h>
#include <model/measurement/MSMSMeasurementSimulation.h>
#include <model/measurement/MSMeasurementSimulation.h>
#include <model/measurement/ParameterMeasurementSimulation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/LabelingNetwork.h>
#include <model/parameter/ParameterSpaceAdapter.h>
#include <model/parameter/ParameterSpaceFactory.h>
#include <model/system/CascadeSystemBuilder.h>

namespace x3cflux {

class SimulatorBase {
  public:
    virtual ~SimulatorBase() = default;
};

void append(std::vector<RealVector> &measurements, const std::vector<RealVector> &measurement);

RealVector flatten(const std::vector<RealVector> &measurements);

/// Finds the position of a parameter entry.
/// \param paramEntries names, types and values of the set parameters
/// \param name parameter name
/// \param type parameter type
/// \return iterator at the position
std::vector<ParameterEntry>::const_iterator findParameterEntry(const std::vector<ParameterEntry> &paramEntries,
                                                               const std::string &name, ParameterType type);

/// Gets binary representation of selected parameters.
/// \tparam ParamObject either Reaction or Metabolite class
/// \param paramEntries names, types and values of the set parameters
/// \param paramObjects Reaction or Metabolite object
/// \param type parameter type
/// \return parameter selection
template <typename ParamObject>
boost::dynamic_bitset<> getParameterSelection(const std::vector<ParameterEntry> &paramEntries,
                                              const std::vector<ParamObject> &paramObjects, ParameterType type) {
    std::size_t numParams = paramObjects.size();
    boost::dynamic_bitset<> paramSelection(numParams, false);

    std::size_t i = 0;
    for (const auto &object : paramObjects) {
        paramSelection[i++] = findParameterEntry(paramEntries, object.getName(), type) != paramEntries.end();
    }

    return paramSelection;
}

/// Gets parameter values from list of parameter entries, e.g. taken from measurement configuration. A warning
/// is issued, if a free parameter is not present.
/// \tparam Stationary IST or INST MFA
/// \tparam ParameterSpace parameter space class, per default chosen based on Stationary
/// \param parameterSpace parameter space instance
/// \param paramEntries names, types and values of the set parameters
/// \return free parameter vector
template <bool Stationary, typename ParameterSpace =
                               std::conditional_t<Stationary, StationaryParameterSpace, NonStationaryParameterSpace>>
RealVector getParameters(const ParameterSpace &parameterSpace, const std::vector<ParameterEntry> &paramEntries) {
    auto lastParameters = RealVector(parameterSpace.getNumFreeParameters());
    Index paramIndex = 0;
    const auto &netNames = parameterSpace.getNetFluxClassification().getParameterNames();
    for (auto netIndex : parameterSpace.getNetFluxClassification().getFreeParameters()) {
        const auto &name = netNames[netIndex];
        auto it = findParameterEntry(paramEntries, name, ParameterType::NET_FLUX);
        if (it != paramEntries.end()) {
            lastParameters(paramIndex++) = it->getValue();
        } else {
            X3CFLUX_WARNING() << "Net flux \"" << name << "\" not set in initial configuration (set to 0)";
            lastParameters(paramIndex++) = 0.;
        }
    }
    const auto &xchNames = parameterSpace.getExchangeFluxClassification().getParameterNames();
    for (auto xchIndex : parameterSpace.getExchangeFluxClassification().getFreeParameters()) {
        const auto &name = xchNames[xchIndex];
        auto it = findParameterEntry(paramEntries, name, ParameterType::EXCHANGE_FLUX);
        if (it != paramEntries.end()) {
            lastParameters(paramIndex++) = it->getValue();
        } else {
            X3CFLUX_WARNING() << "Exchange flux \"" << name << "\" not set in initial configuration (set to 0)";
            lastParameters(paramIndex++) = 0.;
        }
    }
    const auto &poolNames = parameterSpace.getPoolSizeClassification().getParameterNames();
    if (not Stationary) {
        for (auto poolIndex : parameterSpace.getPoolSizeClassification().getFreeParameters()) {
            const auto &name = poolNames[poolIndex];
            auto it = findParameterEntry(paramEntries, name, ParameterType::POOL_SIZE);
            if (it != paramEntries.end()) {
                lastParameters(paramIndex++) = it->getValue();
            } else {
                X3CFLUX_WARNING() << "Pool size \"" << name << "\" not set in initial configuration (set to 1)";
                lastParameters(paramIndex++) = 1.;
            }
        }
    }

    return lastParameters;
}

/// \brief Implementation of the labeling measurement simulator.
///
/// This is the core class of 13CFLUX3. All heavy computation is based on
/// this object. It combines all important pieces like the network of
/// labeling states, the parameter space and the builder of numerical
/// systems used for simulation.
///
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
/// \tparam Reduced reduced or full simulation of labeling states
template <typename Method, bool Stationary, bool Multi = false, bool Reduced = true>
class MeasurementSimulator : public SimulatorBase {
  public:
    typedef std::conditional_t<Stationary, StationaryParameterSpace, NonStationaryParameterSpace> ParameterSpace;
    typedef std::conditional_t<Reduced, ReducedLabelingNetwork<Method>, LabelingNetwork<Method>> Network;
    typedef CascadeSystemBuilder<Method, Stationary, Multi> Builder; // todo: enable other system types in the future
    typedef typename Builder::ProductSystem System;
    typedef typename System::Solution Solution;
    typedef ScalableMeasurementSimulation<Method, Multi> ScaleMeasSimulation;
    typedef ParameterMeasurementSimulation ParamMeasSimulation;

  private:
    NetworkData networkData_;
    std::vector<MeasurementConfiguration> configurations_;
    std::unique_ptr<ParameterSpace> parameterSpace_;
    std::unique_ptr<Network> network_;
    std::unique_ptr<Builder> builder_;
    std::vector<std::unique_ptr<ScaleMeasSimulation>> scaleMeasSimulations_;
    std::vector<std::unique_ptr<ParamMeasSimulation>> paramMeasSimulations_;
    std::size_t numMulti_;

  public:
    /// Create labeling simulator from network and measurement data.
    /// \param networkData data object containing metabolites and reactions
    /// \param configurations measurement configurations
    explicit MeasurementSimulator(const NetworkData &networkData,
                                  const std::vector<MeasurementConfiguration> &configurations)
        : networkData_(networkData), configurations_(configurations) {
        const auto &firstConfig = configurations.front();

        // Cache substrate names
        std::unordered_set<std::string> substrateNames;
        for (const auto &substrate : firstConfig.getSubstrates()) {
            substrateNames.insert(substrate->getMetaboliteName());
        }

        // Only consider inner metabolites for parameter space
        std::vector<Metabolite> innerMetabolites;
        for (const auto &metabolite : networkData.getMetabolites()) {
            if (substrateNames.find(metabolite.getName()) == substrateNames.end()) {
                innerMetabolites.push_back(metabolite);
            }
        }

        const auto &firstParamEntries = firstConfig.getParameterEntries();
        if (firstParamEntries.empty()) {
            parameterSpace_ = std::make_unique<ParameterSpace>(ParameterSpaceFactory::create(
                innerMetabolites, networkData.getReactions(), firstConfig.getNetFluxConstraints(),
                firstConfig.getExchangeFluxConstraints(), firstConfig.getPoolSizeConstraints()));
        } else {
            auto freeNetFluxSelection =
                getParameterSelection(firstParamEntries, networkData.getReactions(), ParameterType::NET_FLUX);
            auto freeExchangeFluxSelection =
                getParameterSelection(firstParamEntries, networkData.getReactions(), ParameterType::EXCHANGE_FLUX);
            auto freePoolSizeSelection =
                getParameterSelection(firstParamEntries, innerMetabolites, ParameterType::POOL_SIZE);
            parameterSpace_ = std::make_unique<ParameterSpace>(ParameterSpaceFactory::create(
                innerMetabolites, networkData.getReactions(), firstConfig.getNetFluxConstraints(),
                firstConfig.getExchangeFluxConstraints(), firstConfig.getPoolSizeConstraints(), freeNetFluxSelection,
                freeExchangeFluxSelection, freePoolSizeSelection));
        }

        // Instantiate the labeling network
        networkData_ = this->filterNetworkData(networkData, substrateNames);
        if constexpr (Reduced) {
            std::vector<std::shared_ptr<LabelingMeasurement>> labelingMeasurements;
            for (const auto &configuration : configurations) {
                for (const auto &measurement : configuration.getMeasurements()) {
                    if (isInstanceOf<LabelingMeasurement>(measurement)) {
                        labelingMeasurements.push_back(std::dynamic_pointer_cast<LabelingMeasurement>(measurement));
                    } else if (isInstanceOf<GenericMeasurement>(measurement)) {
                        auto genMeas = std::dynamic_pointer_cast<GenericMeasurement>(measurement);
                        for (const auto &subMeas : genMeas->getSubMeasurements()) {
                            for (const auto &labelMeas : subMeas.getMeasurements()) {
                                labelingMeasurements.push_back(labelMeas);
                            }
                        }
                    }
                }
            }
            network_ =
                std::make_unique<Network>(networkData_, configurations.front().getSubstrates(), labelingMeasurements);
        } else {
            network_ = std::make_unique<Network>(networkData_, configurations.front().getSubstrates());
        }

        // Instantiate the labeling system builder
        Real endTime = -1.;
        for (const auto &configuration : configurations) {
            for (const auto &meas : configuration.getMeasurements()) {
                if (isInstanceOf<LabelingMeasurement>(meas)) {
                    auto labelingMeas = std::dynamic_pointer_cast<LabelingMeasurement>(meas);
                    const auto &timeStamps = labelingMeas->getData().getTimeStamps();
                    if (endTime < timeStamps.back()) {
                        endTime = timeStamps.back();
                    }
                } else if (isInstanceOf<GenericMeasurement>(meas)) {
                    auto genMeas = std::dynamic_pointer_cast<GenericMeasurement>(meas);
                    const auto &timeStamps = genMeas->getData().getTimeStamps();
                    if (endTime < timeStamps.back()) {
                        endTime = timeStamps.back();
                    }
                }
            }
        }
        if constexpr (Multi) {
            std::vector<std::vector<std::shared_ptr<Substrate>>> multiSubstrates;
            for (const auto &configuration : configurations) {
                multiSubstrates.push_back(configuration.getSubstrates());
            }
            builder_ = std::make_unique<Builder>(*network_, multiSubstrates, endTime);
        } else {
            builder_ = std::make_unique<Builder>(*network_, configurations.front().getSubstrates(), endTime);
        }

        // Parse measurement data and simulations
        std::size_t multiIndex = 0;
        for (const auto &configuration : configurations) {
            for (const auto &measurement : configuration.getMeasurements()) {
                if (isInstanceOf<MSMeasurement>(measurement)) {
                    auto msMeasurement = std::dynamic_pointer_cast<MSMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new MSMeasurementSimulation<Method, Multi>(*msMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<MIMSMeasurement>(measurement)) {
                    auto mimsMeasurement = std::dynamic_pointer_cast<MIMSMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new MIMSMeasurementSimulation<Method, Multi>(*mimsMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<MSMSMeasurement>(measurement)) {
                    auto msmsMeasurement = std::dynamic_pointer_cast<MSMSMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new MSMSMeasurementSimulation<Method, Multi>(*msmsMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<HNMRMeasurement>(measurement)) {
                    auto hnmrMeasurement = std::dynamic_pointer_cast<HNMRMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new HNMRMeasurementSimulation<Method, Multi>(*hnmrMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<CNMRMeasurement>(measurement)) {
                    auto cnmrMeasurement = std::dynamic_pointer_cast<CNMRMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new CNMRMeasurementSimulation<Method, Multi>(*cnmrMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<GenericMeasurement>(measurement)) {
                    auto genMeasurement = std::dynamic_pointer_cast<GenericMeasurement>(measurement);
                    scaleMeasSimulations_.emplace_back(
                        new GenericMeasurementSimulation<Method, Multi>(*genMeasurement, *network_, multiIndex));
                } else if (isInstanceOf<FluxMeasurement>(measurement)) {
                    auto fluxMeasurement = std::dynamic_pointer_cast<FluxMeasurement>(measurement);
                    if (fluxMeasurement->getSpecification().isNet()) {
                        paramMeasSimulations_.emplace_back(new FluxMeasurementSimulation(
                            *fluxMeasurement, 0, parameterSpace_->getNetFluxClassification(), multiIndex));
                    } else {
                        paramMeasSimulations_.emplace_back(new FluxMeasurementSimulation(
                            *fluxMeasurement, parameterSpace_->getNetFluxClassification().getNumFreeParameters(),
                            parameterSpace_->getExchangeFluxClassification(), multiIndex));
                    }
                } else if (isInstanceOf<PoolSizeMeasurement>(measurement)) {
                    auto poolSizeMeasurement = std::dynamic_pointer_cast<PoolSizeMeasurement>(measurement);
                    paramMeasSimulations_.emplace_back(new PoolSizeMeasurementSimulation(
                        *poolSizeMeasurement,
                        parameterSpace_->getNetFluxClassification().getNumFreeParameters() +
                            parameterSpace_->getExchangeFluxClassification().getNumFreeParameters(),
                        parameterSpace_->getPoolSizeClassification(), multiIndex));
                } else {
                    throw std::invalid_argument("Unknown measurement type "
                                                "found in configuration \"" +
                                                configuration.getName() +
                                                "\". 13CFLUX cannot "
                                                "handle custom "
                                                "implementations of "
                                                "measurements. Only use "
                                                "measurement types defined "
                                                "the \'x3cflux\' "
                                                "namespace.");
                }
            }
            ++multiIndex;
        }
        numMulti_ = multiIndex;

        // Report structurally non-identifiable parameters
        if constexpr (Reduced and not Stationary) {
            auto reducedStates = network_->getStateVariables();
            for (Index metaboliteIdx = 0; metaboliteIdx < static_cast<Index>(networkData_.getMetabolites().size());
                 ++metaboliteIdx) {
                if (network_->getPoolInformation(metaboliteIdx).isSubstrate()) {
                    continue;
                }

                std::string name = networkData_.getMetabolites()[metaboliteIdx].getName();
                auto paramNames = parameterSpace_->getFreeParameterNames();
                auto freeIt = std::find(paramNames.begin(), paramNames.end(), name);
                if (freeIt == paramNames.end()) {
                    continue;
                }

                auto statesIt = reducedStates.find(metaboliteIdx);
                auto measIt = std::find_if(paramMeasSimulations_.begin(), paramMeasSimulations_.end(),
                                           [&name](const auto &paramMeasSim) {
                                               return std::find(paramMeasSim->getParameterNames().begin(),
                                                                paramMeasSim->getParameterNames().end(),
                                                                name) != paramMeasSim->getParameterNames().end();
                                           });
                if (statesIt == reducedStates.end() and measIt == paramMeasSimulations_.end()) {
                    X3CFLUX_WARNING() << "Pool size of metabolite \"" << name
                                      << "\" is non-determinable given the "
                                         "measurement configuration, as it "
                                         "does not impact the simulation "
                                         "outcome. Consider fixing the pool "
                                         "size in FluxML to reduce the "
                                         "ill-conditionedness of the "
                                         "inverse problem.";
                }
            }
        }
    }

    ~MeasurementSimulator() override = default;

    /// \return the simulator's metabolites and reactions
    const NetworkData &getNetworkData() const { return networkData_; }

    /// \return the simulator's measurement configurations
    const std::vector<MeasurementConfiguration> &getConfigurations() const { return configurations_; }

    /// \return description of parameters and constraints
    const ParameterSpace &getParameterSpace() const { return *parameterSpace_; }

    /// \return description of parameters and constraints
    ParameterSpace &getParameterSpace() { return *parameterSpace_; }

    /// \return network of labeling states to simulate
    const Network &getLabelingNetwork() const { return *network_; }

    /// \return network of labeling states to simulate
    Network &getLabelingNetwork() { return *network_; }

    /// \return builder for the underlying numerical systems
    const Builder &getSystemBuilder() const { return *builder_; }

    /// \return builder for the underlying numerical systems
    Builder &getSystemBuilder() { return *builder_; }

    /// \return measurements with scaling factor (labeling and generic
    /// measurements)
    const std::vector<std::unique_ptr<ScaleMeasSimulation>> &getScalableMeasurementSimulations() const {
        return scaleMeasSimulations_;
    }

    /// \return measurements of simulation parameters
    const std::vector<std::unique_ptr<ParamMeasSimulation>> &getParameterMeasurementSimulations() const {
        return paramMeasSimulations_;
    }

    /// \return number of multiple labeling experiments
    std::size_t getNumMulti() const { return numMulti_; }

    /// Simulates measurements for a given set of free parameters.
    /// \param freeParameters parameter vector
    /// \param timeStamps optional grid of time stamps (no effect on
    /// stationary simulations) \return simulated measurements (first
    /// labeling measurements, then parameter measurements)
    std::pair<std::vector<RealVector>, std::vector<Real>>
    computeMeasurements(const RealVector &freeParameters, const std::vector<Real> &timeStamps = {}) const {
        Index numParams = freeParameters.size();
        if (numParams != parameterSpace_->getNumFreeParameters()) {
            throw std::invalid_argument("Free model parameter vector has invalid size (" + std::to_string(numParams) +
                                        "). The model expects " +
                                        std::to_string(parameterSpace_->getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace_->contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        auto parameters = parameterSpace_->computeParameters(freeParameters);

        std::unique_ptr<typename Builder::System> system;
        if (not timeStamps.empty() and
            *std::max_element(timeStamps.begin(), timeStamps.end()) > builder_->getEndTime()) {
            X3CFLUX_INFO()
                << "Requested range of time stamps exceeds last measurement time point. Simulations might take longer.";
            Real endTime = *std::max_element(timeStamps.begin(), timeStamps.end());
            std::unique_ptr<Builder> builder;
            if constexpr (Multi) {
                std::vector<std::vector<std::shared_ptr<Substrate>>> multiSubstrates;
                for (const auto &configuration : this->configurations_) {
                    multiSubstrates.push_back(configuration.getSubstrates());
                }
                builder = std::make_unique<Builder>(*network_, multiSubstrates, endTime);
            } else {
                builder = std::make_unique<Builder>(*network_, this->configurations_.front().getSubstrates(), endTime);
            };
            system = builder->build(parameters);
        } else {
            system = builder_->build(parameters);
        }
        auto solution = system->solve();

        std::pair<std::vector<RealVector>, std::vector<Real>> measurements;
        if constexpr (Stationary) {
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
                measurements.first.push_back(scaleMeasSimulations_[measIndex]->evaluate(solution));
            }
        } else {
            if (timeStamps.empty()) {
                for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
                    append(measurements.first, scaleMeasSimulations_[measIndex]->evaluate(solution));
                }
            } else {
                for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
                    auto oldTimeStamps = scaleMeasSimulations_[measIndex]->getTimeStamps();
                    scaleMeasSimulations_[measIndex]->setTimeStamps(timeStamps);
                    auto measurement = scaleMeasSimulations_[measIndex]->evaluate(solution);
                    append(measurements.first, measurement);
                    scaleMeasSimulations_[measIndex]->setTimeStamps(oldTimeStamps);
                }
            }
        }
        for (const auto &measSim : paramMeasSimulations_) {
            measurements.second.push_back(measSim->evaluate(freeParameters));
        }

        return measurements;
    }

    /// \return names of the measurements (first labeling measurements, then parameter measurements)
    std::pair<std::vector<std::string>, std::vector<std::string>> getMeasurementNames() const {
        std::pair<std::vector<std::string>, std::vector<std::string>> names;
        for (const auto &measSim : scaleMeasSimulations_) {
            names.first.emplace_back(measSim->getName());
        }
        for (const auto &measSim : paramMeasSimulations_) {
            names.second.emplace_back(measSim->getName());
        }
        return names;
    }

    std::pair<std::vector<Index>, std::vector<Index>> getMeasurementMultiIndices() const {
        std::pair<std::vector<Index>, std::vector<Index>> indices;
        for (const auto &measSim : scaleMeasSimulations_) {
            indices.first.emplace_back(measSim->getMultiIndex());
        }
        for (const auto &measSim : paramMeasSimulations_) {
            indices.second.emplace_back(measSim->getMultiIndex());
        }
        return indices;
    }

    /// \return time stamps of labeling measurements
    std::vector<std::vector<Real>> getMeasurementTimeStamps() const {
        std::vector<std::vector<Real>> timeStamps;
        for (const auto &measSim : scaleMeasSimulations_) {
            timeStamps.emplace_back(measSim->getTimeStamps());
        }
        return timeStamps;
    }

    /// Compute the Jacobian of the measurements simulation for a given set of free parameters.
    /// \param freeParameters parameter vector
    /// \return simulation Jacobian
    RealMatrix computeJacobian(const RealVector &freeParameters) const {
        Index numParams = freeParameters.size();
        if (numParams != parameterSpace_->getNumFreeParameters()) {
            throw std::invalid_argument("Free model parameter vector has invalid size (" + std::to_string(numParams) +
                                        "). The model expects " +
                                        std::to_string(parameterSpace_->getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace_->contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        Index numParamMeasurements = paramMeasSimulations_.size();
        Index numScaleMeasurements = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
            numScaleMeasurements +=
                scaleMeasSimulations_[measIndex]->getNumTimeStamps() * scaleMeasSimulations_[measIndex]->getSize();
        }

        RealMatrix jacobian(numScaleMeasurements + numParamMeasurements, freeParameters.size());

        auto parameters = parameterSpace_->computeParameters(freeParameters);
        auto system = builder_->build(parameters);
        auto solution = system->solve();

        // clang-format off
#pragma omp parallel for schedule(auto) default(none) shared(jacobian, numParams, numScaleMeasurements, freeParameters, parameters, solution)
        // clang-format on
        for (Index paramIndex = 0; paramIndex < numParams; ++paramIndex) {
            auto parameterDerivative = parameterSpace_->computeParameterDerivatives(paramIndex);
            auto derivSystem = builder_->buildDerivative(parameters, parameterDerivative, solution);
            auto derivSolution = derivSystem->solve();

            Index offset = 0;
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
                RealVector measDeriv;
                if constexpr (Stationary) {
                    measDeriv = scaleMeasSimulations_[measIndex]->evaluateDerivative(derivSolution);
                } else {
                    measDeriv = flatten(scaleMeasSimulations_[measIndex]->evaluateDerivative(derivSolution));
                }
                jacobian.col(paramIndex).segment(offset, measDeriv.size()) = measDeriv;
                offset += measDeriv.size();
            }

            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations_.size(); ++measIndex) {
                jacobian(numScaleMeasurements + static_cast<Index>(measIndex), paramIndex) =
                    paramMeasSimulations_[measIndex]->evaluateDerivative(paramIndex, freeParameters);
            }
        }

        return jacobian;
    }

    /// Compute the Jacobian of each of the multiple measurements simulation
    /// for a given set of free parameters. \param freeParameters parameter
    /// vector \return all simulation Jacobians
    std::vector<RealMatrix> computeMultiJacobians(const RealVector &freeParameters) const {
        Index numParams = freeParameters.size();
        if (numParams != parameterSpace_->getNumFreeParameters()) {
            throw std::invalid_argument("Free model parameter vector has invalid size (" + std::to_string(numParams) +
                                        "). The model expects " +
                                        std::to_string(parameterSpace_->getNumFreeParameters()) + " free parameters.");
        }

        if (not parameterSpace_->contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        std::vector<Index> numScaleMeasurements(numMulti_), numParamMeasurements(numMulti_);
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
            numScaleMeasurements[scaleMeasSimulations_[measIndex]->getMultiIndex()] +=
                scaleMeasSimulations_[measIndex]->getNumTimeStamps() * scaleMeasSimulations_[measIndex]->getSize();
        }
        for (const auto &paramMeasSimulation : paramMeasSimulations_) {
            numParamMeasurements[paramMeasSimulation->getMultiIndex()] += 1;
        }

        std::vector<RealMatrix> jacobians;
        for (std::size_t multiIndex = 0; multiIndex < numMulti_; ++multiIndex) {
            jacobians.emplace_back(numScaleMeasurements[multiIndex] + numParamMeasurements[multiIndex], numParams);
        }

        auto parameters = parameterSpace_->computeParameters(freeParameters);
        auto system = builder_->build(parameters);
        auto solution = system->solve();

        // clang-format off
#pragma omp parallel for schedule(auto) default(none)                      \
        shared(jacobians, numParams, numScaleMeasurements, freeParameters,     \
                   parameters, solution)
        // clang-format on
        for (Index paramIndex = 0; paramIndex < numParams; ++paramIndex) {
            auto parameterDerivative = parameterSpace_->computeParameterDerivatives(paramIndex);
            auto derivSystem = builder_->buildDerivative(parameters, parameterDerivative, solution);
            auto derivSolution = derivSystem->solve();

            std::vector<Index> offsets(numMulti_, 0);
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations_.size(); ++measIndex) {
                Index multiIndex = scaleMeasSimulations_[measIndex]->getMultiIndex();
                auto &jacobian = jacobians[multiIndex];

                RealVector measDeriv;
                if constexpr (Stationary) {
                    measDeriv = scaleMeasSimulations_[measIndex]->evaluateDerivative(derivSolution);
                } else {
                    measDeriv = flatten(scaleMeasSimulations_[measIndex]->evaluateDerivative(derivSolution));
                }
                jacobian.col(paramIndex).segment(offsets[multiIndex], measDeriv.size()) = measDeriv;
                offsets[multiIndex] += measDeriv.size();
            }

            std::vector<Index> paramMeasJacIndices(numMulti_, 0);
            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations_.size(); ++measIndex) {
                Index multiIndex = paramMeasSimulations_[measIndex]->getMultiIndex();
                auto &jacobian = jacobians[multiIndex];

                jacobian(numScaleMeasurements[multiIndex] + paramMeasJacIndices[multiIndex]++, paramIndex) =
                    paramMeasSimulations_[measIndex]->evaluateDerivative(paramIndex, freeParameters);
            }
        }

        return jacobians;
    }

  private:
    NetworkData filterNetworkData(const NetworkData &networkData,
                                  const std::unordered_set<std::string> &substrateNames) const {
        const auto &netClass = parameterSpace_->getNetFluxClassification();
        const auto &poolClass = parameterSpace_->getPoolSizeClassification();

        if (netClass.getNumParameters() == networkData.getReactions().size() and
            poolClass.getNumParameters() == networkData.getMetabolites().size()) {
            return networkData;
        }

        std::vector<Reaction> reducedReactions;
        for (const auto &reaction : networkData.getReactions()) {
            if (std::find(netClass.getParameterNames().begin(), netClass.getParameterNames().end(),
                          reaction.getName()) != netClass.getParameterNames().end()) {
                reducedReactions.push_back(reaction);
            }
        }

        std::vector<Metabolite> reducedMetabolites;
        for (const auto &metabolite : networkData.getMetabolites()) {
            if (std::find(poolClass.getParameterNames().begin(), poolClass.getParameterNames().end(),
                          metabolite.getName()) != poolClass.getParameterNames().end() or
                substrateNames.find(metabolite.getName()) != substrateNames.end()) {
                reducedMetabolites.push_back(metabolite);
            }
        }

        return {reducedMetabolites, reducedReactions};
    }
};

} // namespace x3cflux

#endif // X3CFLUX_MEASUREMENTSIMULATOR_H
