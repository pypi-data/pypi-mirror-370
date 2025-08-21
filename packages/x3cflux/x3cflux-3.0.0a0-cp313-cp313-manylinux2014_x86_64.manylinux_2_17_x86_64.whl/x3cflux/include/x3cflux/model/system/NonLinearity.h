#ifndef X3CFLUX_NONLINEARITY_H
#define X3CFLUX_NONLINEARITY_H

#include "MultiHelper.h"
#include "StateVariableOperations.h"

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi> class NonLinearity;

template <typename Method, bool Multi> class NonLinearity<Method, true, Multi> {
  public:
    typedef SystemTraits<Method, Multi> Traits;
    typedef typename Traits::FractionType Fraction;
    typedef typename Traits::SystemStateType SystemState;
    typedef std::vector<SystemState> Input;

  public:
    virtual Fraction evaluate(const Input &input) const = 0;

    virtual Fraction evaluateDerivative(const Input &input, const Input &inputDerivative) const = 0;
};

template <typename Method, bool Multi> class NonLinearity<Method, false, Multi> {
  public:
    typedef SystemTraits<Method, Multi> Traits;
    typedef typename Traits::FractionType Fraction;
    typedef typename Traits::SystemStateType SystemState;
    typedef std::conditional_t<Traits::TYPE == SystemType::CASCADED,
                               std::vector<typename IVPSolver<SystemState>::Solution>, SystemState>
        Input;

  public:
    virtual Fraction evaluate(Real time, const Input &input) const = 0;

    virtual Fraction evaluateDerivative(Real time, const Input &input, const Input &inputDerivative) const = 0;
};

template <typename Method, bool Stationary, bool Multi> class Condensation;

template <bool Multi>
class Condensation<IsotopomerMethod, false, Multi> : public NonLinearity<IsotopomerMethod, false, Multi> {
  public:
    typedef SystemTraits<IsotopomerMethod, Multi> Traits;
    typedef typename Traits::FractionType Fraction;
    typedef typename Traits::SystemStateType SystemState;
    typedef StateVariableOperations<IsotopomerMethod, Multi> StateVarOps;

  private:
    std::vector<Index> systemIndices_;

  public:
    explicit Condensation(std::vector<Index> systemIndices) : systemIndices_(std::move(systemIndices)) {}

    Fraction evaluate(Real time, const SystemState &isotopomers) const override {
        std::ignore = time;
        Fraction value = StateVarOps::get(isotopomers, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            value *= StateVarOps::get(isotopomers, systemIndices_[i]);
        }

        return value;
    }

    Fraction evaluateDerivative(Real time, const SystemState &isotopomers,
                                const SystemState &isotopomerDerivatives) const override {
        std::ignore = time;
        Fraction totalValue = StateVarOps::get(isotopomerDerivatives, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            totalValue *= StateVarOps::get(isotopomers, systemIndices_[i]);
        }

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            Fraction value = StateVarOps::get(isotopomerDerivatives, systemIndices_[i]);

            for (std::size_t j = 0; j < systemIndices_.size(); ++j) {
                if (j != i) {
                    value *= StateVarOps::get(isotopomers, systemIndices_[j]);
                }
            }

            totalValue += value;
        }

        return totalValue;
    }
};

template <typename Method, bool Stationary, bool Multi>
class Condensation : public NonLinearity<Method, true, Multi>, public NonLinearity<Method, false, Multi> {
  public:
    typedef SystemTraits<Method, Multi> Traits;
    typedef typename Traits::FractionType Fraction;
    typedef typename Traits::SystemStateType SystemState;
    typedef typename NonLinearity<Method, true, Multi>::Input StationaryInput;
    typedef typename NonLinearity<Method, false, Multi>::Input NonStationaryInput;
    typedef StateVariableOperations<Method, Multi> StateVarOps;

  private:
    std::vector<std::size_t> cascadeIndices_;
    std::vector<std::size_t> systemIndices_;

