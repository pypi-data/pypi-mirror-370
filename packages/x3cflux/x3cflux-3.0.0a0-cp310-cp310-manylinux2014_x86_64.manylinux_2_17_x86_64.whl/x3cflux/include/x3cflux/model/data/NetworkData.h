#ifndef X3CFLUX_SRC_DATA_NETWORKDATA_H
#define X3CFLUX_SRC_DATA_NETWORKDATA_H

#include "Metabolite.h"
#include "Reaction.h"
#include <list>

namespace x3cflux {

/// \brief Metabolic network data
///
/// Stores structure and atom transitions of the metabolic network. The Pool
/// instances can be interpreted as the vertices of the network and the Reaction
/// instances as the edges.
class NetworkData {
  private:
    std::vector<Metabolite> metabolites_;
    std::vector<Reaction> reactions_;

  public:
    /// \brief Creates a network data storage.
    /// \param pools metabolite data
    /// \param reactions reaction data
    NetworkData(std::vector<Metabolite> metabolites, std::vector<Reaction> reactions)
        : metabolites_(std::move(metabolites)), reactions_(std::move(reactions)) {}

    /// \return metabolite data
    const std::vector<Metabolite> &getMetabolites() const { return metabolites_; }

    /// \return reaction data
    const std::vector<Reaction> &getReactions() const { return reactions_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_NETWORKDATA_H