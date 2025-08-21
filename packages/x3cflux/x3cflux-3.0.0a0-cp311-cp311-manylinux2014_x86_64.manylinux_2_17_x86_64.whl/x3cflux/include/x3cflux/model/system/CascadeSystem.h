#ifndef X3CFLUX_CASCADESYSTEM_H
#define X3CFLUX_CASCADESYSTEM_H

#include "LabelingSystem.h"
#include "NonLinearElement.h"
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>

#include <utility>

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi = false> class CascadeLevelSystem;

/// \brief Level system of IST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelSystem<Method, true, Multi>
    : public LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> {
  public:
    typedef LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> Base;
    using typename Base::RhsType;

    typedef RhsType Solution;
    typedef NumericNonLinearElement<Method, true, Multi> NonLinearElement;
    typedef RhsType SystemCondition;
    typedef StateVariableOperations<Method, Multi> StateVarOps;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<RhsType> &prevLevelSolutions_;

  public:
    /// Create level system of IST cascade
    /// \param jacobiMatrix linear part
    /// \param nonLinearities non-linear part
    /// \param initialGuess initial labeling state
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelSystem(const RealSparseMatrix &jacobiMatrix, std::vector<NonLinearElement> nonLinearities,
                       const RhsType &initialGuess, const std::vector<Solution> &prevLevelSolutions)
        : Base(jacobiMatrix, createRhs(initialGuess.rows(), initialGuess.cols(), nonLinearities, prevLevelSolutions),
               initialGuess),
          nonLinearities_(nonLinearities), prevLevelSolutions_(prevLevelSolutions) {}

  private:
    static RhsType createRhs(Index numRows, Index numCols, const std::vector<NonLinearElement> &nonLinearities,
                             const std::vector<Solution> &prevLevelSolutions) {
        RhsType eval = RhsType::Zero(numRows, numCols);
        for (const auto &nonLin : nonLinearities) {
            StateVarOps::assign(eval, nonLin.getRowIndex(), -nonLin.evaluate(prevLevelSolutions));
        }
        return eval;
    }
};

/// \brief Level system of INST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelSystem<Method, false, Multi>
    : public LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> {
  public:
    typedef LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> Base;
    using typename Base::State;
    typedef typename IVPSolver<State>::Solution Solution;

    typedef NumericNonLinearElement<Method, false, Multi> NonLinearElement;
    typedef std::pair<Real, State> SystemCondition;
    typedef StateVariableOperations<Method, Multi> StateVarOps;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<Solution> &prevLevelSolutions_;

  public:
    /// Create level system of INST cascade
    /// \param jacobiMatrix linear part
    /// \param nonLinearities non-linear part
    /// \param condition initial labeling state
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelSystem(const RealSparseMatrix &jacobiMatrix, std::vector<NonLinearElement> nonLinearities,
                       const SystemCondition &condition, const std::vector<Solution> &prevLevelSolutions)
        : Base(0., condition.first, condition.second, jacobiMatrix), nonLinearities_(nonLinearities),
          prevLevelSolutions_(prevLevelSolutions) {}

    State evaluateInhomogeneity(Real time) const override {
        State eval = State::Zero(this->getSize(), this->getNumStates());
        for (const auto &nonLin : nonLinearities_) {
            StateVarOps::assign(eval, nonLin.getRowIndex(), nonLin.evaluate(time, prevLevelSolutions_));
        }
        return eval;
    }
};

template <typename Method, bool Stationary, bool Multi = false> class CascadeLevelDerivativeSystem;

