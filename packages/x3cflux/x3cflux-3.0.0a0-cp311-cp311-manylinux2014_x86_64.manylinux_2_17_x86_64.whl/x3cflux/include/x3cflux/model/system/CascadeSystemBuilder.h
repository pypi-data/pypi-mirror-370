#ifndef X3CFLUX_CASCADESYSTEMBUILDER_H
#define X3CFLUX_CASCADESYSTEMBUILDER_H

#include "CascadeSystem.h"
#include "NaturalLabelingInitializer.h"
#include "SymbolicElementsBuilder.h"
#include "SymbolicLinearElement.h"
#include "SystemBuilder.h"
#include "SystemError.h"

#include <model/network/LabelingNetwork.h>

namespace x3cflux {

template <typename Method, bool Stationary> struct SymbolicSubstrateIntakeBuilder;

template <typename Method> struct SymbolicSubstrateIntakeBuilder<Method, true> {
  public:
    typedef StateVariableImpl<typename Method::StateType> StateVariable;
    typedef typename StateVariable::StateType State;

    typedef NonLinearity<Method, true, false> SingleNonLinearFunction;
    typedef NonLinearity<Method, true, true> MultiNonLinearFunction;

    static std::shared_ptr<SingleNonLinearFunction> buildSingleIntake(const std::shared_ptr<Substrate> &substrate,
                                                                      const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrate)) {
            auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
            return std::make_shared<ConstantSubstrateInput<Method, true, false>>(constSubstr, state);
        } else if (isInstanceOf<VariateSubstrate>(substrate)) {
            X3CFLUX_THROW(SystemError, "Variate substrate type cannot be used in "
                                       "stationary simulation");
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }

    static std::shared_ptr<MultiNonLinearFunction>
    buildMultiIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<ConstantSubstrate>> constSubstrates;
            for (const auto &substrate : substrates) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
                constSubstrates.push_back(constSubstr);
            }

            return std::make_shared<ConstantSubstrateInput<Method, true, true>>(constSubstrates, state);
        } else if (isInstanceOf<VariateSubstrate>(substrates.front())) {
            X3CFLUX_THROW(SystemError, "Variate substrate type cannot be used in "
                                       "stationary simulation");
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }
};

template <typename Method> struct SymbolicSubstrateIntakeBuilder<Method, false> {
  public:
    typedef StateVariableImpl<typename Method::StateType> StateVariable;
    typedef typename StateVariable::StateType State;

    typedef NonLinearity<Method, false, false> SingleNonLinearFunction;
    typedef NonLinearity<Method, false, true> MultiNonLinearFunction;

    static std::shared_ptr<SingleNonLinearFunction> buildSingleIntake(const std::shared_ptr<Substrate> &substrate,
                                                                      const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrate)) {
            auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
            return std::make_shared<ConstantSubstrateInput<Method, false, false>>(constSubstr, state);
        } else if (isInstanceOf<VariateSubstrate>(substrate)) {
            auto varSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
            return std::make_shared<VariateSubstrateInput<Method, false>>(varSubstr, state);
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }

    static std::shared_ptr<MultiNonLinearFunction>
    buildMultiIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<ConstantSubstrate>> constSubstrates;
            for (const auto &substrate : substrates) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
                constSubstrates.push_back(constSubstr);
            }

            return std::make_shared<ConstantSubstrateInput<Method, false, true>>(constSubstrates, state);
        } else if (isInstanceOf<VariateSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<VariateSubstrate>> varSubstrates;
            for (const auto &substrate : substrates) {
                auto varSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
                varSubstrates.push_back(varSubstr);
            }

            return std::make_shared<VariateSubstrateInput<Method, true>>(varSubstrates, state);
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }
};

