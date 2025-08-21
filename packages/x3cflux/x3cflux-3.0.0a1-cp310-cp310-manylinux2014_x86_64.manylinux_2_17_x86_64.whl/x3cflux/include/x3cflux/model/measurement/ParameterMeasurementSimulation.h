#ifndef X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H
#define X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H

#include <math/NumericTypes.h>
#include <model/data/Measurement.h>

#include <model/parameter/ParameterClassification.h>
#include <utility>

namespace x3cflux {

class ParameterMeasurementSimulation {
  private:
    std::string name_;
    Index offset_;
    std::vector<std::string> parameterNames_;
    std::vector<std::string> freeParameterNames_;
    flux::symb::ExprTree measurementFormula_;
    Index multiIndex_;

  public:
    ParameterMeasurementSimulation(std::string name, Index offset, const ParameterClassification &paramClass,
                                   const flux::symb::ExprTree &measurementFormula, Index multiIndex)
        : name_(std::move(name)), offset_(offset), measurementFormula_(measurementFormula), multiIndex_(multiIndex) {
        const auto &varNames = measurementFormula_.getVarNames();
        const auto &depParams = paramClass.getDependentParameters();
        const auto &constrParams = paramClass.getConstraintParameters();
        const auto &paramNames = paramClass.getParameterNames();
        for (auto index : paramClass.getFreeParameters()) {
            freeParameterNames_.push_back(paramNames[index]);
        }

        for (const auto &namePtr : varNames) {
            parameterNames_.emplace_back(namePtr);

            auto freeParamIt = std::find(freeParameterNames_.begin(), freeParameterNames_.end(), std::string(namePtr));
            auto constrParamIt =
                std::find_if(constrParams.begin(), constrParams.end(), [&](const std::pair<Index, Real> &constrParam) {
                    return paramNames[constrParam.first] == std::string(namePtr);
                });
            auto depParamIt = std::find_if(depParams.begin(), depParams.end(),
                                           [&](const std::pair<Index, std::vector<std::pair<Index, Real>>> &depParam) {
                                               return paramNames[depParam.first] == std::string(namePtr);
                                           });

            if (freeParamIt != freeParameterNames_.end()) {
                continue;
            } else if (constrParamIt != constrParams.end()) {
                std::shared_ptr<flux::symb::ExprTree> val(flux::symb::ExprTree::val(constrParamIt->second));
                measurementFormula_.subst(paramNames[constrParamIt->first].c_str(), val.get());
            } else if (depParamIt != depParams.end()) {
                const auto &dependencies = depParamIt->second;
                auto *freeParamForm = flux::symb::ExprTree::val(
                    dependencies.back().second); // todo: dirty trick to get constant term; replace
                for (std::size_t depIndex = 0; depIndex < dependencies.size() - 1; ++depIndex) {
                    auto *term = flux::symb::ExprTree::mul(
                        flux::symb::ExprTree::sym(freeParameterNames_[dependencies[depIndex].first].c_str()),
                        flux::symb::ExprTree::val(dependencies[depIndex].second));
                    freeParamForm = flux::symb::ExprTree::add(freeParamForm, term);
                }
                measurementFormula_.subst(paramNames[depParamIt->first].c_str(), freeParamForm);
            } else {
                X3CFLUX_THROW(std::logic_error, "Unknown metabolic parameter \"" + std::string(namePtr) +
                                                    "\" in measurement \"" + name + "\"");
            }
        }
        measurementFormula_.simplify();
    }

    const std::string &getName() const { return name_; }

    const std::vector<std::string> &getParameterNames() const { return parameterNames_; }

    const flux::symb::ExprTree &getMeasurementFormula() const { return measurementFormula_; }

    Index getMultiIndex() const { return multiIndex_; }

    Real evaluate(const RealVector &freeParameters) const {
        std::shared_ptr<flux::symb::ExprTree> eval(measurementFormula_.clone());

        for (Index i = 0; i < static_cast<Index>(freeParameterNames_.size()); ++i) {
            std::shared_ptr<flux::symb::ExprTree> paramVal(flux::symb::ExprTree::val(freeParameters(offset_ + i)));
            eval->subst(freeParameterNames_[i].c_str(), paramVal.get());
        }
        eval->eval();

        return eval->getDoubleValue();
    }

    Real evaluateDerivative(Index derivParamIndex, const RealVector &freeParameters) const {
        X3CFLUX_CHECK(derivParamIndex < freeParameters.size());

        // Derivation parameter is not of the same type as measurement parameters
        if (derivParamIndex - offset_ < 0 or
            derivParamIndex - offset_ >= static_cast<Index>(freeParameterNames_.size())) {
            return 0.;
        }

        std::shared_ptr<flux::symb::ExprTree> derivEval(
            measurementFormula_.deval(freeParameterNames_[derivParamIndex - offset_].c_str()));
        for (Index i = 0; i < static_cast<Index>(freeParameterNames_.size()); ++i) {
            std::shared_ptr<flux::symb::ExprTree> paramVal(flux::symb::ExprTree::val(freeParameters(offset_ + i)));
            derivEval->subst(freeParameterNames_[i].c_str(), paramVal.get());
        }
        derivEval->eval();

        return derivEval->getDoubleValue();
    }
};

template <typename Specification> class ParameterMeasurementSimulationImpl;

template <> class ParameterMeasurementSimulationImpl<FluxSpecification> : public ParameterMeasurementSimulation {
  public:
    ParameterMeasurementSimulationImpl(const FluxMeasurement &measurement, Index numFreePrevTypeFluxes,
                                       const ParameterClassification &paramClass, Index multiIndex)
        : ParameterMeasurementSimulation(measurement.getName(), numFreePrevTypeFluxes, paramClass,
                                         measurement.getMeasurementFormula(), multiIndex) {}
};

template <> class ParameterMeasurementSimulationImpl<PoolSizeSpecification> : public ParameterMeasurementSimulation {
  public:
    ParameterMeasurementSimulationImpl(const PoolSizeMeasurement &measurement, std::size_t numFreeParams,
                                       const ParameterClassification &paramClass, Index multiIndex)
        : ParameterMeasurementSimulation(measurement.getName(), static_cast<Index>(numFreeParams), paramClass,
                                         measurement.getMeasurementFormula(), multiIndex) {}
};

typedef ParameterMeasurementSimulationImpl<FluxSpecification> FluxMeasurementSimulation;

typedef ParameterMeasurementSimulationImpl<PoolSizeSpecification> PoolSizeMeasurementSimulation;

} // namespace x3cflux

#endif // X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H
