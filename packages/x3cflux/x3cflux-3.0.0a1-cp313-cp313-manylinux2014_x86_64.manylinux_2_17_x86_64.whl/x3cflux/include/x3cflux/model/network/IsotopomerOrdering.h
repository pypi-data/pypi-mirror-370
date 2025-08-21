#ifndef X3CFLUX_ISOTOPOMERORDERING_H
#define X3CFLUX_ISOTOPOMERORDERING_H

#include "IsotopomerIterator.h"
#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Sequential ordering of isotopomer state variables
///
/// The ordering maps isotopomer state variables from a network
/// to a range of positive integers and vice versa. The range of
/// integers can used to map fractions of the isotopomers to a
/// vector and with that formulate labeling systems.
class IsotopomerOrdering {
  public:
    typedef typename IsotopomerIterator::Isotopomer StateVariable;

  private:
    Index numStateVariables_;
    std::vector<Index> offset_;
    std::vector<std::size_t> numAtoms_;

  public:
    /// Create sequential ordering of the networks isotopomers.
    /// \param network network information
    explicit IsotopomerOrdering(const MetaboliteNetwork &network);

    /// \return total number of isotopomers
    Index getNumStateVariables() const { return numStateVariables_; }

    /// \param stateVar isotopomer state variable
    /// \return calculated index of the isotopomer
    Index getSystemIndex(const StateVariable &stateVar) const;

    /// \param systemIndex index of the labeling system
    /// \return calculated isotopomer
    StateVariable getStateVariable(Index systemIndex) const;
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERORDERING_H
