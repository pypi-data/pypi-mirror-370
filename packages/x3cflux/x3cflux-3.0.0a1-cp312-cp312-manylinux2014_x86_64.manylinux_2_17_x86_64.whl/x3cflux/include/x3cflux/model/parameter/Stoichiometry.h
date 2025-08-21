#ifndef X3CFLUX_SRC_MAIN_PARAMETER_STOICHIOMETRY_H
#define X3CFLUX_SRC_MAIN_PARAMETER_STOICHIOMETRY_H

#include <utility>
#include <vector>

#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Stoichiometry of a metabolic model
class Stoichiometry {
  private:
    IntegerMatrix stoichiometricMatrix_;
    std::vector<std::string> metaboliteNames_;
    std::vector<std::string> reactionNames_;

  public:
    /// \brief Creates stoichiometry.
    /// \param stoichiometricMatrix matrix of reaction equations
    /// \param metaboliteNames names of inner metabolites
    /// \param reactionNames names of reactions
    Stoichiometry(IntegerMatrix stoichiometricMatrix, std::vector<std::string> metaboliteNames,
                  std::vector<std::string> reactionNames)
        : stoichiometricMatrix_(std::move(stoichiometricMatrix)), metaboliteNames_(std::move(metaboliteNames)),
          reactionNames_(std::move(reactionNames)) {}

    /// \return matrix of reaction equations
    const IntegerMatrix &getStoichiometricMatrix() const { return stoichiometricMatrix_; }

    /// \return names of inner metabolites
    const std::vector<std::string> &getMetaboliteNames() const { return metaboliteNames_; }

    /// \return names of reactions
    const std::vector<std::string> &getReactionNames() const { return reactionNames_; }

    /// \return number of inner metabolites
    Index getNumMetabolites() const { return stoichiometricMatrix_.rows(); }

    /// \return number of reactions
    Index getNumReactions() const { return stoichiometricMatrix_.cols(); }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_STOICHIOMETRY_H