/// \brief Level system of IST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelDerivativeSystem<Method, true, Multi>
    : public LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> {
  public:
    typedef LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> Base;
    using typename Base::RhsType;

    typedef RhsType Solution;
    typedef NumericNonLinearElementDerivative<Method, true, Multi> NonLinearElement;
    typedef RhsType SystemCondition;
    typedef StateVariableOperations<Method, Multi> StateVarOps;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<RhsType> &prevLevelSolutions_;

  public:
    /// Create level system of derivative IST cascade
    /// \param jacobiMatrix linear part
    /// \param jacobiMatrixDerivative partial derivative of linear part
    /// \param nonLinearities non-linear part
    /// \param initialGuess initial labeling state
    /// \param nonDerivSolutions solution of base system
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelDerivativeSystem(const RealSparseMatrix &jacobiMatrix, const RealSparseMatrix &jacobiMatrixDerivative,
                                 std::vector<NonLinearElement> nonLinearities, const RhsType &initialGuess,
                                 const std::vector<Solution> &nonDerivSolutions,
                                 const std::vector<Solution> &prevLevelSolutions)
        : Base(jacobiMatrix,
               createRhs(initialGuess.rows(), initialGuess.cols(), nonLinearities, nonDerivSolutions,
                         prevLevelSolutions) -
                   jacobiMatrixDerivative * nonDerivSolutions[prevLevelSolutions.size()], // todo: very hacky, replace
               initialGuess),
          nonLinearities_(nonLinearities), prevLevelSolutions_(prevLevelSolutions) {}

  private:
    static RhsType createRhs(Index numRows, Index numCols, const std::vector<NonLinearElement> &nonLinearities,
                             const std::vector<Solution> &nonDerivSolutions,
                             const std::vector<Solution> &prevLevelSolutions) {
        RhsType eval = RhsType::Zero(numRows, numCols);
        for (const auto &nonLin : nonLinearities) {
            StateVarOps::assign(eval, nonLin.getRowIndex(), -nonLin.evaluate(nonDerivSolutions, prevLevelSolutions));
        }
        return eval;
    }
};

/// \brief Level system of derivative INST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelDerivativeSystem<Method, false, Multi>
    : public LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> {
  public:
    typedef LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> Base;
    using typename Base::State;
    typedef typename IVPSolver<State>::Solution Solution;

    typedef NumericNonLinearElementDerivative<Method, false, Multi> NonLinearElement;
    typedef std::pair<Real, State> SystemCondition;
    typedef StateVariableOperations<Method, Multi> StateVarOps;

  private:
    RealSparseMatrix jacobiMatrixDerivative_;
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<Solution> &nonDerivSolutions_;
    const std::vector<Solution> &prevLevelSolutions_;

  public:
    /// Create level system of derivative INST cascade
    /// \param jacobiMatrix linear part
    /// \param jacobiMatrixDerivative partial derivative of linear part
    /// \param nonLinearities non-linear part
    /// \param condition initial labeling state
    /// \param nonDerivSolutions solution of base system
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelDerivativeSystem(const RealSparseMatrix &jacobiMatrix, const RealSparseMatrix &jacobiMatrixDerivative,
                                 std::vector<NonLinearElement> nonLinearities, const SystemCondition &condition,
                                 const std::vector<Solution> &nonDerivSolutions,
                                 const std::vector<Solution> &prevLevelSolutions)
        : Base(0., condition.first, condition.second, jacobiMatrix), jacobiMatrixDerivative_(jacobiMatrixDerivative),
          nonLinearities_(nonLinearities), nonDerivSolutions_(nonDerivSolutions),
          prevLevelSolutions_(prevLevelSolutions) {}

    State evaluateInhomogeneity(Real time) const override {
        State eval = State::Zero(this->getSize(), this->getNumStates());
        for (const auto &nonLin : nonLinearities_) {
            StateVarOps::assign(eval, nonLin.getRowIndex(),
                                nonLin.evaluate(time, nonDerivSolutions_, prevLevelSolutions_));
        }

        return eval + jacobiMatrixDerivative_ *
                          nonDerivSolutions_[prevLevelSolutions_.size()](time); // todo: very hacky, replace
    }
};

template <typename SystemStateType>
SystemStateType reduceSystemState(const SystemStateType &state, const std::vector<Index> &nonZeroIndices) {
    if constexpr (std::is_same<SystemStateType, RealVector>::value) {
        return state(nonZeroIndices).eval();
    } else {
        return state(nonZeroIndices, Eigen::all).eval();
    }
}

