#ifndef X3CFLUX_NONLINEARELEMENT_H
#define X3CFLUX_NONLINEARELEMENT_H

#include <utility>

#include "LabelingSystem.h"
#include "NonLinearity.h"
#include "ParameterAccessor.h"

namespace x3cflux {

/// \brief Base class for numerical non-linear elements
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementBase {
  public:
    typedef typename SystemTraits<Method, Multi>::FractionType Fraction;
    typedef typename SystemTraits<Method, Multi>::SystemStateType SystemState;
    typedef NonLinearity<Method, Stationary, Multi> NonLinearFunction;
    typedef typename NonLinearFunction::Input Input;

  private:
    Index rowIndex_;
    std::vector<Real> coefficients_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create base for numerical non-linear elements
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementBase(Index rowIndex, std::vector<Real> coefficients,
                                std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions)
        : rowIndex_(rowIndex), coefficients_(std::move(coefficients)),
          nonLinearFunctions_(std::move(nonLinearFunctions)) {}

    /// \return row index of the element
    Index getRowIndex() const { return rowIndex_; }

    /// \return coefficients of the linear combination
    const std::vector<Real> &getCoefficients() const { return coefficients_; }

    /// \return non-linear functions to combine
    const std::vector<std::shared_ptr<NonLinearFunction>> &getNonLinearFunctions() const { return nonLinearFunctions_; }
};

/// \brief Numerical non-linear element
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElement;

/// \brief Numerical non-linear element for IST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElement<Method, true, Multi> : public NumericNonLinearElementBase<Method, true, Multi> {
  public:
    typedef NumericNonLinearElementBase<Method, true, Multi> Base;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    typedef typename NonLinearFunction::Input Input;

  public:
    /// Create IST MFA non-linear element
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElement(Index rowIndex, const std::vector<Real> &coefficients,
                            const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions)
        : Base(rowIndex, coefficients, nonLinearFunctions) {}

    /// Evaluate linear combination of non-linearities
    /// \param input evaluation input
    /// \return element value
    Fraction evaluate(const Input &input) const {
        const auto &coeffs = this->getCoefficients();
        const auto &nonLinFuncs = this->getNonLinearFunctions();

        Fraction value = coeffs[0] * nonLinFuncs[0]->evaluate(input);
        for (std::size_t linCombIndex = 1; linCombIndex < coeffs.size(); ++linCombIndex) {
            value += coeffs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluate(input);
        }

        return value;
    }
};

/// \brief Numerical non-linear element for INST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElement<Method, false, Multi> : public NumericNonLinearElementBase<Method, false, Multi> {
  public:
    typedef NumericNonLinearElementBase<Method, false, Multi> Base;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    typedef typename NonLinearFunction::Input Input;

  public:
    /// Create IST MFA non-linear element
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElement(Index rowIndex, const std::vector<Real> &coefficients,
                            const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions)
        : Base(rowIndex, coefficients, nonLinearFunctions) {}

    /// Evaluate linear combination of non-linearities
    /// \param time time point at which to evaluate
    /// \param input evaluation input
    /// \return element value
    Fraction evaluate(Real time, const Input &input) const {
        const auto &coeffs = this->getCoefficients();
        const auto &nonLinFuncs = this->getNonLinearFunctions();

        Fraction value = coeffs[0] * nonLinFuncs[0]->evaluate(time, input);
        for (std::size_t linCombIndex = 1; linCombIndex < coeffs.size(); ++linCombIndex) {
            value += coeffs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluate(time, input);
        }

        return value;
    }
};

