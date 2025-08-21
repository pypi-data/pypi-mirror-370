#ifndef X3CFLUX_GENERICMEASUREMENTSIMULATION_H
#define X3CFLUX_GENERICMEASUREMENTSIMULATION_H

#include <model/data/Measurement.h>
#include <model/measurement/CNMRMeasurementSimulation.h>
#include <model/measurement/CumomerMeasurementSimulation.h>
#include <model/measurement/HNMRMeasurementSimulation.h>
#include <model/measurement/MSMSMeasurementSimulation.h>
#include <model/measurement/MSMeasurementSimulation.h>
#include <model/measurement/ScalableMeasurementSimulation.h>

namespace x3cflux {

template <typename Method, bool Multi = false>
class GenericMeasurementSimulation : public ScalableMeasurementSimulation<Method, Multi> {
  public:
    typedef typename ScalableMeasurementSimulation<Method, Multi>::StationarySolution StationarySolution;
    typedef typename ScalableMeasurementSimulation<Method, Multi>::InstationarySolution InstationarySolution;
    typedef LabelingMeasurementSimulation<Method, Multi> LabelMeasSim;

  private:
    std::vector<flux::symb::ExprTree> formulas_;
    std::vector<std::vector<std::string>> variableNames_;
    std::vector<std::vector<std::shared_ptr<LabelMeasSim>>> measurements_;

  public:
    template <typename Network>
    GenericMeasurementSimulation(const GenericMeasurement &measurement, const Network &network, Index multiIndex = 0)
        : ScalableMeasurementSimulation<Method, Multi>(measurement.getName(), measurement.isAutoScalable(),
                                                       measurement.getData().getTimeStamps(), multiIndex) {
        for (const auto &subMeasurement : measurement.getSubMeasurements()) {
            formulas_.push_back(subMeasurement.getFormula());
            variableNames_.push_back(subMeasurement.getVariableNames());

            const auto &measurements = subMeasurement.getMeasurements();
            std::vector<std::shared_ptr<LabelMeasSim>> subMeasurements;
            for (const auto &meas : measurements) {
                if (isInstanceOf<MSMeasurement>(meas)) {
                    auto msMeasurement = std::dynamic_pointer_cast<MSMeasurement>(meas);
                    subMeasurements.emplace_back(
                        new MSMeasurementSimulation<Method, Multi>(*msMeasurement, network, multiIndex));
                } else if (isInstanceOf<MSMSMeasurement>(meas)) {
                    auto msmsMeasurement = std::dynamic_pointer_cast<MSMSMeasurement>(meas);
                    subMeasurements.emplace_back(
                        new MSMSMeasurementSimulation<Method, Multi>(*msmsMeasurement, network, multiIndex));
                } else if (isInstanceOf<HNMRMeasurement>(meas)) {
                    auto hnmrMeasurement = std::dynamic_pointer_cast<HNMRMeasurement>(meas);
                    subMeasurements.emplace_back(
                        new HNMRMeasurementSimulation<Method, Multi>(*hnmrMeasurement, network, multiIndex));
                } else if (isInstanceOf<CNMRMeasurement>(meas)) {
                    auto cnmrMeasurement = std::dynamic_pointer_cast<CNMRMeasurement>(meas);
                    subMeasurements.emplace_back(
                        new CNMRMeasurementSimulation<Method, Multi>(*cnmrMeasurement, network, multiIndex));
                } else if (isInstanceOf<CumomerMeasurement>(meas)) {
                    auto cumoMeasurement = std::dynamic_pointer_cast<CumomerMeasurement>(meas);
                    subMeasurements.emplace_back(
                        new CumomerMeasurementSimulation<Method, Multi>(*cumoMeasurement, network, multiIndex));
                }

                subMeasurements.back()->setTimeStamps(this->getTimeStamps());
            }
            measurements_.push_back(subMeasurements);
        }
    }

    void setTimeStamps(const std::vector<Real> &timeStamps) override {
        ScalableMeasurementSimulation<Method, Multi>::setTimeStamps(timeStamps);

        for (auto &row : measurements_) {
            for (auto &rowMeas : row) {
                rowMeas->setTimeStamps(timeStamps);
            }
        }
    }