  public:
    Condensation(std::vector<std::size_t> cascadeIndices, std::vector<std::size_t> systemIndices)
        : cascadeIndices_(std::move(cascadeIndices)), systemIndices_(std::move(systemIndices)) {}

    Fraction evaluate(const StationaryInput &prevLevelSolutions) const override {
        auto firstSolution = prevLevelSolutions[cascadeIndices_.front()];
        Fraction value = StateVarOps::get(firstSolution, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            auto solution = prevLevelSolutions[cascadeIndices_[i]];
            value = StateVarOps::computeProduct(value, StateVarOps::get(solution, systemIndices_[i]),
                                                cascadeIndices_[i] + 1);
        }

        return value;
    }

    Fraction evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const {
        const auto &firstSolution = prevLevelSolutions[cascadeIndices_.front()];
        Fraction value = firstSolution(time, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            const auto &solution = prevLevelSolutions[cascadeIndices_[i]];
            value = StateVarOps::computeProduct(value, solution(time, systemIndices_[i]), cascadeIndices_[i] + 1);
        }

        return value;
    }

    Fraction evaluateDerivative(const StationaryInput &baseSolution,
                                const StationaryInput &prevLevelDerivativeSolutions) const override {
        auto firstSolution = prevLevelDerivativeSolutions[cascadeIndices_.front()];
        Fraction totalValue = StateVarOps::get(firstSolution, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            auto solution = baseSolution[cascadeIndices_[i]];
            totalValue = StateVarOps::computeProduct(totalValue, StateVarOps::get(solution, systemIndices_[i]),
                                                     cascadeIndices_[i] + 1);
        }

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            const auto &midSolution = prevLevelDerivativeSolutions[cascadeIndices_[i]];
            Fraction value = StateVarOps::get(midSolution, systemIndices_[i]);

            for (std::size_t j = 0; j < systemIndices_.size(); ++j) {
                if (j != i) {
                    const auto &solution = baseSolution[cascadeIndices_[j]];
                    value = StateVarOps::computeProduct(value, StateVarOps::get(solution, systemIndices_[j]),
                                                        cascadeIndices_[j] + 1);
                }
            }

            totalValue += value;
        }

        return totalValue;
    }

    Fraction evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                                const NonStationaryInput &prevLevelDerivativeSolutions) const {
        const auto &firstSolution = prevLevelDerivativeSolutions[cascadeIndices_.front()];
        Fraction totalValue = firstSolution(time, systemIndices_.front());

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            const auto &solution = baseSolution[cascadeIndices_[i]];
            totalValue =
                StateVarOps::computeProduct(totalValue, solution(time, systemIndices_[i]), cascadeIndices_[i] + 1);
        }

        for (std::size_t i = 1; i < systemIndices_.size(); ++i) {
            const auto &midSolution = prevLevelDerivativeSolutions[cascadeIndices_[i]];
            Fraction value = midSolution(time, systemIndices_[i]);

            for (std::size_t j = 0; j < systemIndices_.size(); ++j) {
                if (j != i) {
                    const auto &solution = baseSolution[cascadeIndices_[j]];
                    value =
                        StateVarOps::computeProduct(value, solution(time, systemIndices_[j]), cascadeIndices_[j] + 1);
                }
            }

            totalValue += value;
        }

        return totalValue;
    }
};

