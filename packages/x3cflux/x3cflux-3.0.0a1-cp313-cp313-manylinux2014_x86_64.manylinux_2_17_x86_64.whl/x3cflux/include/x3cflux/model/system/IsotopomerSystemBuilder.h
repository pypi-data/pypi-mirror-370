#ifndef X3CFLUX_ISOTOPOMERSYSTEMBUILDER_H
#define X3CFLUX_ISOTOPOMERSYSTEMBUILDER_H

#include "IsotopomerSystem.h"
#include "MultiHelper.h"
#include "NaturalLabelingInitializer.h"
#include "SymbolicElementsBuilder.h"
#include "SystemBuilder.h"
#include "SystemError.h"
#include <boost/functional/hash.hpp>
#include <model/network/LabelingNetwork.h>

#include <utility>

namespace x3cflux {

template <bool Multi> class SymbolicNonLinearityBuilder<LabelingNetwork<IsotopomerMethod>, false, Multi> {
  public:
    typedef typename LabelingNetwork<IsotopomerMethod>::ModelingMethod Method;
    typedef typename LabelingNetwork<IsotopomerMethod>::Ordering Ordering;
    typedef StateVariableImpl<typename Method::StateType> StateVariable;
    typedef typename StateVariable::StateType State;

    typedef NonLinearity<Method, false, false> SingleNonLinearFunction;
    typedef NonLinearity<Method, false, true> MultiNonLinearFunction;
    typedef Condensation<IsotopomerMethod, false, Multi> IsotopomerCondensation;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    const Ordering &ordering_;

  public:
    explicit SymbolicNonLinearityBuilder(const Ordering &ordering) : ordering_(ordering) {}

    std::shared_ptr<IsotopomerCondensation> buildCondensation(const std::vector<StateVariable> &educts) const {
        std::vector<Index> isotopomerIndices;
        for (const auto &educt : educts) {
            isotopomerIndices.push_back(ordering_.getSystemIndex(educt));
        }
        return std::make_shared<IsotopomerCondensation>(isotopomerIndices);
    }

    std::shared_ptr<SingleNonLinearFunction>
    buildSubstrateIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const std::string &name,
                         const State &state) const {
        auto substrate = findSubstrate(substrates, name);

        // Build intake element if substrate is found
        if (substrate) {
            if (isInstanceOf<ConstantSubstrate>(substrate)) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
                const auto &labelInputs = constSubstr->getProfiles();
                auto labelInIt = labelInputs.find(state);

                if (labelInIt != labelInputs.end()) {
                    return std::make_shared<ConstantSubstrateInput<IsotopomerMethod, false, false>>(labelInIt->second);
                }
            } else if (isInstanceOf<VariateSubstrate>(substrate)) {
                auto constSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
                const auto &labelInputs = constSubstr->getProfiles();
                auto labelInIt = labelInputs.find(state);

                if (labelInIt != labelInputs.end()) {
                    return std::make_shared<VariateSubstrateInput<IsotopomerMethod, false>>(labelInIt->second);
                }
            } else {
                X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
            }
        }

        return nullptr;
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
        if (not checkSubstrateTypesEqual(foundSubstrates)) {
            X3CFLUX_THROW(SystemError, "Multi substrate intake type varies between "
                                       "experiments");
        }

        if (isInstanceOf<ConstantSubstrate>(foundSubstrates.front())) {
            auto numMulti = static_cast<Index>(foundSubstrates.size());
            RealVector multiIntake = RealVector::Zero(numMulti);
            for (Index substrIndex = 0; substrIndex < numMulti; ++substrIndex) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(foundSubstrates[substrIndex]);
                const auto &labelInputs = constSubstr->getProfiles();
                auto labelInIt = labelInputs.find(state);

                if (labelInIt != labelInputs.end()) {
                    multiIntake[substrIndex] = labelInIt->second;
                }
            }

            if (not multiIntake.isZero()) {
                return std::make_shared<ConstantSubstrateInput<IsotopomerMethod, false, true>>(multiIntake);
            } else {
                return nullptr;
            }
        } else if (isInstanceOf<VariateSubstrate>(foundSubstrates.front())) {
            std::vector<std::vector<std::tuple<Real, Real, flux::symb::ExprTree>>> multiIntake;
            for (const auto &substrate : foundSubstrates) {
                auto constSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
                const auto &labelInputs = constSubstr->getProfiles();
                auto labelInIt = labelInputs.find(state);

                if (labelInIt != labelInputs.end()) {
                    multiIntake.push_back(labelInIt->second);
                } else {
                    std::vector<std::tuple<Real, Real, flux::symb::ExprTree>> zeroIntake;
                    zeroIntake.emplace_back(0., std::numeric_limits<Real>::max(), *flux::symb::ExprTree::val(0.));
                    multiIntake.push_back(zeroIntake);
                }
            }

            return std::make_shared<VariateSubstrateInput<IsotopomerMethod, true>>(multiIntake);
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
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

    static bool checkSubstrateTypesEqual(const std::vector<std::shared_ptr<Substrate>> &substrates) {
        auto isConstant = [&](const std::shared_ptr<Substrate> &substrate) -> bool {
            return isInstanceOf<ConstantSubstrate>(substrate);
        };

        auto isVariate = [&](const std::shared_ptr<Substrate> &substrate) -> bool {
            return isInstanceOf<VariateSubstrate>(substrate);
        };

        bool constant = std::all_of(substrates.begin(), substrates.end(), isConstant);

        bool variate = std::all_of(substrates.begin(), substrates.end(), isVariate);

        return constant or variate;
    }
};