template <bool IsDerivative, typename NonLinearElement, typename Condition>
auto reduceSystem(const RealSparseMatrix &linearCoefficients, const std::vector<NonLinearElement> &nonLinearElements,
                  const Condition &condition, const std::vector<Index> &nonZeroIndices) {
    auto reducedLinCoeffs = linearCoefficients.toDense()(nonZeroIndices, nonZeroIndices).sparseView().eval();
    std::vector<NonLinearElement> reducedNonLinElems;
    for (Index i = 0; i < static_cast<Index>(nonZeroIndices.size()); ++i) {
        auto it = std::find_if(nonLinearElements.begin(), nonLinearElements.end(),
                               [i, &nonZeroIndices](const NonLinearElement &nonLinElem) {
                                   return nonLinElem.getRowIndex() == nonZeroIndices[i];
                               });
        if (it != nonLinearElements.end()) {
            if constexpr (IsDerivative) {
                reducedNonLinElems.emplace_back(it->getRowIndex() - (nonZeroIndices[i] - i), it->getCoefficients(),
                                                it->getCoefficientDerivatives(), it->getNonLinearFunctions());
            } else {
                reducedNonLinElems.emplace_back(it->getRowIndex() - (nonZeroIndices[i] - i), it->getCoefficients(),
                                                it->getNonLinearFunctions());
            }
        }
    }

    if constexpr (std::is_same<Condition, RealVector>::value or std::is_same<Condition, RealMatrix>::value) {
        return std::make_tuple(reducedLinCoeffs, reducedNonLinElems, reduceSystemState(condition, nonZeroIndices));
    } else {
        return std::make_tuple(reducedLinCoeffs, reducedNonLinElems,
                               std::make_pair(condition.first, reduceSystemState(condition.second, nonZeroIndices)));
    }
}

template <typename SystemStateType>
SystemStateType expandSystemState(const SystemStateType &reducedState, const std::vector<Index> &zeroIndices) {
    if constexpr (std::is_same<SystemStateType, RealVector>::value) {
        std::vector<Real> expandedStateValues(reducedState.data(), reducedState.data() + reducedState.size());
        for (const auto &zeroIdx : zeroIndices) {
            expandedStateValues.insert(expandedStateValues.begin() + zeroIdx, 0);
        }
        return Eigen::Map<RealVector>{expandedStateValues.data(), static_cast<Index>(expandedStateValues.size())};
    } else {
        Index reducedSize = reducedState.rows();
        RealMatrix expandedState(reducedSize + zeroIndices.size(), reducedState.cols());
        expandedState.block(0, 0, reducedSize, reducedState.cols()) = reducedState;

        Index currentSize = reducedSize;
        for (const auto &zeroIdx : zeroIndices) {
            if (zeroIdx < currentSize) {
                expandedState.middleRows(zeroIdx + 1, currentSize - zeroIdx) =
                    expandedState.middleRows(zeroIdx, currentSize - zeroIdx).eval();
            }
            expandedState.row(zeroIdx).setZero();
            ++currentSize;
        }

        return expandedState;
    }
};

template <typename SolutionType>
SolutionType expandSystem(const SolutionType &reducedSolution, const std::vector<Index> &zeroIndices) {
    if constexpr (std::is_same<SolutionType, RealVector>::value or std::is_same<SolutionType, RealMatrix>::value) {
        return expandSystemState(reducedSolution, zeroIndices);
    } else {
        const auto &reducedFunctionValues = reducedSolution.getFunctionValues(),
                   &reducedDerivativeValues = reducedSolution.getDerivativeValues();
        std::vector<typename SolutionType::FunctionValue> functionValues, derivativeValues;
        for (std::size_t i = 0; i < reducedFunctionValues.size(); ++i) {
            functionValues.push_back(expandSystemState(reducedFunctionValues[i], zeroIndices));
            derivativeValues.push_back(expandSystemState(reducedDerivativeValues[i], zeroIndices));
        }

        return {reducedSolution.getPlaces(), functionValues, derivativeValues};
    }
}