/// \brief Base class for numerical non-linear element derivatives
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementDerivativeBase {
  public:
    typedef typename SystemTraits<Method, Multi>::FractionType Fraction;
    typedef typename SystemTraits<Method, Multi>::SystemStateType SystemState;
    typedef NonLinearity<Method, Stationary, Multi> NonLinearFunction;
    typedef typename NonLinearFunction::Input Input;

  private:
    Index rowIndex_;
    std::vector<Real> coefficients_;
    std::vector<Real> coefficientDerivatives_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create base of numerical non-linear element derivative
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivativeBase(Index rowIndex, std::vector<Real> coefficients,
                                          std::vector<Real> coefficientDerivatives,
                                          std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions)
        : rowIndex_(rowIndex), coefficients_(std::move(coefficients)),
          coefficientDerivatives_(std::move(coefficientDerivatives)),
          nonLinearFunctions_(std::move(nonLinearFunctions)) {}

    /// \return row index of the element
    Index getRowIndex() const { return rowIndex_; }

    /// \return coefficient of the linear combination
    const std::vector<Real> &getCoefficients() const { return coefficients_; }

    /// \return partial derivative of the coefficients
    const std::vector<Real> &getCoefficientDerivatives() const { return coefficientDerivatives_; }

    /// \return non-linear functions to combine
    const std::vector<std::shared_ptr<NonLinearFunction>> &getNonLinearFunctions() const { return nonLinearFunctions_; }
};

/// \brief Numerical non-linear element derivative
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementDerivative;

/// \brief Numerical non-linear element derivative for IST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElementDerivative<Method, true, Multi>
    : public NumericNonLinearElementDerivativeBase<Method, true, Multi> {
  public:
    typedef NumericNonLinearElementDerivativeBase<Method, true, Multi> Base;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    typedef typename NonLinearFunction::Input Input;

  public:
    /// Create numerical IST MFA non-linear element derivate
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivative(Index rowIndex, const std::vector<Real> &coefficients,
                                      const std::vector<Real> &coefficientDerivatives,
                                      const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions)
        : Base(rowIndex, coefficients, coefficientDerivatives, nonLinearFunctions) {}

    /// Evaluate linear combination of non-linearities and their derivatives
    /// \param input evaluation input
    /// \param inputDerivative derivative of evaluation input
    /// \return element partial derivate value
    Fraction evaluate(const Input &input, const Input &inputDerivative) const {
        const auto &coeffs = this->getCoefficients();
        const auto &coeffDerivs = this->getCoefficientDerivatives();
        const auto &nonLinFuncs = this->getNonLinearFunctions();

        Fraction value = coeffs[0] * nonLinFuncs[0]->evaluateDerivative(input, inputDerivative) +
                         coeffDerivs[0] * nonLinFuncs[0]->evaluate(input);
        for (std::size_t linCombIndex = 1; linCombIndex < coeffs.size(); ++linCombIndex) {
            value += coeffs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluateDerivative(input, inputDerivative) +
                     coeffDerivs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluate(input);
        }

        return value;
    }
};

/// \brief Numerical non-linear element derivative for INST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElementDerivative<Method, false, Multi>
    : public NumericNonLinearElementDerivativeBase<Method, false, Multi> {
  public:
    typedef NumericNonLinearElementDerivativeBase<Method, false, Multi> Base;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    typedef typename NonLinearFunction::Input Input;

  public:
    /// Create numerical INST MFA non-linear element derivate
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivative(Index rowIndex, const std::vector<Real> &coefficients,
                                      const std::vector<Real> &coefficientDerivatives,
                                      const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions)
        : Base(rowIndex, coefficients, coefficientDerivatives, nonLinearFunctions) {}

    /// Evaluate linear combination of non-linearities and their derivatives
    /// \param input evaluation input
    /// \param inputDerivative derivative of evaluation input
    /// \return element partial derivate value
    Fraction evaluate(Real time, const Input &input, const Input &inputDerivative) const {
        const auto &coeffs = this->getCoefficients();
        const auto &coeffDerivs = this->getCoefficientDerivatives();
        const auto &nonLinFuncs = this->getNonLinearFunctions();

        Fraction value = coeffs[0] * nonLinFuncs[0]->evaluateDerivative(time, input, inputDerivative) +
                         coeffDerivs[0] * nonLinFuncs[0]->evaluate(time, input);
        for (std::size_t linCombIndex = 1; linCombIndex < coeffs.size(); ++linCombIndex) {
            value +=
                coeffs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluateDerivative(time, input, inputDerivative) +
                coeffDerivs[linCombIndex] * nonLinFuncs[linCombIndex]->evaluate(time, input);
        }

        return value;
    }
};

