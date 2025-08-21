#ifndef X3CFLUX_STATETRANSPORTER_H
#define X3CFLUX_STATETRANSPORTER_H

#include "MetaboliteNetwork.h"

#include <utility>
#include <vector>

namespace x3cflux {

/// \brief Metabolite state variable
/// \tparam State metabolite state
///
/// A metabolite state variable that is supposed to be used for
/// transportation calculation.
template <typename State> class StateVariableImpl {
  public:
    typedef State StateType;

  private:
    std::size_t poolIndex_;
    State state_;

  public:
    /// Create metabolite state variable.
    /// \param poolIndex metabolite pool index
    /// \param state metabolite state
    StateVariableImpl(std::size_t poolIndex, State state) : poolIndex_(poolIndex), state_(std::move(state)) {}

    /// \return metabolite pool index
    std::size_t getPoolIndex() const { return poolIndex_; }

    /// \return metabolite state
    State getState() const { return state_; }
};

/// \brief Reaction of metabolite state variables
/// \tparam State metabolite state
///
/// A reaction of state variables that is supposed to be used
/// for transportation calculation. Therefore, there is only one
/// product whose state is then transported back to the educts.
template <typename State> class StateVariableReactionImpl {
  public:
    typedef StateVariableImpl<State> StateVariableType;

  private:
    std::size_t reactionIndex_;
    bool forward_;
    StateVariableType product_;
    std::vector<StateVariableType> educts_;

  public:
    /// Create reaction of state variables.
    /// \param reactionIndex metabolic reaction index
    /// \param forward indicates if reaction is forward or backward
    /// \param product single state variable product
    /// \param educts state variable educts
    StateVariableReactionImpl(std::size_t reactionIndex, bool forward, const StateVariableType &product,
                              const std::vector<StateVariableType> &educts)
        : reactionIndex_(reactionIndex), forward_(forward), product_(product), educts_(educts) {}

    /// \return metabolic reaction index
    std::size_t getReactionIndex() const { return reactionIndex_; }

    /// \return indicates if reaction is forward or backward
    bool isForward() const { return forward_; }

    /// \return single state variable product
    const StateVariableType &getProduct() const { return product_; }

    /// \return state variable educts
    const std::vector<StateVariableType> &getEducts() const { return educts_; }
};

/// \brief Basic typedefs for a metabolite state variable
/// \tparam T metabolite state
template <typename T> struct StateTransporterTraits {
    typedef T StateType;
    typedef StateVariableImpl<StateType> StateVariableType;
    typedef StateVariableReactionImpl<StateType> ReactionType;
};

/// \brief Default transporter (cannot be used)
/// \tparam T metabolite state
///
/// The transporter should be implemented for sensible
/// choices of states the correspond to existing state
/// variables. They have to implement the static function
/// "transport".
template <typename T> struct StateTransporter;

/// \brief State transporter check (default false)
/// \tparam T metabolite state
///
/// Check should be implemented for types that have a
/// sensible transporter implementation.
template <typename T> struct HasStateTransporter : public std::false_type {};

/// \brief State transporter implementation for binary number state
///
/// The implementation works for state variables with binary numbers as state
/// (e.g. Cumomer, EMU). It uses atom permutations of the given reactions
/// to permute the labeling of the product and omits all 0-labeled educts.
template <> struct StateTransporter<boost::dynamic_bitset<>> {
    typedef typename StateTransporterTraits<boost::dynamic_bitset<>>::StateType State;
    typedef typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType StateVariable;

    /// Transport labeling state of given reactant to reaction educts.
    /// \param network network information
    /// \param reactionIndex index of the reaction
    /// \param backwards indicate direction of the reaction
    /// \param reactantIndex index of reactant
    /// \param state state of the metabolite pool
    /// \return educt state variables
    static std::vector<StateVariable> transport(const MetaboliteNetwork &network, std::size_t reactionIndex,
                                                bool backwards, std::size_t reactantIndex, const State &state) {
        const auto &reactionInfo = network.getReactionInformation(reactionIndex);
        const auto &hyperedge = network.getHyperedge(reactionIndex);

        const auto &eductIndices = backwards ? hyperedge.first : hyperedge.second;
        const auto &productIndices = backwards ? hyperedge.second : hyperedge.first;
        const auto &permutation =
            backwards ? reactionInfo.getAtomPermutation().getInverse() : reactionInfo.getAtomPermutation();

        // Check if labeling state size is equal to number of atoms
        std::size_t poolIndex = productIndices[reactantIndex];
        X3CFLUX_CHECK(state.size() == network.getPoolInformation(poolIndex).getNumAtoms());

        // Calculate number of atoms before the selected product
        std::size_t numAtomsBefore = 0;
        for (std::size_t i = 0; i < reactantIndex; ++i) {
            numAtomsBefore += network.getPoolInformation(productIndices[i]).getNumAtoms();
        }

        // Set labeling sequence of all products
        State productLabeling(permutation.getNumIndices());
        for (std::size_t i = 0; i < state.size(); ++i) {
            productLabeling.set(numAtomsBefore + i, state[i]);
        }

        // Permute to get educt labeling sequence
        State eductLabeling = permutation.permute(productLabeling);

        // Split labeling sequence for each product
        std::vector<StateVariable> stateVars;
        std::size_t currAtomPos = 0;
        for (const auto &eductIndex : eductIndices) {
            std::size_t numAtoms = network.getPoolInformation(eductIndex).getNumAtoms();

            // Get labeling of current product
            State reactantLabeling(numAtoms);
            for (std::size_t i = 0; i < numAtoms; ++i) {
                reactantLabeling[i] = eductLabeling[currAtomPos + i];
            }

            // Only add cascade reactant if labeling state is not 0..0
            if (reactantLabeling.any()) {
                stateVars.emplace_back(eductIndex, reactantLabeling);
            }

            currAtomPos += numAtoms;
        }

        return stateVars;
    }
};

/// \brief State transporter check for binary number state
template <> struct HasStateTransporter<boost::dynamic_bitset<>> : public std::true_type {};

} // namespace x3cflux

#endif // X3CFLUX_STATETRANSPORTER_H