template <typename Method, bool Stationary, bool Multi> class ConstantSubstrateInput;

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<IsotopomerMethod, Stationary, Multi>
    : public NonLinearity<IsotopomerMethod, true, Multi>, public NonLinearity<IsotopomerMethod, false, Multi> {
  public:
    typedef NonLinearity<IsotopomerMethod, Stationary, Multi> Base;
    using typename Base::Fraction;
    using typename Base::SystemState;
    typedef typename NonLinearity<IsotopomerMethod, true, Multi>::Input StationaryInput;
    typedef typename NonLinearity<IsotopomerMethod, false, Multi>::Input NonStationaryInput;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(Fraction concentration) : concentration_(concentration) {}

    Fraction evaluate(const StationaryInput &prevLevelSolutions) const override {
        std::ignore = prevLevelSolutions;
        return concentration_;
    }

    Fraction evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const override {
        std::ignore = time;
        std::ignore = prevLevelSolutions;
        return concentration_;
    }

    Fraction evaluateDerivative(const StationaryInput &baseSolution,
                                const StationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return RealVector::Zero(concentration_.size());
        } else {
            return concentration_;
        }
    }

    Fraction evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                                const NonStationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = time;
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return RealVector::Zero(concentration_.size());
        } else {
            return concentration_;
        }
    }
};

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<CumomerMethod, Stationary, Multi> : public NonLinearity<CumomerMethod, true, Multi>,
                                                                 public NonLinearity<CumomerMethod, false, Multi> {
  public:
    typedef NonLinearity<CumomerMethod, Stationary, Multi> Base;
    using typename Base::Fraction;
    using typename Base::SystemState;
    typedef typename NonLinearity<CumomerMethod, true, Multi>::Input StationaryInput;
    typedef typename NonLinearity<CumomerMethod, false, Multi>::Input NonStationaryInput;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(const MultiAdapt<std::shared_ptr<ConstantSubstrate>> &substrate,
                                    const boost::dynamic_bitset<> &state)
        : concentration_(MultiHelper<Multi>::template apply<Fraction>(&computeCumomer, substrate, state)) {}

    Fraction evaluate(const StationaryInput &prevLevelSolutions) const override {
        std::ignore = prevLevelSolutions;
        return concentration_;
    }

    Fraction evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const override {
        std::ignore = time;
        std::ignore = prevLevelSolutions;
        return concentration_;
    }

    Fraction evaluateDerivative(const StationaryInput &baseSolution,
                                const StationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return RealVector::Zero(concentration_.size());
        } else {
            return 0.;
        }
    }

    Fraction evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                                const NonStationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = time;
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return RealVector::Zero(concentration_.size());
        } else {
            return 0.;
        }
    }

  private:
    static Real computeCumomer(const std::shared_ptr<ConstantSubstrate> &substrate,
                               const boost::dynamic_bitset<> &state) {
        Real value = 0.;
        for (const auto &pair : substrate->getProfiles()) {
            if (state.is_subset_of(pair.first)) {
                value += pair.second;
            }
        }
        return value;
    }
};

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<EMUMethod, Stationary, Multi> : public NonLinearity<EMUMethod, true, Multi>,
                                                             public NonLinearity<EMUMethod, false, Multi> {
  public:
    typedef NonLinearity<EMUMethod, Stationary, Multi> Base;
    using typename Base::Fraction;
    using typename Base::SystemState;
    typedef typename NonLinearity<EMUMethod, true, Multi>::Input StationaryInput;
    typedef typename NonLinearity<EMUMethod, false, Multi>::Input NonStationaryInput;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(const MultiAdapt<std::shared_ptr<ConstantSubstrate>> &substrate,
                                    const boost::dynamic_bitset<> &state)
        : concentration_(computeEMU(substrate, state)) {}

    Fraction evaluate(const StationaryInput &input) const override {
        std::ignore = input;
        return concentration_;
    }

    Fraction evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const override {
        std::ignore = time;
        std::ignore = prevLevelSolutions;
        return concentration_;
    }

    Fraction evaluateDerivative(const StationaryInput &baseSolution,
                                const StationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return Fraction::Zero(concentration_.rows(), concentration_.cols());
        } else {
            return Fraction::Zero(concentration_.size());
        }
    }

    Fraction evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                                const NonStationaryInput &prevLevelDerivativeSolutions) const override {
        std::ignore = time;
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolutions;
        if constexpr (Multi) {
            return Fraction::Zero(concentration_.rows(), concentration_.cols());
        } else {
            return Fraction::Zero(concentration_.size());
        }
    }

  private:
    static RealVector computeEMU(const std::shared_ptr<ConstantSubstrate> &substrate,
                                 const boost::dynamic_bitset<> &state) {
        RealVector value = RealVector::Zero(static_cast<Index>(state.count() + 1));
        for (const auto &pair : substrate->getProfiles()) {
            value[static_cast<int>((state & pair.first).count())] += pair.second;
        }
        return value;
    }

    static RealVector computeEMU(const std::vector<std::shared_ptr<ConstantSubstrate>> &parSubstrate,
                                 const boost::dynamic_bitset<> &state) {
        auto size = static_cast<Index>(state.count() + 1), numMulti = static_cast<Index>(parSubstrate.size());
        RealVector value = RealVector::Zero(size * numMulti);

        value.head(size) = computeEMU(parSubstrate.front(), state);
        for (Index parSubInd = 1; parSubInd < numMulti - 1; ++parSubInd) {
            value.segment(parSubInd * size, size) = computeEMU(parSubstrate[parSubInd], state);
        }
        value.tail(size) = computeEMU(parSubstrate.back(), state);

        return value;
    }
};

