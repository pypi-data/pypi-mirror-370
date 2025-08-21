#ifndef X3CFLUX_CASCADEORDERING_H
#define X3CFLUX_CASCADEORDERING_H

#include "MetaboliteNetwork.h"
#include "StateTransporter.h"
#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Sequential ordering of cascade levels state variables
///
/// The ordering maps state variables on one level of a cascaded
/// labeling network to a range of positive integers and vice versa.
/// The range of integers can used to map fractions of the state variables
/// to a vector and with that formulate labeling systems.
class CascadeOrdering {
  public:
    typedef typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType StateVariable;

  private:
    std::size_t level_;
    Index numStateVariables_;
    std::vector<Index> offset_;
    std::vector<std::size_t> numAtoms_;

  public:
    /// Create sequential ordering of the networks levels state variables.
    /// \param network network information
    /// \param level network level index
    CascadeOrdering(const MetaboliteNetwork &network, std::size_t level);

    /// \return network level index
    std::size_t getLevel() const { return level_; }

    /// \return total number of state variables
    std::size_t getNumStateVariables() const { return numStateVariables_; }

    /// \param stateVar state variable
    /// \return calculated index of the state variable
    Index getSystemIndex(const StateVariable &stateVar) const;

    /// \param systemIndex index of the labeling system
    /// \return calculated state variable
    StateVariable getStateVariable(Index systemIndex) const;
};

} // namespace x3cflux

#endif // X3CFLUX_CASCADEORDERING_H
