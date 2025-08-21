#ifndef X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H
#define X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H

#include "MeasurementSimulator.h"

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi = false, bool Reduced = true>
class WeightedLeastSquaresLossFunction : public MeasurementSimulator<Method, Stationary, Multi, Reduced> {
  private:
    std::vector<RealVector> scaleMeasData_;
    std::vector<RealVector> scaleStdDeviations_;
    std::vector<Real> paramMeasData_;
    std::vector<Real> paramStdDeviations_;

  public:
    WeightedLeastSquaresLossFunction(const NetworkData &networkData,
                                     const std::vector<MeasurementConfiguration> &configurations)
        : MeasurementSimulator<Method, Stationary, Multi, Reduced>(networkData, configurations) {

        for (const auto &configuration : configurations) {
            for (const auto &measurement : configuration.getMeasurements()) {
                if (isInstanceOf<MSMeasurement>(measurement)) {
                    auto msMeasurement = std::dynamic_pointer_cast<MSMeasurement>(measurement);
                    append(scaleMeasData_, msMeasurement->getData().getValues());
                    append(scaleStdDeviations_, msMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<MIMSMeasurement>(measurement)) {
                    auto mimsMeasurement = std::dynamic_pointer_cast<MIMSMeasurement>(measurement);
                    append(scaleMeasData_, mimsMeasurement->getData().getValues());
                    append(scaleStdDeviations_, mimsMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<MSMSMeasurement>(measurement)) {
                    auto msmsMeasurement = std::dynamic_pointer_cast<MSMSMeasurement>(measurement);
                    append(scaleMeasData_, msmsMeasurement->getData().getValues());
                    append(scaleStdDeviations_, msmsMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<HNMRMeasurement>(measurement)) {
                    auto hnmrMeasurement = std::dynamic_pointer_cast<HNMRMeasurement>(measurement);
                    append(scaleMeasData_, hnmrMeasurement->getData().getValues());
                    append(scaleStdDeviations_, hnmrMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<CNMRMeasurement>(measurement)) {
                    auto cnmrMeasurement = std::dynamic_pointer_cast<CNMRMeasurement>(measurement);
                    append(scaleMeasData_, cnmrMeasurement->getData().getValues());
                    append(scaleStdDeviations_, cnmrMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<GenericMeasurement>(measurement)) {
                    auto genMeasurement = std::dynamic_pointer_cast<GenericMeasurement>(measurement);
                    append(scaleMeasData_, genMeasurement->getData().getValues());
                    append(scaleStdDeviations_, genMeasurement->getData().getStandardDeviations());
                } else if (isInstanceOf<FluxMeasurement>(measurement)) {
                    auto fluxMeasurement = std::dynamic_pointer_cast<FluxMeasurement>(measurement);
                    paramMeasData_.push_back(fluxMeasurement->getValue());
                    paramStdDeviations_.push_back(fluxMeasurement->getStandardDeviation());
                } else if (isInstanceOf<PoolSizeMeasurement>(measurement)) {
                    auto poolSizeMeasurement = std::dynamic_pointer_cast<PoolSizeMeasurement>(measurement);
                    paramMeasData_.push_back(poolSizeMeasurement->getValue());
                    paramStdDeviations_.push_back(poolSizeMeasurement->getStandardDeviation());
                } else {
                    X3CFLUX_THROW(std::invalid_argument, "Unknown measurement type passed");
                }
            }
        }
    }

    const std::vector<RealVector> &getScalableMeasurementData() const { return scaleMeasData_; }

    const std::vector<RealVector> &getScalableMeasurementStandardDeviations() const { return scaleStdDeviations_; }

    const std::vector<Real> &getParameterMeasurementData() const { return paramMeasData_; }

    const std::vector<Real> &getParameterMeasurementStandardDeviations() const { return paramStdDeviations_; }

    std::pair<std::vector<RealVector>, std::vector<Real>> getMeasurementData() const {
        return std::make_pair(getScalableMeasurementData(), getParameterMeasurementData());
    }

    std::pair<std::vector<RealVector>, std::vector<Real>> getMeasurementStandardDeviations() const {
        return std::make_pair(getScalableMeasurementStandardDeviations(), getParameterMeasurementStandardDeviations());
    }

    std::pair<std::vector<RealVector>, std::vector<Real>> computeScaledMeasurements(const RealVector &parameters) {
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();

        auto measurements = this->computeMeasurements(parameters);
        auto &scaleMeasSims = measurements.first;

        std::size_t measValueOffset = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            if (scaleMeasSimulations[measIndex]->isAutoScalable() and scaleMeasSims[measValueOffset].size() > 1) {
                for (std::size_t timeIndex = 0; timeIndex < scaleMeasSimulations[measIndex]->getNumTimeStamps();
                     ++timeIndex) {
                    scaleMeasSims[measValueOffset + timeIndex] *= computeScaleFactor(
                        scaleMeasSims[measValueOffset + timeIndex], scaleMeasData_[measValueOffset + timeIndex],
                        scaleStdDeviations_[measValueOffset + timeIndex]);
                }
            }
            measValueOffset += scaleMeasSimulations[measIndex]->getNumTimeStamps();
        }

        return measurements;
    }

    Real computeLoss(const RealVector &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.size();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace.contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        Real lossValue = 0.;

        auto parameters = parameterSpace.computeParameters(freeParameters);
        auto system = builder.build(parameters);
        auto solution = system->solve();

        std::size_t valIndex = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            lossValue += computeNormalizedResidual(scaleMeasSimulations[measIndex]->evaluate(solution), valIndex,
                                                   scaleMeasSimulations[measIndex]->isAutoScalable());
            valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
        }

        for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
            Real diff = (paramMeasData_[measIndex] - paramMeasSimulations[measIndex]->evaluate(freeParameters)) /
                        paramStdDeviations_[measIndex];
            lossValue += diff * diff;
        }

        return lossValue;
    }

    RealVector computeLoss(const RealMatrix &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.rows();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        Index numSimulations = freeParameters.cols();
        for (Index colIndex = 0; colIndex < numSimulations; ++colIndex) {
            if (not parameterSpace.contains(freeParameters.col(colIndex))) {
                throw std::domain_error("Free model parameters in column " + std::to_string(colIndex) +
                                        " violate inequality constraints. Relax lower/upper "
                                        "bounds. If violations are very small, consider "
                                        "raising "
                                        "\'parameter_space.constraint_violation_tolerance\'.");
            }
        }

        RealVector lossValues(freeParameters.cols());

        // clang-format off
#pragma omp parallel for schedule(auto) default(none) shared(lossValues, numSimulations, freeParameters, \
                                                                     parameterSpace, builder, scaleMeasSimulations, paramMeasSimulations)
        // clang-format on
        for (Index colIndex = 0; colIndex < numSimulations; ++colIndex) {
            Real lossValue = 0.;

            auto parameters = parameterSpace.computeParameters(freeParameters.col(colIndex));
            auto system = builder.build(parameters);
            auto solution = system->solve();

            std::size_t valIndex = 0;
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
                lossValue += computeNormalizedResidual(scaleMeasSimulations[measIndex]->evaluate(solution), valIndex,
                                                       scaleMeasSimulations[measIndex]->isAutoScalable());
                valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
            }

            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
                Real diff = (paramMeasData_[measIndex] -
                             paramMeasSimulations[measIndex]->evaluate(freeParameters.col(colIndex))) /
                            paramStdDeviations_[measIndex];
                lossValue += diff * diff;
            }

            lossValues(colIndex) = lossValue;
        }