/// \brief Cascade labeling system
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeSystem : public LabelingSystem<Method, Stationary, Multi> {
  public:
    typedef LabelingSystem<Method, Stationary, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    typedef CascadeLevelSystem<Method, Stationary, Multi> LevelSystem;
    typedef typename LevelSystem::SystemCondition SystemCondition;

    typedef NumericNonLinearElement<Method, Stationary, Multi> NonLinearElement;

  private:
    std::size_t numLevels_;
    std::vector<RealSparseMatrix> levelLinearCoefficients_;
    std::vector<std::vector<NonLinearElement>> levelNonLinearities_;
    std::vector<SystemCondition> levelConditions_;
    mutable Solution solutionCache_;

  public:
    /// Create cascade labeling system
    /// \param levelLinearCoefficients linear labeling interaction terms
    /// \param levelNonLinearities non-linear labeling interaction terms
    /// \param levelConditions initial labeling states
    /// \param solver numerical solver
    CascadeSystem(const std::vector<RealSparseMatrix> &levelLinearCoefficients,
                  std::vector<std::vector<NonLinearElement>> levelNonLinearities,
                  std::vector<SystemCondition> levelConditions, const Solver &solver)
        : Base(solver), numLevels_(levelLinearCoefficients.size()), levelLinearCoefficients_(levelLinearCoefficients),
          levelNonLinearities_(levelNonLinearities), levelConditions_(levelConditions) {}

    void solveLevelSystem(std::size_t levelIndex) const {
        X3CFLUX_CHECK(levelIndex < numLevels_);

        if (levelLinearCoefficients_[levelIndex].rows() == 0) {
            solutionCache_.emplace_back();
            return;
        }

        const auto &solver = this->getSolver();
        try {
            LevelSystem system(levelLinearCoefficients_[levelIndex], levelNonLinearities_[levelIndex],
                               levelConditions_[levelIndex], solutionCache_);
            auto levelSolution = solver.solve(system);

            solutionCache_.push_back(levelSolution);
        } catch (const MathError &error) {
            X3CFLUX_WARNING() << "The current labeling system is not "
                                 "numerically solvable, but a solvable "
                                 "system can be recovered. This happened "
                                 "because the current parameter "
                                 "configuration effectively disables one "
                                 "or more metabolic nodes by setting all "
                                 "fluxes through them to zero. If you don't"
                                 "want to see this error message, raise the"
                                 "log level using "
                                 "\"x3cflux.logging.level\". If this should"
                                 "not happen at all, make sure that your"
                                 "have non-zero constraints on all fluxes"
                                 "of branching pathways.";

            auto diag = levelLinearCoefficients_[levelIndex].diagonal();
            std::vector<Index> nonZeroIndices, zeroIndices;
            for (Index i = 0; i < diag.size(); ++i) {
                if (std::fabs(diag[i]) > 100.0 * std::numeric_limits<Real>::epsilon()) {
                    nonZeroIndices.push_back(i);
                } else {
                    zeroIndices.push_back(i);
                }
            }

            auto [reducedLinCoeffs, reducedNonLinElems, reducedCondition] =
                reduceSystem<false>(levelLinearCoefficients_[levelIndex], levelNonLinearities_[levelIndex],
                                    levelConditions_[levelIndex], nonZeroIndices);
            LevelSystem system(reducedLinCoeffs, reducedNonLinElems, reducedCondition, solutionCache_);
            auto reducedSolution = solver.solve(system);

            solutionCache_.push_back(expandSystem(reducedSolution, zeroIndices));
        }
    }

    LevelSystem getLevelSystem(std::size_t level) const {
        for (std::size_t levelIndex = solutionCache_.size(); levelIndex < level; ++levelIndex) {
            solveLevelSystem(levelIndex);
        }

        return LevelSystem(levelLinearCoefficients_[level], levelNonLinearities_[level], levelConditions_[level],
                           solutionCache_);
    }

    /// Solve this cascade system
    /// \return solution of cascade system
    Solution solve() const override {
        solutionCache_.clear();
        for (std::size_t levelIndex = 0; levelIndex < numLevels_; ++levelIndex) {
            solveLevelSystem(levelIndex);
        }

        return solutionCache_;
    }
};