template <typename Network, bool Stationary, bool Multi> class SymbolicNonLinearityBuilder {
  public:
    typedef typename Network::ModelingMethod Method;
    typedef typename Network::Ordering Ordering;
    typedef StateVariableImpl<typename Method::StateType> StateVariable;
    typedef typename StateVariable::StateType State;

    typedef SymbolicSubstrateIntakeBuilder<Method, Stationary> SymbSubstrateIntakeBuilder;
    typedef typename SymbSubstrateIntakeBuilder::SingleNonLinearFunction SingleNonLinearFunction;
    typedef typename SymbSubstrateIntakeBuilder::MultiNonLinearFunction MultiNonLinearFunction;
    typedef Condensation<Method, Stationary, Multi> CascadeCondensation;

  private:
    const std::vector<Ordering> &orderings_;

  public:
    explicit SymbolicNonLinearityBuilder(const std::vector<Ordering> &orderings) : orderings_(orderings) {}

    std::shared_ptr<CascadeCondensation> buildCondensation(const std::vector<StateVariable> &educts) const {
        std::vector<std::size_t> levelIndices, systemIndices;
        for (const auto &educt : educts) {
            std::size_t level = educt.getState().count() - 1;
            levelIndices.push_back(level);
            systemIndices.push_back(orderings_[level].getSystemIndex(educt));
        }
        return std::make_shared<CascadeCondensation>(levelIndices, systemIndices);
    }

    std::shared_ptr<SingleNonLinearFunction>
    buildSubstrateIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const std::string &name,
                         const State &state) const {
        auto substrate = findSubstrate(substrates, name);

        // Continue if substrate does not exist
        if (not substrate) {
            return nullptr;
        }

        return SymbSubstrateIntakeBuilder::buildSingleIntake(substrate, state);
    }

    std::shared_ptr<MultiNonLinearFunction>
    buildSubstrateIntake(const std::vector<std::vector<std::shared_ptr<Substrate>>> &parSubstrates,
                         const std::string &name, const State &state) const {
        std::vector<std::shared_ptr<Substrate>> foundSubstrates;
        for (const auto &substrates : parSubstrates) {
            if (auto substrate = findSubstrate(substrates, name)) {
                foundSubstrates.push_back(substrate);
            }
        }

        // Leave out substrates that were not fed in the experiment
        if (foundSubstrates.empty()) {
            return nullptr;
        }

        // Some experiments left out the substrate - this is not supported yet
        if (foundSubstrates.size() != parSubstrates.size()) {
            X3CFLUX_THROW(SystemError, "Multi substrate intake missing");
        }

        // Substrates with different type is not supported
        checkSubstrateTypesEqual(foundSubstrates);

        return SymbSubstrateIntakeBuilder::buildMultiIntake(foundSubstrates, state);
    }

  private:
    std::shared_ptr<Substrate> findSubstrate(const std::vector<std::shared_ptr<Substrate>> &substrates,
                                             const std::string &name) const {
        auto substrIt = std::find_if(substrates.begin(), substrates.end(),
                                     [&](const std::shared_ptr<Substrate> &substrate) -> bool {
                                         return substrate->getMetaboliteName() == name;
                                     });

        if (substrIt != substrates.end()) {
            return *substrIt;
        }

        return nullptr;
    }

    static void checkSubstrateTypesEqual(const std::vector<std::shared_ptr<Substrate>> &substrates) {
        auto isConstant = [&](const std::shared_ptr<Substrate> &substrate) -> bool {
            return isInstanceOf<ConstantSubstrate>(substrate);
        };

        // Multi intake must have the same type - constant or time variate
        if (std::all_of(substrates.begin(), substrates.end(), isConstant) or
            std::none_of(substrates.begin(), substrates.end(), isConstant)) {
            return;
        }

        X3CFLUX_THROW(SystemError, "Multi substrate intake type varies between experiments");
    }
};