        return lossValues;
    }

    std::vector<Real> computeMultiLosses(const RealVector &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.size();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace.contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        std::vector<Real> lossValues(this->getNumMulti(), 0.);

        auto parameters = parameterSpace.computeParameters(freeParameters);
        auto system = builder.build(parameters);
        auto solution = system->solve();

        std::size_t valIndex = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            lossValues[scaleMeasSimulations[measIndex]->getMultiIndex()] +=
                computeNormalizedResidual(scaleMeasSimulations[measIndex]->evaluate(solution), valIndex,
                                          scaleMeasSimulations[measIndex]->isAutoScalable());
            valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
        }

        for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
            Real diff = (paramMeasData_[measIndex] - paramMeasSimulations[measIndex]->evaluate(freeParameters)) /
                        paramStdDeviations_[measIndex];
            lossValues[paramMeasSimulations[measIndex]->getMultiIndex()] += diff * diff;
        }

        return lossValues;
    }

    RealVector computeLossGradient(const RealVector &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.size();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace.contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        RealVector gradient(freeParameters.size());

        auto parameters = parameterSpace.computeParameters(freeParameters);
        auto system = builder.build(parameters);
        auto solution = system->solve();

        // clang-format off
#pragma omp parallel for schedule(auto) default(none) shared(gradient, numParams, freeParameters, parameters, solution, \
                                                                     parameterSpace, builder, scaleMeasSimulations, paramMeasSimulations)
        // clang-format on
        for (Index paramIndex = 0; paramIndex < numParams; ++paramIndex) {
            Real gradValue = 0.;

            auto parameterDerivative = parameterSpace.computeParameterDerivatives(paramIndex);
            auto derivSystem = builder.buildDerivative(parameters, parameterDerivative, solution);
            auto derivSolution = derivSystem->solve();

            std::size_t valIndex = 0;
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
                gradValue += computeNormalizedResidualDerivative(
                    scaleMeasSimulations[measIndex]->evaluate(solution),
                    scaleMeasSimulations[measIndex]->evaluateDerivative(derivSolution), valIndex,
                    scaleMeasSimulations[measIndex]->isAutoScalable());
                valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
            }

            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
                gradValue -= 2 *
                             (paramMeasData_[measIndex] - paramMeasSimulations[measIndex]->evaluate(freeParameters)) *
                             paramMeasSimulations[measIndex]->evaluateDerivative(paramIndex, freeParameters) /
                             (paramStdDeviations_[measIndex] * paramStdDeviations_[measIndex]);
            }

            gradient(paramIndex) = gradValue;
        }

        return gradient;
    }

    RealMatrix computeLossGradient(const RealMatrix &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.rows();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        Index numSimulations = freeParameters.cols();
        for (Index colIndex = 0; colIndex < numSimulations; ++colIndex) {
            if (not parameterSpace.contains(freeParameters.col(colIndex))) {
                throw std::domain_error("Free model parameters in column " + std::to_string(colIndex) +
                                        " violate inequality constraints. Relax lower/upper "
                                        "bounds. If violations are very small, consider "
                                        "raising "
                                        "\'parameter_space.constraint_violation_tolerance\'.");
            }
        }

        RealMatrix gradients(numParams, numSimulations);

        // clang-format off
#pragma omp parallel for schedule(auto) default(none) shared(gradients, numSimulations, numParams, freeParameters, \
                                                                     parameterSpace, builder, scaleMeasSimulations, paramMeasSimulations)
        // clang-format on
        for (Index colIndex = 0; colIndex < numSimulations; ++colIndex) {
            auto parameters = parameterSpace.computeParameters(freeParameters.col(colIndex));
            auto system = builder.build(parameters);
            auto solution = system->solve();

            for (Index paramIndex = 0; paramIndex < numParams; ++paramIndex) {
                Real gradValue = 0.;

                auto parameterDerivatives = parameterSpace.computeParameterDerivatives(paramIndex);
                auto derivSystem = builder.buildDerivative(parameters, parameterDerivatives, solution);
                auto derivSolution = derivSystem->solve();

                std::size_t valIndex = 0;
                for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
                    gradValue += computeNormalizedResidualDerivative(
                        scaleMeasSimulations[measIndex]->evaluate(solution),
                        scaleMeasSimulations[measIndex]->evaluateDerivative(derivSolution), valIndex,
                        scaleMeasSimulations[measIndex]->isAutoScalable());
                    valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
                }

                for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
                    gradValue -=
                        2 *
                        (paramMeasData_[measIndex] -
                         paramMeasSimulations[measIndex]->evaluate(freeParameters.col(colIndex))) *
                        paramMeasSimulations[measIndex]->evaluateDerivative(paramIndex, freeParameters.col(colIndex)) /
                        (paramStdDeviations_[measIndex] * paramStdDeviations_[measIndex]);
                }

                gradients(paramIndex, colIndex) = gradValue;
            }
        }

        return gradients;
    }

    std::vector<RealVector> computeMultiLossGradients(const RealVector &freeParameters) const {
        const auto &parameterSpace = this->getParameterSpace();
        const auto &builder = this->getSystemBuilder();
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();

        Index numParams = freeParameters.size();
        if (numParams != this->getParameterSpace().getNumFreeParameters()) {
            throw std::invalid_argument(
                "Free model parameter vector has invalid size (" + std::to_string(numParams) + "). The model expects " +
                std::to_string(this->getParameterSpace().getNumFreeParameters()) + " free parameters.");
        }
        if (not parameterSpace.contains(freeParameters)) {
            throw std::domain_error("Free model parameters violate inequality constraints. "
                                    "Relax lower/upper bounds. If violations are very small, "
                                    "consider raising "
                                    "\'parameter_space.constraint_violation_tolerance\'.");
        }

        std::vector<RealVector> gradients(this->getNumMulti(), RealVector::Zero(numParams).eval());

        auto parameters = parameterSpace.computeParameters(freeParameters);
        auto system = builder.build(parameters);
        auto solution = system->solve();

        // clang-format off
#pragma omp parallel for schedule(auto) default(none)                          \
    shared(gradients, numParams, freeParameters, parameters, solution,         \
               parameterSpace, builder, scaleMeasSimulations,                  \
               paramMeasSimulations)
        // clang-format on
        for (Index paramIndex = 0; paramIndex < numParams; ++paramIndex) {
            auto parameterDerivative = parameterSpace.computeParameterDerivatives(paramIndex);
            auto derivSystem = builder.buildDerivative(parameters, parameterDerivative, solution);
            auto derivSolution = derivSystem->solve();

            std::size_t valIndex = 0;
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
                gradients[scaleMeasSimulations[measIndex]->getMultiIndex()](paramIndex) +=
                    computeNormalizedResidualDerivative(
                        scaleMeasSimulations[measIndex]->evaluate(solution),
                        scaleMeasSimulations[measIndex]->evaluateDerivative(derivSolution), valIndex,
                        scaleMeasSimulations[measIndex]->isAutoScalable());
                valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
            }

            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
                gradients[paramMeasSimulations[measIndex]->getMultiIndex()](paramIndex) -=
                    2 * (paramMeasData_[measIndex] - paramMeasSimulations[measIndex]->evaluate(freeParameters)) *
                    paramMeasSimulations[measIndex]->evaluateDerivative(paramIndex, freeParameters) /
                    (paramStdDeviations_[measIndex] * paramStdDeviations_[measIndex]);
            }
        }

        return gradients;
    }

    RealMatrix computeLinearizedHessian(const RealVector &freeParameters) const {
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();
        const auto &scaleStdDeviations = this->getScalableMeasurementStandardDeviations();
        const auto &paramStdDeviations = this->getParameterMeasurementStandardDeviations();

        Index numParamMeasurements = paramMeasSimulations.size();
        Index numScaleMeasurements = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            numScaleMeasurements +=
                scaleMeasSimulations[measIndex]->getNumTimeStamps() * scaleMeasSimulations[measIndex]->getSize();
        }

        auto jacobian = this->computeJacobian(freeParameters);

        RealVector measVariances(numScaleMeasurements + numParamMeasurements);
        Index offset = 0, valIndex = 0;
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            Index measurementSize = scaleMeasSimulations[measIndex]->getSize();

            for (std::size_t subMeasIndex = 0; subMeasIndex < scaleMeasSimulations[measIndex]->getNumTimeStamps();
                 ++subMeasIndex) {
                measVariances.segment(offset, measurementSize) =
                    scaleStdDeviations[valIndex + subMeasIndex].array().inverse().square();
                offset += measurementSize;
            }

            valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
        }

        for (Index measIndex = 0; measIndex < static_cast<Index>(paramMeasSimulations.size()); ++measIndex) {
            measVariances(measIndex + numScaleMeasurements) =
                1. / (paramStdDeviations[measIndex] * paramStdDeviations[measIndex]);
        }

        return (jacobian.transpose() * measVariances.asDiagonal() * jacobian).eval();
    }

    std::vector<RealMatrix> computeMultiLinearizedHessians(const RealVector &freeParameters) const {
        const auto &scaleMeasSimulations = this->getScalableMeasurementSimulations();
        const auto &paramMeasSimulations = this->getParameterMeasurementSimulations();
        const auto &scaleStdDeviations = this->getScalableMeasurementStandardDeviations();
        const auto &paramStdDeviations = this->getParameterMeasurementStandardDeviations();
        std::size_t numMulti = this->getNumMulti();
        Index numParams = freeParameters.size();

        auto jacobians = this->computeMultiJacobians(freeParameters);

        std::vector<Index> numScaleMeasurements(numMulti), numParamMeasurements(numMulti);
        for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
            numScaleMeasurements[scaleMeasSimulations[measIndex]->getMultiIndex()] +=
                scaleMeasSimulations[measIndex]->getNumTimeStamps() * scaleMeasSimulations[measIndex]->getSize();
        }
        for (const auto &paramMeasSimulation : paramMeasSimulations) {
            numParamMeasurements[paramMeasSimulation->getMultiIndex()] += 1;
        }

        std::vector<RealMatrix> hessians;
        for (std::size_t multiIndex = 0; multiIndex < numMulti; ++multiIndex) {
            hessians.emplace_back(numParams, numParams);
        }

        // clang-format off
