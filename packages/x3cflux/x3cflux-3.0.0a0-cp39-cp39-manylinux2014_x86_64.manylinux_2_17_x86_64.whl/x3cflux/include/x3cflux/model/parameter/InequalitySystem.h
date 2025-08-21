#ifndef X3CFLUX_SRC_MAIN_PARAMETER_INEQUALITYSYSTEM_H
#define X3CFLUX_SRC_MAIN_PARAMETER_INEQUALITYSYSTEM_H

#include <math/NumericTypes.h>

#include <utility>

namespace x3cflux {

/// \brief System of inequalities \f$\mathbf{A} \cdot \mathbf{x} \le \mathbf{b}\f$
///
/// With \f$\mathbf{A}^{m \times n} \in \mathbb{R}^n\f$, the solution of the inequality
/// system is a subset of \f$\mathbb{R}^n\f$. The solution set can be expressed as intersection
/// of closed half spaces that define a convex \f$n\f$-polytope.
class InequalitySystem {
  private:
    RealMatrix matrix_;
    RealVector bound_;

  public:
    /// \brief Creates inequality system.
    /// \param matrix system matrix
    /// \param bound bound vector
    InequalitySystem(RealMatrix matrix, RealVector bound) : matrix_(std::move(matrix)), bound_(std::move(bound)) {}

    /// \return system matrix
    const RealMatrix &getMatrix() const { return matrix_; }

    /// \return bound vector
    const RealVector &getBound() const { return bound_; }

    /// \return number of unknowns
    Index getNumUnknowns() const { return matrix_.cols(); }

    /// \return number of inequalities
    Index getNumInequalities() const { return matrix_.rows(); }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_INEQUALITYSYSTEM_H