template <typename Method, bool Multi> class VariateSubstrateInputBase : public NonLinearity<Method, false, Multi> {
  public:
    typedef NonLinearity<Method, false, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    typedef std::conditional_t<Multi, Real, RealVector> EvaluationResult;

  public:
    static Real evaluateSimpleInput(const VariateProfile &inputFunctions, Real time) {
        auto inFunIt = inputFunctions.begin();

        // No switch conditions supplied (only 0)
        if (inputFunctions.size() == 1) {
            return evaluateExpression(std::get<2>(*inFunIt), time);
        }

        Real lowerBound, upperBound;
        for (auto tuple : inputFunctions) {
            lowerBound = std::get<0>(tuple);
            upperBound = std::get<1>(tuple);

            if (time >= lowerBound and time < upperBound) {
                return evaluateExpression(std::get<2>(tuple), time);
            }
        }

        return 0.;
    }

    static Real evaluateSimpleInputDerivative(const VariateProfile &inputFunctions, Real time) {
        std::ignore = inputFunctions;
        std::ignore = time;
        return 0.;
    }

  private:
    static Real evaluateExpression(const flux::symb::ExprTree &expr, Real time) {
        std::shared_ptr<flux::symb::ExprTree> value(expr.clone());
        std::shared_ptr<flux::symb::ExprTree> timeExpr(flux::symb::ExprTree::val(time));
        value->subst("t", timeExpr.get());
        value->eval(true);
        return value->getDoubleValue();
    }
};

template <typename Method, bool Multi> class VariateSubstrateInput;

template <bool Multi>
class VariateSubstrateInput<IsotopomerMethod, Multi> : public VariateSubstrateInputBase<IsotopomerMethod, Multi> {
  public:
    typedef VariateSubstrateInputBase<IsotopomerMethod, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<VariateProfile> substrate_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<VariateProfile> &inputFunctions) : substrate_(inputFunctions) {}

    Fraction evaluate(Real time, const Input &input) const override {
        std::ignore = input;
        return MultiHelper<Multi>::template apply<Fraction>(&Base::evaluateSimpleInput, substrate_, time);
    }

    Fraction evaluateDerivative(Real time, const Input &input, const Input &inputDerivative) const override {
        std::ignore = input;
        std::ignore = inputDerivative;
        return MultiHelper<Multi>::template apply<Fraction>(&Base::evaluateSimpleInputDerivative, substrate_, time);
    }
};

