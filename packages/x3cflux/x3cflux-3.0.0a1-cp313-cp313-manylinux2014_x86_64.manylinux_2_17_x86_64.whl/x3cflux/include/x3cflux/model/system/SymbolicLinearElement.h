#ifndef X3CFLUX_SYMBOLICLINEARELEMENT_H
#define X3CFLUX_SYMBOLICLINEARELEMENT_H

#include "ParameterAccessor.h"
#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Symbolic element of a linear system
/// \tparam Stationary IST or INST MFA
template <bool Stationary> class SymbolicLinearElement {
  private:
    Index rowIndex_;
    Index columnIndex_;
    Index poolSizeIndex_;
    bool diagonal_;
    std::vector<std::pair<Index, bool>> fluxCoefficients_;

  public:
    /// Create symbolic linear element
    /// \param rowIndex row index of element
    /// \param columnIndex column index of element
    /// \param poolSizeIndex index of metabolic pool size corresponding to the row
    SymbolicLinearElement(Index rowIndex, Index columnIndex, Index poolSizeIndex)
        : rowIndex_(rowIndex), columnIndex_(columnIndex), poolSizeIndex_(poolSizeIndex),
          diagonal_(rowIndex == columnIndex) {}

    /// Add symbolic flux value to the element
    /// \param reactionIndex index of metabolic reaction associated with flux
    /// \param forward forward or backward flux
    void addFlux(std::size_t reactionIndex, bool forward) { fluxCoefficients_.emplace_back(reactionIndex, forward); }

    /// \return row index of element
    Index getRowIndex() const { return rowIndex_; }

    /// \return column index of element
    Index getColumnIndex() const { return columnIndex_; }

    /// \return index of metabolic pool size corresponding to the row
    Index getPoolSizeIndex() const { return poolSizeIndex_; }

    /// \return row index equal to column index
    bool isDiagonal() const { return diagonal_; }

    /// \return list of index and type representation of metabolic fluxes
    const std::vector<std::pair<Index, bool>> &getFluxCoefficients() const { return fluxCoefficients_; }

    /// Evaluate the symbolic summation of fluxes
    /// \param accessor accessor of metabolic fluxes
    /// \return triplet holding the element value
    RealTriplet evaluate(const ParameterAccessor &accessor) const {
        Real value = 0.;

        for (const auto &flux : this->getFluxCoefficients()) {
            value += accessor.getFlux(flux.first, flux.second);
        }

        if constexpr (not Stationary) {
            value /= accessor.getPoolSize(this->getPoolSizeIndex());
        }

        return {static_cast<int>(this->getRowIndex()), static_cast<int>(this->getColumnIndex()),
                this->isDiagonal() ? -value : value};
    }

    /// Evaluate the partial derivative of the symbolic summation of fluxes
    /// \param accessor accessor of metabolic fluxes and partial derivatives
    /// \return triplet holding the element derivative value
    RealTriplet evaluateDerivative(const DerivativeParameterAccessor &accessor) const {
        Real value = 0.;

        if constexpr (Stationary) {
            for (const auto &flux : this->getFluxCoefficients()) {
                value += accessor.getFluxDerivative(flux.first, flux.second);
            }
        } else {
            // Check if derivative is with respect to pool size
            // todo: improve so it does not depends on float zero check
            Real poolSizeDeriv = accessor.getPoolSizeDerivative(this->getPoolSizeIndex()),
                 poolSize = accessor.getPoolSize(this->getPoolSizeIndex());
            if (std::fabs(poolSizeDeriv) <= std::numeric_limits<Real>::epsilon()) {
                for (const auto &flux : this->getFluxCoefficients()) {
                    value += accessor.getFluxDerivative(flux.first, flux.second);
                }
                value /= poolSize;
            } else {
                for (const auto &flux : this->getFluxCoefficients()) {
                    value -= accessor.getFlux(flux.first, flux.second);
                }
                value /= poolSize * poolSize;
            }
        }

        return {static_cast<int>(this->getRowIndex()), static_cast<int>(this->getColumnIndex()),
                this->isDiagonal() ? -value : value};
    }
};

} // namespace x3cflux

#endif // X3CFLUX_SYMBOLICLINEARELEMENT_H