/// \brief Symbolic element that is non-linear
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class SymbolicNonLinearElement {
  public:
    typedef NonLinearity<Method, Stationary, Multi> NonLinearFunction;
    typedef NumericNonLinearElement<Method, Stationary, Multi> EvaluatedNonLinearElement;
    typedef NumericNonLinearElementDerivative<Method, Stationary, Multi> EvaluatedNonLinearElementDerivative;

  private:
    Index rowIndex_;
    Index poolSizeIndex_;
    std::vector<std::pair<std::size_t, bool>> fluxCoefficients_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create non-linear symbolic element
    /// \param rowIndex row index of element
    /// \param poolSizeIndex index of metabolic pool size corresponding to the row
    explicit SymbolicNonLinearElement(Index rowIndex, Index poolSizeIndex)
        : rowIndex_(rowIndex), poolSizeIndex_(poolSizeIndex) {}

    /// Add non-linearity with flux coefficient to the element
    /// \param reactionIndex index of metabolic reaction associated with flux
    /// \param forward forward or backward flux
    /// \param nonLinearFunction non-linear function
    void addNonLinearity(std::size_t reactionIndex, bool forward,
                         const std::shared_ptr<NonLinearFunction> &nonLinearFunction) {
        fluxCoefficients_.emplace_back(reactionIndex, forward);
        nonLinearFunctions_.push_back(nonLinearFunction);
    }

    /// \return row index of element
    Index getRowIndex() const { return rowIndex_; }

    /// \return index of metabolic pool size corresponding to the row
    Index getPoolSizeIndex() const { return poolSizeIndex_; }

    /// \return list of index and type representation of metabolic fluxes
    const std::vector<std::pair<std::size_t, bool>> &getFluxCoefficients() const { return fluxCoefficients_; }

    /// \return list of non-linear functions
    const std::vector<std::shared_ptr<NonLinearFunction>> &getNonLinearFunctions() const { return nonLinearFunctions_; }

    /// Semi-evaluate the symbolic summation of non-linearities
    /// \param accessor accessor of metabolic fluxes
    /// \return linear combination of non-linearities
    EvaluatedNonLinearElement evaluate(const ParameterAccessor &accessor) const {
        std::vector<Real> coefficients;

        for (const auto &flux : this->getFluxCoefficients()) {
            if constexpr (Stationary) {
                coefficients.push_back(accessor.getFlux(flux.first, flux.second));
            } else {
                coefficients.push_back(accessor.getFlux(flux.first, flux.second) /
                                       accessor.getPoolSize(this->getPoolSizeIndex()));
            }
        }

        return {this->getRowIndex(), coefficients, this->getNonLinearFunctions()};
    }

    /// Semi-evaluate the partial derivative of the symbolic summation of non-linearities
    /// \param accessor accessor of metabolic fluxes and partial derivatives
    /// \return linear combination of non-linearities and their partial derivatives
    EvaluatedNonLinearElementDerivative evaluateDerivative(const DerivativeParameterAccessor &accessor) const {
        std::vector<Real> coefficients, coefficientDerivatives;

        if constexpr (Stationary) {
            for (const auto &flux : this->getFluxCoefficients()) {
                coefficients.push_back(accessor.getFlux(flux.first, flux.second));
                coefficientDerivatives.push_back(accessor.getFluxDerivative(flux.first, flux.second));
            }
        } else {
            Real poolSize = accessor.getPoolSize(this->getPoolSizeIndex());
            Real poolSizeDeriv = accessor.getPoolSizeDerivative(this->getPoolSizeIndex());
            for (const auto &flux : this->getFluxCoefficients()) {
                coefficients.push_back(accessor.getFlux(flux.first, flux.second) / poolSize);

                if (std::fabs(poolSizeDeriv) <= std::numeric_limits<Real>::epsilon()) {
                    coefficientDerivatives.push_back(accessor.getFluxDerivative(flux.first, flux.second) / poolSize);
                } else {
                    coefficientDerivatives.push_back(-accessor.getFlux(flux.first, flux.second) /
                                                     (poolSize * poolSize));
                }
            }
        }

        return {this->getRowIndex(), coefficients, coefficientDerivatives, this->getNonLinearFunctions()};
    }
};

} // namespace x3cflux

#endif // X3CFLUX_NONLINEARELEMENT_H