    std::size_t getSize() const override { return formulas_.size(); }

    RealVector evaluate(const StationarySolution &solution) const {
        RealVector value(formulas_.size());

        for (std::size_t i = 0; i < formulas_.size(); ++i) {
            std::shared_ptr<flux::symb::ExprTree> formula(formulas_[i].clone());

            for (std::size_t j = 0; j < measurements_[i].size(); ++j) {
                std::shared_ptr<flux::symb::ExprTree> measExpr(
                    flux::symb::ExprTree::val(measurements_[i][j]->evaluate(solution)(0)));
                formula->subst(variableNames_[i][j].c_str(), measExpr.get());
            }

            formula->eval(true);
            value(static_cast<Index>(i)) = formula->getDoubleValue();
        }

        return value;
    }

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const {
        std::vector<RealVector> simMeasurements;

        for (const auto &timeStamp : this->getTimeStamps()) {
            std::ignore = timeStamp;
            simMeasurements.emplace_back(formulas_.size());
        }

        for (std::size_t i = 0; i < measurements_.size(); ++i) {
            // Cache values of current sub measurement's measurements
            std::vector<std::vector<Real>> measValues;
            for (std::size_t j = 0; j < measurements_[i].size(); ++j) {
                std::vector<Real> measEval;
                for (const auto &val : measurements_[i][j]->evaluate(solution)) {
                    measEval.push_back(val(0));
                }
                measValues.push_back(measEval);
            }

            // Simulate measurements for all time points for current sub
            // measurement
            for (std::size_t k = 0; k < simMeasurements.size(); ++k) {
                std::shared_ptr<flux::symb::ExprTree> formula(formulas_[i].clone());

                for (std::size_t j = 0; j < measValues.size(); ++j) {
                    std::shared_ptr<flux::symb::ExprTree> measExpr(flux::symb::ExprTree::val(measValues[j][k]));
                    formula->subst(variableNames_[i][j].c_str(), measExpr.get());
                }

                formula->eval(true);
                simMeasurements[k](static_cast<Index>(i)) = formula->getDoubleValue();
            }
        }

        return simMeasurements;
    }

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override {
        RealVector value(formulas_.size());

        for (std::size_t i = 0; i < formulas_.size(); ++i) {
            std::shared_ptr<flux::symb::ExprTree> formula(formulas_[i].clone());

            for (std::size_t j = 0; j < measurements_[i].size(); ++j) {
                std::shared_ptr<flux::symb::ExprTree> measExpr(
                    flux::symb::ExprTree::val(measurements_[i][j]->evaluateDerivative(derivSolution)(0)));
                formula->subst(variableNames_[i][j].c_str(), measExpr.get());
            }

            formula->eval(true);
            value(static_cast<Index>(i)) = formula->getDoubleValue();
        }

        return value;
    }

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override {
        std::vector<RealVector> simMeasurements;

        for (const auto &timeStamp : this->getTimeStamps()) {
            std::ignore = timeStamp;
            simMeasurements.emplace_back(formulas_.size());
        }

        for (std::size_t i = 0; i < measurements_.size(); ++i) {
            // Cache values of current sub measurement's measurements
            std::vector<std::vector<Real>> measValues;
            for (std::size_t j = 0; j < measurements_[i].size(); ++j) {
                std::vector<Real> measEval;
                for (const auto &val : measurements_[i][j]->evaluateDerivative(derivSolution)) {
                    measEval.push_back(val(0));
                }
                measValues.push_back(measEval);
            }

            // Simulate measurements for all time points for current sub
            // measurement
            for (std::size_t k = 0; k < simMeasurements.size(); ++k) {
                std::shared_ptr<flux::symb::ExprTree> formula(formulas_[i].clone());

                for (std::size_t j = 0; j < measValues.size(); ++j) {
                    std::shared_ptr<flux::symb::ExprTree> measExpr(flux::symb::ExprTree::val(measValues[j][k]));
                    formula->subst(variableNames_[i][j].c_str(), measExpr.get());
                }

                formula->eval(true);
                simMeasurements[k](static_cast<Index>(i)) = formula->getDoubleValue();
            }
        }

        return simMeasurements;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_GENERICMEASUREMENTSIMULATION_H