template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeSystemBuilder : public SystemBuilder<Method, Stationary, Multi> {
  public:
    typedef SystemBuilder<Method, Stationary, Multi> Base;
    typedef typename Base::System System;
    typedef typename Base::Solution Solution;
    typedef typename System::Fraction Fraction;
    typedef typename System::SystemState SystemState;

    typedef LabelingNetwork<Method> CascadeNetwork;
    typedef ReducedLabelingNetwork<Method> ReducedCascadeNetwork;
    typedef CascadeSystem<Method, Stationary, Multi> ProductSystem;
    typedef typename ProductSystem::SystemCondition SystemCondition;
    typedef CascadeDerivativeSystem<Method, Stationary, Multi> ProductDerivativeSystem;
    typedef NaturalLabelingInitializer<Method> NaturalLabeling;
    typedef StateVariableOperations<Method, Multi> StateVarOps;
    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

    typedef SymbolicLinearElement<Stationary> SymbLinearElement;
    typedef SymbolicNonLinearElement<Method, Stationary, Multi> SymbNonLinearElement;
    typedef NumericNonLinearElement<Method, Stationary, Multi> NonLinearElement;
    typedef NumericNonLinearElementDerivative<Method, Stationary, Multi> NonLinearElementDerivative;

  private:
    std::vector<std::size_t> levelSizes_;
    std::vector<std::vector<SymbLinearElement>> levelSymbolicLinearElements_;
    std::vector<std::vector<SymbNonLinearElement>> levelSymbolicNonLinearities_;
    std::vector<SystemCondition> levelInitialValues_;
    std::vector<SystemCondition> levelInitialValueDerivatives_;
    Real endTime_;

  public:
    template <typename Network, std::enable_if_t<std::is_same<Network, CascadeNetwork>::value or
                                                     std::is_same<Network, ReducedCascadeNetwork>::value,
                                                 bool> = true>
    CascadeSystemBuilder(const Network &network, const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates,
                         Real endTime = std::numeric_limits<Real>::infinity())
        : Base(static_cast<Index>(network.getNumReactions()),
               static_cast<Index>(network.getNumPools() - network.getNumSubstrates())),
          endTime_(endTime) {
        typedef typename Network::Ordering Ordering;
        typedef SymbolicElementsBuilder<Network, Stationary, Multi> SymbElementsBuilder;
        typedef SymbolicNonLinearityBuilder<Network, Stationary, Multi> SymbNonLinBuilder;

        std::vector<Ordering> orderings;
        for (const auto &level : network) {
            std::size_t levelIndex = level.getIndex();
            orderings.emplace_back(network, levelIndex);
            const auto &ordering = orderings.back();
            levelSizes_.push_back(ordering.getNumStateVariables());

            // Build system conditions (dynamic system initial state and
            // end time)
            auto initialState = NaturalLabeling::computeInitialState(network, ordering);
            auto initialValue = StateVarOps::blockwiseIfMulti(initialState, substrates.size());
            if constexpr (Stationary) {
                levelInitialValues_.emplace_back(initialValue);
                levelInitialValueDerivatives_.emplace_back(SystemState::Zero(initialValue.rows(), initialValue.cols()));
            } else {
                levelInitialValues_.emplace_back(endTime_, initialValue);
                levelInitialValueDerivatives_.emplace_back(endTime_,
                                                           SystemState::Zero(initialValue.rows(), initialValue.cols()));
            }

            // Build balance equation system
            SymbNonLinBuilder symbNonLinBuilder(orderings);
            SymbElementsBuilder symbElementsBuilder(network, ordering, substrates, symbNonLinBuilder);
            for (const auto &reaction : level) {
                symbElementsBuilder.addReaction(reaction.getReactionIndex(), reaction.isForward(),
                                                reaction.getProduct(), reaction.getEducts());
            }
            levelSymbolicLinearElements_.push_back(symbElementsBuilder.getSymbolicLinearities());
            levelSymbolicNonLinearities_.push_back(symbElementsBuilder.getSymbolicNonLinearities());
        }
    }

    Real getEndTime() const { return endTime_; }

    std::unique_ptr<System> build(const RealVector &parameters) const override {
        auto accessor = this->getParameterAccessor(parameters);

        std::vector<RealSparseMatrix> levelLinearCoefficients;
        for (std::size_t levelIndex = 0; levelIndex < levelSizes_.size(); ++levelIndex) {
            std::vector<RealTriplet> triplets;
            triplets.reserve(levelSymbolicLinearElements_[levelIndex].size());
            for (const auto &symbTriplet : levelSymbolicLinearElements_[levelIndex]) {
                triplets.push_back(symbTriplet.evaluate(accessor));
            }

            RealSparseMatrix linCoeffs(levelSizes_[levelIndex], levelSizes_[levelIndex]);
            linCoeffs.setFromTriplets(triplets.begin(), triplets.end());
            levelLinearCoefficients.push_back(linCoeffs);
        }

        std::vector<std::vector<NonLinearElement>> levelNonLinearities;
        for (const auto &levelNonLins : levelSymbolicNonLinearities_) {
            std::vector<NonLinearElement> nonLinearities;
            for (const auto &nonLin : levelNonLins) {
                nonLinearities.push_back(nonLin.evaluate(accessor));
            }
            levelNonLinearities.push_back(nonLinearities);
        }

        return std::make_unique<ProductSystem>(levelLinearCoefficients, levelNonLinearities, levelInitialValues_,
                                               this->getSolver());
    }

    std::unique_ptr<System> buildDerivative(const RealVector &parameters, const RealVector &parameterDerivatives,
                                            const Solution &baseSystemSolution) const override {
        auto accessor = this->getDerivativeParameterAccessor(parameters, parameterDerivatives);

        std::vector<RealSparseMatrix> levelLinearCoefficients, levelLinearCoefficientDerivatives;
        for (std::size_t levelIndex = 0; levelIndex < levelSizes_.size(); ++levelIndex) {
            std::vector<RealTriplet> triplets, tripletDerivatives;
            triplets.reserve(levelSymbolicLinearElements_[levelIndex].size());
            for (const auto &symbTriplet : levelSymbolicLinearElements_[levelIndex]) {
                triplets.push_back(symbTriplet.evaluate(accessor));
                tripletDerivatives.push_back(symbTriplet.evaluateDerivative(accessor));
            }

            RealSparseMatrix linCoeffs(levelSizes_[levelIndex], levelSizes_[levelIndex]);
            linCoeffs.setFromTriplets(triplets.begin(), triplets.end());
            levelLinearCoefficients.push_back(linCoeffs);

            RealSparseMatrix linCoeffDerivs(levelSizes_[levelIndex], levelSizes_[levelIndex]);
            linCoeffDerivs.setFromTriplets(tripletDerivatives.begin(), tripletDerivatives.end());
            levelLinearCoefficientDerivatives.push_back(linCoeffDerivs);
        }

        std::vector<std::vector<NonLinearElementDerivative>> levelNonLinearities;
        for (const auto &levelNonLins : levelSymbolicNonLinearities_) {
            std::vector<NonLinearElementDerivative> nonLinearities;
            for (const auto &nonLin : levelNonLins) {
                nonLinearities.push_back(nonLin.evaluateDerivative(accessor));
            }
            levelNonLinearities.push_back(nonLinearities);
        }

        return std::make_unique<ProductDerivativeSystem>(levelLinearCoefficients, levelLinearCoefficientDerivatives,
                                                         levelNonLinearities, levelInitialValueDerivatives_,
                                                         std::cref(baseSystemSolution), this->getDerivativeSolver());
    }
};

} // namespace x3cflux

#endif // X3CFLUX_CASCADESYSTEMBUILDER_H