template <bool Multi = false> class IsotopomerSystemBuilder : public SystemBuilder<IsotopomerMethod, false, Multi> {
  public:
    typedef SystemBuilder<IsotopomerMethod, false, Multi> Base;
    typedef typename Base::System System;
    typedef typename Base::Solution Solution;

    typedef typename System::Fraction Fraction;
    typedef typename System::SystemState SystemState;

    typedef IsotopomerSystem<Multi> ProductSystem;
    typedef LabelingNetwork<IsotopomerMethod> IsotopomerNetwork;
    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;
    typedef NaturalLabelingInitializer<IsotopomerMethod> NaturalLabeling;
    typedef StateVariableOperations<IsotopomerMethod, Multi> StateVarOps;

    typedef SymbolicElementsBuilder<IsotopomerNetwork, false, Multi> SymbElementsBuilder;
    typedef typename SymbElementsBuilder::SymbLinearElement SymbLinearElement;
    typedef typename SymbElementsBuilder::SymbNonLinearElement SymbNonLinearElement;
    typedef SymbolicNonLinearityBuilder<LabelingNetwork<IsotopomerMethod>, false, Multi> SymbNonLinearityBuilder;
    typedef NumericNonLinearElement<IsotopomerMethod, false, Multi> NonLinearElement;

  private:
    std::size_t size_;
    std::vector<SymbLinearElement> symbolicLinearities_;
    std::vector<SymbNonLinearElement> symbolicNonLinearities_;
    SystemState initialValue_;
    Real endTime_;

  public:
    IsotopomerSystemBuilder(const IsotopomerNetwork &network,
                            const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates, Real endTime)
        : Base(static_cast<Index>(network.getNumReactions()),
               static_cast<Index>(network.getNumPools() - network.getNumSubstrates())),
          endTime_(endTime) {
        IsotopomerNetwork::Ordering ordering(network);
        size_ = ordering.getNumStateVariables();

        // Compute isotopomer initial labeling
        auto initialState = NaturalLabeling::computeInitialState(network, ordering);
        initialValue_ = StateVarOps::blockwiseIfMulti(initialState, substrates.size());

        // Build isotopomer balance equation systems
        SymbNonLinearityBuilder symbNonLinBuilder(ordering);
        SymbElementsBuilder symbElementsBuilder(network, ordering, substrates, symbNonLinBuilder);
        for (const auto &reaction : network) {
            const auto &educts = reaction.getEducts();
            const auto &products = reaction.getProducts();

            for (const auto &product : products) {
                symbElementsBuilder.addReaction(reaction.getReactionIndex(), reaction.isForward(), product, educts);
            }
        }
        symbolicLinearities_ = symbElementsBuilder.getSymbolicLinearities();
        symbolicNonLinearities_ = symbElementsBuilder.getSymbolicNonLinearities();
    }

    std::unique_ptr<System> build(const RealVector &parameters) const override {
        auto accessor = this->getParameterAccessor(parameters);

        std::vector<RealTriplet> triplets;
        triplets.reserve(symbolicLinearities_.size());
        for (const auto &symbTriplet : symbolicLinearities_) {
            triplets.push_back(symbTriplet.evaluate(accessor));
        }

        RealSparseMatrix linearities(size_, size_);
        linearities.setFromTriplets(triplets.begin(), triplets.end());

        std::vector<NonLinearElement> nonLinearities;
        for (const auto &nonLin : symbolicNonLinearities_) {
            nonLinearities.push_back(nonLin.evaluate(accessor));
        }

        return std::make_unique<ProductSystem>(linearities, nonLinearities, initialValue_, endTime_, this->getSolver());
    }

    std::unique_ptr<System> buildDerivative(const RealVector &parameters, const RealVector &parameterDerivatives,
                                            const Solution &baseSolution) const override {
        std::ignore = parameters;
        std::ignore = parameterDerivatives;
        std::ignore = baseSolution;
        X3CFLUX_ERROR() << "Isotopomer derivative systems are not yet supported";
        return nullptr;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERSYSTEMBUILDER_H
