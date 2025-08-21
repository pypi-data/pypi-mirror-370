#ifndef X3CFLUX_LABELINGNETWORK_H
#define X3CFLUX_LABELINGNETWORK_H

#include "BacktrackReduction.h"
#include "MetaboliteNetwork.h"
#include "ReductionIterator.h"
#include "ReductionOrdering.h"

namespace x3cflux {

/// \brief Network of metabolite labeling states and state reactions
/// \tparam Method labeling state modeling method
///
/// The simple LabelingNetwork is derived from MetaboliteNetwork
/// and directly operates on its data. It provides iterators to iterate
/// its labeling state-based reactions and orderings that sequentially
/// order the labeling states. These features must be implemented by the
/// method and accessible as typedefs.
template <typename Method> class LabelingNetwork : public MetaboliteNetwork {
  public:
    typedef Method ModelingMethod;
    typedef typename ModelingMethod::IteratorType Iterator;
    typedef typename ModelingMethod::OrderingType Ordering;

  public:
    /// Create labeling network.
    /// \param data raw raw metabolite and reaction data
    /// \param substrates raw substrate data
    explicit LabelingNetwork(const NetworkData &data, const std::vector<std::shared_ptr<Substrate>> substrates)
        : MetaboliteNetwork(data, substrates) {}

    /// \return begin network iterator
    Iterator begin() const { return Iterator(*this, true); }

    /// \return end network iterator
    Iterator end() const { return Iterator(*this, false); }
};

/// \brief Backtrack-reduced network of metabolite labeling states and state reactions
/// \tparam Method labeling state modeling method
///
/// The ReducedLabelingNetwork is derived from BacktrackReduction and directly operates
/// on its data. It provides iterators to iterate its labeling state-based reactions
/// and orderings that sequentially order the labeling states. These features are
/// implemented by the BacktrackReduction. However, the chosen labeling modeling method
/// must fulfill the criteria to be backtrack-reducible.
template <typename Method> class ReducedLabelingNetwork : public BacktrackReduction<Method> {
  public:
    typedef Method ModelingMethod;
    typedef BacktrackReduction<ModelingMethod> Reduction;
    typedef ReductionIterator<typename Reduction::State> Iterator;
    typedef ReductionOrdering<typename Reduction::State> Ordering;

  public:
    /// Create ReducedLabelingNetwork
    /// \param data raw metabolite and reaction data
    /// \param substrates raw substrate data
    /// \param measurements
    ReducedLabelingNetwork(const NetworkData &data, const std::vector<std::shared_ptr<Substrate>> &substrates,
                           const std::vector<std::shared_ptr<LabelingMeasurement>> &measurements)
        : Reduction(data, substrates, measurements) {}

    /// \return begin reduced network iterator
    Iterator begin() const { return Iterator(this->getReactions(), true); }

    /// \return end reduced network iterator
    Iterator end() const { return Iterator(this->getReactions(), false); }
};

} // namespace x3cflux

#endif // X3CFLUX_LABELINGNETWORK_H
