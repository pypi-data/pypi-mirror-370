#ifndef X3CFLUX_SRC_UTILS_PERMUTATION_H
#define X3CFLUX_SRC_UTILS_PERMUTATION_H

#include <numeric>
#include <utility>
#include <valarray>
#include <vector>

#include "Logging.h"

namespace x3cflux {

/// \brief Permutation of a finite family.
class Permutation {
  private:
    std::valarray<std::size_t> indices_;

  public:
    /// \brief Creates identity permutation.
    /// \param numIndices number of indices of the family
    explicit Permutation(std::size_t numIndices) : indices_(numIndices) {
        std::iota(std::begin(indices_), std::end(indices_), std::size_t(0));
    }

    /// \brief Creates permutation.
    /// \param indices permutation of the families indices
    explicit Permutation(std::valarray<std::size_t> indices) : indices_(std::move(indices)) {
        X3CFLUX_CHECK(checkIfAllIndicesExist());
    }

    /// \brief Applies the permutation.
    /// \param i index of the permuted family
    /// \return index of the not-permuted family
    std::size_t operator()(std::size_t i) const {
        X3CFLUX_CHECK(i < getNumIndices());

        return apply(i);
    }

    /// \brief Compares two permutations for equality.
    /// \param permutation other permutation
    /// \return equal or not
    bool operator==(const Permutation &permutation) const { return (this->indices_ == permutation.indices_).min(); }

    /// \brief Computes the inverse of this permutation.
    /// \return inverse permutation
    Permutation getInverse() const {
        std::valarray<std::size_t> permutationIndices(getNumIndices());

        for (std::size_t i = 0; i < getNumIndices(); ++i) {
            permutationIndices[apply(i)] = i;
        }

        return Permutation(permutationIndices);
    }

    /// \brief Applies permutation to a family.
    /// \tparam Family object with [] operator for 0,...,"length of this permutation"-1
    /// \param family indexed family to permute
    /// \return permuted indexed family
    template <typename Family> Family permute(const Family &family) const {
        X3CFLUX_CHECK(family.size() == getNumIndices());

        Family permutedFamily(family);
        for (std::size_t i = 0; i < getNumIndices(); ++i) {
            permutedFamily[apply(i)] = family[i];
        }

        return permutedFamily;
    }

    /// \brief Applies inverse permutation to a family.
    /// \tparam Family object with [] operator for 0,...,"length of this permutation"-1
    /// \param family indexed family to permute inversely
    /// \return inverse-permuted indexed family
    template <typename Family> Family permuteInverse(const Family &family) const {
        X3CFLUX_CHECK(family.size() == getNumIndices());

        Permutation inverse = getInverse();
        return inverse.permute(family);
    }

    /// \return number of indices of the family
    std::size_t getNumIndices() const { return indices_.size(); }

    /// \return indices that encode the permutation
    const std::valarray<std::size_t> &getIndices() const { return indices_; }

  private:
    std::size_t apply(std::size_t i) const { return indices_[i]; }

    bool checkIfAllIndicesExist() const {
        for (std::size_t i = 0; i < getNumIndices(); ++i) {
            if (std::find(std::begin(indices_), std::end(indices_), i) == std::end(indices_)) {
                return false;
            }
        }

        return true;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_UTILS_PERMUTATION_H