/// \brief Derivative of cascade labeling system
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeDerivativeSystem : public LabelingSystem<Method, Stationary, Multi> {
  public:
    typedef LabelingSystem<Method, Stationary, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    typedef CascadeLevelDerivativeSystem<Method, Stationary, Multi> LevelSystem;
    typedef typename LevelSystem::SystemCondition SystemCondition;

    typedef NumericNonLinearElementDerivative<Method, Stationary, Multi> NonLinearElement;

  private:
    std::size_t numLevels_;
    std::vector<RealSparseMatrix> levelLinearCoefficients_;
    std::vector<RealSparseMatrix> levelLinearDerivativeCoefficients_;
    std::vector<std::vector<NonLinearElement>> levelNonLinearities_;
    std::vector<SystemCondition> levelConditions_;
    const Solution &nonDerivSolution_;
    mutable Solution solutionCache_;

  public:
    /// Create derivative of cascade labeling system
    /// \param levelLinearCoefficients linear labeling interaction terms
    /// \param levelLinearDerivativeCoefficients partial derivative of linear interaction terms
    /// \param levelNonLinearities non-linear labeling interaction terms
    /// \param levelConditions initial labeling states
    /// \param nonDerivSolution solution of base system
    /// \param solver numerical solver
    CascadeDerivativeSystem(const std::vector<RealSparseMatrix> &levelLinearCoefficients,
                            std::vector<RealSparseMatrix> levelLinearDerivativeCoefficients,
                            std::vector<std::vector<NonLinearElement>> levelNonLinearities,
                            std::vector<SystemCondition> levelConditions, const Solution &nonDerivSolution,
                            const Solver &solver)
        : Base(solver), numLevels_(levelLinearCoefficients.size()), levelLinearCoefficients_(levelLinearCoefficients),
          levelLinearDerivativeCoefficients_(std::move(levelLinearDerivativeCoefficients)),
          levelNonLinearities_(levelNonLinearities), levelConditions_(levelConditions),
          nonDerivSolution_(nonDerivSolution) {}

    void solveLevelSystem(std::size_t levelIndex) const {
        X3CFLUX_CHECK(levelIndex < numLevels_);

        if (levelLinearCoefficients_[levelIndex].rows() == 0) {
            solutionCache_.emplace_back();
            return;
        }

        const auto &solver = this->getSolver();
        try {
            LevelSystem system(levelLinearCoefficients_[levelIndex], levelLinearDerivativeCoefficients_[levelIndex],
                               levelNonLinearities_[levelIndex], levelConditions_[levelIndex], nonDerivSolution_,
                               solutionCache_);
            auto levelSolution = solver.solve(system);

            solutionCache_.push_back(levelSolution);
        } catch (const MathError &error) {
            X3CFLUX_WARNING() << "The current labeling system is not "
                                 "numerically solvable, but a solvable "
                                 "system can be recovered. This happened "
                                 "because the current parameter "
                                 "configuration effectively disables one "
                                 "or more metabolic nodes by setting all "
                                 "fluxes through them to zero. If you don't"
                                 "want to see this error message, raise the"
                                 "log level using "
                                 "\"x3cflux.logging.level\". If this should"
                                 "not happen at all, make sure that your"
                                 "have non-zero constraints on all fluxes"
                                 "of branching pathways.";

            auto diag = levelLinearCoefficients_[levelIndex].diagonal();
            std::vector<Index> nonZeroIndices, zeroIndices;
            for (Index i = 0; i < diag.size(); ++i) {
                if (std::fabs(diag[i]) > 100.0 * std::numeric_limits<Real>::epsilon()) {
                    nonZeroIndices.push_back(i);
                } else {
                    zeroIndices.push_back(i);
                }
            }

            auto [reducedLinCoeffs, reducedNonLinElems, reducedCondition] =
                reduceSystem<true>(levelLinearCoefficients_[levelIndex], levelNonLinearities_[levelIndex],
                                   levelConditions_[levelIndex], nonZeroIndices);
            LevelSystem system(reducedLinCoeffs, levelLinearDerivativeCoefficients_[levelIndex], reducedNonLinElems,
                               reducedCondition, nonDerivSolution_, solutionCache_);
            auto reducedSolution = solver.solve(system);

            solutionCache_.push_back(expandSystem(reducedSolution, zeroIndices));
        }
    }

    LevelSystem getLevelSystem(std::size_t level) const {
        for (std::size_t levelIndex = solutionCache_.size(); levelIndex < level; ++levelIndex) {
            solveLevelSystem(levelIndex);
        }

        return LevelSystem(levelLinearCoefficients_[level], levelLinearDerivativeCoefficients_[level],
                           levelNonLinearities_[level], levelConditions_[level], nonDerivSolution_, solutionCache_);
    }

    /// Solve this cascade system
    /// \return solution of cascade system derivative
    Solution solve() const override {
        solutionCache_.clear();
        for (std::size_t levelIndex = 0; levelIndex < numLevels_; ++levelIndex) {
            solveLevelSystem(levelIndex);
        }

        return solutionCache_;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_CASCADESYSTEM_H
