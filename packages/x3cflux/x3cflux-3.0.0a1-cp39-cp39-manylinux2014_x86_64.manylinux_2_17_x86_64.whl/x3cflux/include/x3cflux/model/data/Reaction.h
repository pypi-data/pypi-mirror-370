#ifndef X3CFLUX_SRC_DATA_REACTION_H
#define X3CFLUX_SRC_DATA_REACTION_H

#include <util/Permutation.h>

#include <utility>

namespace x3cflux {

/// \brief Metabolic reaction data
///
/// Stores partaking educts and products names that can be matched with instances
/// of the Pool class. Also contains the permutation of the traceable atoms
/// (carbon, nitrogen, etc.) from the educts atoms to the products atoms. The
/// order of educts and products in the permutation is given by the storage
/// order.
class Reaction {
  private:
    std::string name_;
    std::size_t numAtoms_;
    bool bidirectional_;

    Permutation atomPermutation;
    std::vector<std::string> eductNames_;
    std::vector<std::string> productNames_;

  public:
    /// \brief Creates metabolic reaction.
    /// \param name name of the reaction
    /// \param numAtoms number of traceable atoms partaking
    /// \param bidirectional indicates if bi- or unidirectional
    /// \param atomPermutation permutation of the traceable atoms
    /// \param eductNames names of reaction educts
    /// \param productNames names of reaction products
    Reaction(std::string name, std::size_t numAtoms, bool bidirectional, Permutation atomPermutation,
             std::vector<std::string> eductNames, std::vector<std::string> productNames)
        : name_(std::move(name)), numAtoms_(numAtoms), bidirectional_(bidirectional),
          atomPermutation(std::move(atomPermutation)), eductNames_(std::move(eductNames)),
          productNames_(std::move(productNames)) {}

    /// \return name of the metabolic reaction
    const std::string &getName() const { return name_; }

    /// \return number of traceable atoms partaking
    std::size_t getNumAtoms() const { return numAtoms_; }

    /// \return if bidirectional or unidirectional
    bool isBidirectional() const { return bidirectional_; }

    /// \return permutation of the traceable atoms
    const Permutation &getAtomPermutation() const { return atomPermutation; }

    /// \return names of the reactions educts
    const std::vector<std::string> &getEductNames() const { return eductNames_; }

    /// \return names of the reactions products
    const std::vector<std::string> &getProductNames() const { return productNames_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_REACTION_H