template <bool Multi>
class VariateSubstrateInput<CumomerMethod, Multi> : public VariateSubstrateInputBase<CumomerMethod, Multi> {
  public:
    typedef VariateSubstrateInputBase<CumomerMethod, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<std::shared_ptr<VariateSubstrate>> substrate_;
    boost::dynamic_bitset<> state_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<std::shared_ptr<VariateSubstrate>> &substrate,
                                   boost::dynamic_bitset<> state)
        : substrate_(substrate), state_(std::move(state)) {}

    Fraction evaluate(Real time, const Input &prevLevelSolutions) const override {
        std::ignore = prevLevelSolutions;
        return MultiHelper<Multi>::template apply<Fraction>(&evaluateCumomer, substrate_, state_, time);
    }

    Fraction evaluateDerivative(Real time, const Input &baseSolution,
                                const Input &prevLevelDerivativeSolution) const override {
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolution;
        return MultiHelper<Multi>::template apply<Fraction>(&evaluateCumomerDerivative, substrate_, state_, time);
    }

  private:
    static Real evaluateCumomer(const std::shared_ptr<VariateSubstrate> &substrate,
                                const boost::dynamic_bitset<> &state, Real time) {
        Real value = 0.;
        for (const auto &pair : substrate->getProfiles()) {
            if (state.is_subset_of(pair.first)) {
                value += Base::evaluateSimpleInput(pair.second, time);
            }
        }
        return value;
    }

    static Real evaluateCumomerDerivative(const std::shared_ptr<VariateSubstrate> &substrate,
                                          const boost::dynamic_bitset<> &state, Real time) {
        std::ignore = substrate;
        std::ignore = state;
        std::ignore = time;
        return 0.;
    }
};

template <bool Multi>
class VariateSubstrateInput<EMUMethod, Multi> : public VariateSubstrateInputBase<EMUMethod, Multi> {
  public:
    typedef VariateSubstrateInputBase<EMUMethod, Multi> Base;
    using typename Base::EvaluationResult;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<std::shared_ptr<VariateSubstrate>> substrate_;
    boost::dynamic_bitset<> state_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<std::shared_ptr<VariateSubstrate>> &substrate,
                                   boost::dynamic_bitset<> state)
        : substrate_(substrate), state_(std::move(state)) {}

    Fraction evaluate(Real time, const Input &prevLevelSolutions) const override {
        std::ignore = prevLevelSolutions;
        return evaluateEMU(substrate_, state_, time);
    }

    Fraction evaluateDerivative(Real time, const Input &baseSolution,
                                const Input &prevLevelDerivativeSolution) const override {
        std::ignore = baseSolution;
        std::ignore = prevLevelDerivativeSolution;
        return evaluateEMUDerivative(substrate_, state_, time);
    }

  private:
    static RealVector evaluateEMU(const std::vector<std::shared_ptr<VariateSubstrate>> &parSubstrate,
                                  const boost::dynamic_bitset<> &state, Real time) {
        auto size = static_cast<Index>(state.count() + 1), numMulti = static_cast<Index>(parSubstrate.size());
        RealVector value = RealVector::Zero(size * numMulti);

        value.head(size) = evaluateEMU(parSubstrate.front(), state, time);
        for (Index parSubInd = 1; parSubInd < numMulti - 1; ++parSubInd) {
            value.segment(parSubInd * size, size) = evaluateEMU(parSubstrate[parSubInd], state, time);
        }
        value.tail(size) = evaluateEMU(parSubstrate.back(), state, time);

        return value;
    }

    static RealVector evaluateEMU(const std::shared_ptr<VariateSubstrate> &substrate,
                                  const boost::dynamic_bitset<> &state, Real time) {
        RealVector value = RealVector::Zero(static_cast<Index>(state.count()) + 1);
        for (const auto &pair : substrate->getProfiles()) {
            value[static_cast<Index>((state & pair.first).count())] += Base::evaluateSimpleInput(pair.second, time);
        }
        return value;
    }

    static RealVector evaluateEMUDerivative(const std::vector<std::shared_ptr<VariateSubstrate>> &parSubstrate,
                                            const boost::dynamic_bitset<> &state, Real time) {
        std::ignore = time;
        auto size = static_cast<Index>(state.count() + 1), numMulti = static_cast<Index>(parSubstrate.size());
        return RealVector::Zero(size * numMulti);
    }

    static RealVector evaluateEMUDerivative(const std::shared_ptr<VariateSubstrate> &substrate,
                                            const boost::dynamic_bitset<> &state, Real time) {
        std::ignore = substrate;
        std::ignore = time;
        return RealVector::Zero(static_cast<Index>(state.count()) + 1);
    }
};

} // namespace x3cflux

#endif // X3CFLUX_NONLINEARITY_H