#pragma omp parallel for schedule(auto) default(none)                          \
    shared(hessians, jacobians, numMulti, numScaleMeasurements,                \
               scaleMeasSimulations, scaleStdDeviations, numParamMeasurements, \
               paramMeasSimulations, paramStdDeviations)
        // clang-format on
        for (Index multiIndex = 0; multiIndex < static_cast<Index>(numMulti); ++multiIndex) {
            RealVector measVariances(numScaleMeasurements[multiIndex] + numParamMeasurements[multiIndex]);
            Index offset = 0, valIndex = 0;
            for (std::size_t measIndex = 0; measIndex < scaleMeasSimulations.size(); ++measIndex) {
                if (scaleMeasSimulations[measIndex]->getMultiIndex() == multiIndex) {
                    Index measurementSize = scaleMeasSimulations[measIndex]->getSize();

                    for (std::size_t subMeasIndex = 0;
                         subMeasIndex < scaleMeasSimulations[measIndex]->getNumTimeStamps(); ++subMeasIndex) {
                        measVariances.segment(offset, measurementSize) =
                            scaleStdDeviations[valIndex + subMeasIndex].array().inverse().square();
                        offset += measurementSize;
                    }
                }

                valIndex += scaleMeasSimulations[measIndex]->getNumTimeStamps();
            }
            for (std::size_t measIndex = 0; measIndex < paramMeasSimulations.size(); ++measIndex) {
                if (paramMeasSimulations[measIndex]->getMultiIndex() == multiIndex) {
                    measVariances(numScaleMeasurements[multiIndex]) =
                        1. / (paramStdDeviations[measIndex] * paramStdDeviations[measIndex]);
                }
            }

            hessians[multiIndex] =
                (jacobians[multiIndex].transpose() * measVariances.asDiagonal() * jacobians[multiIndex]).eval();
        }

        return hessians;
    }

  private:
    Real computeNormalizedResidual(const RealVector &simMeasValue, std::size_t measIndex, bool isAutoScalable) const {
        const auto &measValue = scaleMeasData_[measIndex];
        const auto &stdDev = scaleStdDeviations_[measIndex];

        if (isAutoScalable and simMeasValue.size() > 1) {
            Real scale = computeScaleFactor(simMeasValue, measValue, stdDev);
            return ((measValue - scale * simMeasValue).array() / stdDev.array()).matrix().squaredNorm();
        } else {
            return ((measValue - simMeasValue).array() / stdDev.array()).matrix().squaredNorm();
        }
    }

    Real computeNormalizedResidual(const std::vector<RealVector> &simMeasValues, std::size_t beginMeasIndex,
                                   bool isAutoScalable) const {
        Real residValue = 0.;

        if (isAutoScalable and simMeasValues.front().size() > 1) {
            for (std::size_t measIndex = 0; measIndex < simMeasValues.size(); ++measIndex) {
                const auto &measValue = scaleMeasData_[beginMeasIndex + measIndex];
                const auto &stdDev = scaleStdDeviations_[beginMeasIndex + measIndex];
                const auto &simMeasValue = simMeasValues[measIndex];
                Real scale = computeScaleFactor(simMeasValue, measValue, stdDev);
                residValue += ((measValue - scale * simMeasValue).array() / stdDev.array()).matrix().squaredNorm();
            }
        } else {
            for (std::size_t measIndex = 0; measIndex < simMeasValues.size(); ++measIndex) {
                const auto &measValue = scaleMeasData_[beginMeasIndex + measIndex];
                const auto &stdDev = scaleStdDeviations_[beginMeasIndex + measIndex];
                const auto &simMeasValue = simMeasValues[measIndex];
                residValue += ((measValue - simMeasValue).array() / stdDev.array()).matrix().squaredNorm();
            }
        }

        return residValue;
    }

    Real computeNormalizedResidualDerivative(const RealVector &simMeasValue, const RealVector &simMeasValueDerivative,
                                             std::size_t measIndex, bool isAutoScalable) const {
        const auto &measValue = scaleMeasData_[measIndex];
        const auto &stdDev = scaleStdDeviations_[measIndex];

        if (isAutoScalable and simMeasValue.size() > 1) {
            Real scale = computeScaleFactor(simMeasValue, measValue, stdDev),
                 scaleDeriv = computeScaleFactorDerivative(simMeasValue, simMeasValueDerivative, measValue, stdDev);

            auto scaledSimMeasValueDeriv = scaleDeriv * simMeasValue + scale * simMeasValueDerivative;
            return -2 * ((measValue - scale * simMeasValue).array() * scaledSimMeasValueDeriv.array() /
                         stdDev.array().square())
                            .sum();
        } else {
            return -2 * ((measValue - simMeasValue).array() * simMeasValueDerivative.array() / stdDev.array().square())
                            .sum();
        }
    }

    Real computeNormalizedResidualDerivative(const std::vector<RealVector> &simMeasValues,
                                             const std::vector<RealVector> &simMeasValueDerivatives,
                                             std::size_t beginMeasIndex, bool isAutoScalable) const {
        Real residValue = 0.;

        if (isAutoScalable and simMeasValues.front().size() > 1) {
            for (std::size_t measIndex = 0; measIndex < simMeasValues.size(); ++measIndex) {
                const auto &measValue = scaleMeasData_[beginMeasIndex + measIndex];
                const auto &stdDev = scaleStdDeviations_[beginMeasIndex + measIndex];
                const auto &simMeasValue = simMeasValues[measIndex];
                const auto &simMeasValueDeriv = simMeasValueDerivatives[measIndex];
                Real scale = computeScaleFactor(simMeasValue, measValue, stdDev),
                     scaleDeriv = computeScaleFactorDerivative(simMeasValue, simMeasValueDeriv, measValue, stdDev);

                auto scaledSimMeasValueDeriv = scaleDeriv * simMeasValue + scale * simMeasValueDeriv;
                residValue -= ((measValue - scale * simMeasValue).array() * scaledSimMeasValueDeriv.array() /
                               stdDev.array().square())
                                  .sum();
            }
        } else {
            for (std::size_t measIndex = 0; measIndex < simMeasValues.size(); ++measIndex) {
                const auto &measValue = scaleMeasData_[beginMeasIndex + measIndex];
                const auto &stdDev = scaleStdDeviations_[beginMeasIndex + measIndex];
                const auto &simMeasValue = simMeasValues[measIndex];
                const auto &simMeasValueDeriv = simMeasValueDerivatives[measIndex];
                residValue -=
                    ((measValue - simMeasValue).array() * simMeasValueDeriv.array() / stdDev.array().square()).sum();
            }
        }

        return 2 * residValue;
    }

    static Real computeScaleFactor(const RealVector &simMeasurements, const RealVector &realMeasurements,
                                   const RealVector &standardDeviations) {
        return ((simMeasurements.array() * realMeasurements.array()) / standardDeviations.array().square()).sum() /
               (simMeasurements.array() / standardDeviations.array()).square().sum();
    }

    static Real computeScaleFactorDerivative(const RealVector &simMeasurements,
                                             const RealVector &simMeasurementDerivatives,
                                             const RealVector &realMeasurements, const RealVector &standardDeviations) {
        auto sum1 =
            (realMeasurements.array() * simMeasurementDerivatives.array() / standardDeviations.array().square()).sum();
        auto sum2 = (simMeasurements.array() * realMeasurements.array() / standardDeviations.array().square()).sum();
        auto sum3 =
            (simMeasurements.array() * simMeasurementDerivatives.array() / standardDeviations.array().square()).sum();
        auto sum4 = (simMeasurements.array() * simMeasurements.array() / standardDeviations.array().square()).sum();

        return (sum1 - 2. * sum2 * sum3 / sum4) / sum4;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H
