#ifndef X3CFLUX_REDUCTIONORDERING_H
#define X3CFLUX_REDUCTIONORDERING_H

#include "BacktrackReduction.h"
#include "StateTransporter.h"

namespace x3cflux {

/// \brief Default reduction ordering (cannot be used)
/// \tparam T modeling state type
///
/// For certain state variables labeling networks can be reduced based
/// on their state type. The ordering is supposed to sequentially order
/// the reduced set of state variables by mapping it to a range of
/// positive integers.
template <typename T> class ReductionOrdering {};

/// \brief Reduction ordering check (default false)
/// \tparam T modeling state type
///
/// Check should be implemented for types that have a
/// sensible reduction ordering implementation.
template <typename T> struct HasReductionOrdering : public std::false_type {};

/// \brief Base class for reduction orderings
/// \tparam T modeling state type
///
/// Supplies useful typedefs.
template <typename T> class ReductionOrderingBase {
  public:
    typedef StateTransporterTraits<T> TransporterTraits;
    typedef typename TransporterTraits::StateType State;
    typedef typename TransporterTraits::StateVariableType StateVariable;
    typedef typename TransporterTraits::ReactionType Reaction;
};

/// \brief Reduction ordering implementation for binary number state
///
/// The implementation works for state variables with binary numbers as state
/// (e.g. Cumomer, EMU). These states also allow decomposition of the labeling
/// network (see CascadeOrdering). The implementation establishes a sequential
/// ordering on the reduced state variables of the specified level.
template <> class ReductionOrdering<boost::dynamic_bitset<>> : public ReductionOrderingBase<boost::dynamic_bitset<>> {
  public:
    typedef ReductionOrderingBase<boost::dynamic_bitset<>> Base;
    using Base::Reaction;
    using Base::State;
    using Base::StateVariable;

  private:
    std::size_t level_;
    Index numStateVariables_;
    std::unordered_map<std::size_t, std::unordered_map<boost::dynamic_bitset<>, Index>> stateVariableIndices_;
    std::vector<boost::dynamic_bitset<>> indexToStateMap_;
    std::vector<std::size_t> poolOffsets_;

  public:
    /// Create sequential ordering of a reduced cascaded network level.
    /// \tparam Method modeling method
    /// \param reduction reduced network information
    /// \param level network level index
    template <typename Method, std::enable_if_t<std::is_same<State, typename Method::StateType>::value, bool> = true>
    ReductionOrdering(const BacktrackReduction<Method> reduction, const std::size_t level) : level_(level) {
        const auto &stateVariables = reduction.getStateVariables();

        Index totalOffset = 0;
        for (std::size_t poolIndex = 0; poolIndex < reduction.getNumPools(); ++poolIndex) {
            poolOffsets_.emplace_back(totalOffset);

            const auto &poolInfo = reduction.getPoolInformation(poolIndex);
            auto &stateIndices = stateVariableIndices_[poolIndex];
            std::size_t numAtoms = poolInfo.getNumAtoms();
            auto keyValueIt = stateVariables.find(poolIndex);

            // Calculate offset (omitting substrates, lower-level and
            // not-reached metabolites)
            if (not poolInfo.isSubstrate() and numAtoms >= level_ and keyValueIt != stateVariables.end()) {
                for (const auto &labeling : keyValueIt->second) {
                    if (labeling.count() == level_) {
                        stateIndices[labeling] = totalOffset++;
                        indexToStateMap_.push_back(labeling);
                    }
                }
            }
        }

        numStateVariables_ = totalOffset;
    }

    /// \return network level index
    std::size_t getLevel() const { return level_; }

    /// \return number of state variables
    Index getNumStateVariables() const { return numStateVariables_; }

    /// \param stateVar state variable
    /// \return calculated index of the state variable
    Index getSystemIndex(const StateVariable &stateVar) const;

    /// \param systemIndex index of the labeling system
    /// \return calculated state variable
    StateVariable getStateVariable(Index systemIndex) const;
};
} // namespace x3cflux

#endif // X3CFLUX_REDUCTIONORDERING_H
