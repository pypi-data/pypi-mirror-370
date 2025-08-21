#ifndef X3CFLUX_SRC_MAIN_PARAMETER_SOLUTIONSPACE_H
#define X3CFLUX_SRC_MAIN_PARAMETER_SOLUTIONSPACE_H

#include <math/NumericTypes.h>

#include <utility>

namespace x3cflux {

/// \brief Solution space of a linear equation system
///
/// An underdetermined system \f$\mathbf{A} \cdot \mathbf{x} = \mathbf{b}\f$
/// has infinitely many solutions that can calculated by
/// \f$\mathbf{p} + Kern(\mathbf{A})\f$, where \f$\mathbf{p}\f$ is a
/// particular solution of the system.
///
/// A SolutionSpace instance is the result of a numerical computation of
/// such a solution space. It consists of the particular solution, a
/// transformation to the kernel space (input basis depends on computation
/// method) and the permutation of the solution space components. To obtain
/// the solution space in the basis of \f$\mathbf{A}\f$, the inverse
/// permutation must be applied.
class SolutionSpace {
  private:
    RealVector particularSolution_;
    RealMatrix kernelBasis_;
    PermutationMatrix permutation_;

  public:
    /// \brief Create solution space.
    /// \param particularSolution particular solution of the system
    /// \param kernelBasis transformation matrix to the kernel space
    /// \param permutation solution space component permutation
    SolutionSpace(RealVector particularSolution, RealMatrix kernelBasis, const PermutationMatrix &permutation)
        : particularSolution_(std::move(particularSolution)), kernelBasis_(std::move(kernelBasis)),
          permutation_(permutation) {}

    /// \return particular solution of the system
    const RealVector &getParticularSolution() const { return particularSolution_; }

    /// \return transformation matrix to the kernel space
    const RealMatrix &getKernelBasis() const { return kernelBasis_; }

    /// \return solution space component permutation
    const PermutationMatrix &getPermutation() const { return permutation_; }

    /// \return dimension of the kernel
    Index getDimension() const { return kernelBasis_.cols(); }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_SOLUTIONSPACE_H