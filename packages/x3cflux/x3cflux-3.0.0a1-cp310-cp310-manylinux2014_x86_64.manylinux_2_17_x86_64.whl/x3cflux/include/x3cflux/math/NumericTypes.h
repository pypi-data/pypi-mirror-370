#ifndef X3CFLUX_SRC_MATH_ALGEBRA_H
#define X3CFLUX_SRC_MATH_ALGEBRA_H

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <complex>

namespace x3cflux {

/// For real numbers.
using Real = double;

/// For complex numbers.
using Complex = std::complex<Real>;

/// For integral numbers.
using Integer = long;

/// Unsigned integral type for linear algebra indices.
using Index = Eigen::Index;

/// Dense dynamically sized matrix.
/// \tparam Scalar Matrix element type
template <typename Scalar> using Matrix = Eigen::Matrix<Scalar, Eigen::Dynamic, Eigen::Dynamic>;

/// Real specialization of dense dynamically sized matrix.
using RealMatrix = Matrix<Real>;

/// Complex specialization of dense dynamically sized matrix.
using ComplexMatrix = Matrix<Complex>;

/// Integer specialization of dense dynamically sized matrix.
using IntegerMatrix = Matrix<Integer>;

/// Dense dynamically sized vector.
/// \tparam Scalar Vector element type
template <typename Scalar> using Vector = Eigen::Matrix<Scalar, Eigen::Dynamic, 1>;

/// Real specialization of dense dynamically sized vector.
using RealVector = Vector<Real>;

/// Complex specialization of dense dynamically sized vector.
using ComplexVector = Vector<Complex>;

/// Integer specialization of dense dynamically sized vector.
using IntegerVector = Vector<Integer>;

/// Sparse dynamically sized matrix.
/// \tparam Scalar Matrix element type
template <typename Scalar> using SparseMatrix = Eigen::SparseMatrix<Scalar>;

/// Real specialization of sparse dynamically sized matrix.
using RealSparseMatrix = SparseMatrix<Real>;

/// Complex specialization of sparse dynamically sized matrix.
using ComplexSparseMatrix = SparseMatrix<Complex>;

/// Triplet initializer for sparse matrices.
template <typename Scalar> using Triplet = Eigen::Triplet<Scalar>;

/// Real specialization of triplet initializer.
using RealTriplet = Triplet<Real>;

/// Complex specialization of triplet initializer.
using ComplexTriplet = Triplet<Complex>;

/// Dynamically sized permutation matrix.
using PermutationMatrix = Eigen::PermutationMatrix<Eigen::Dynamic, Eigen::Dynamic>;

} // namespace x3cflux

#endif // X3CFLUX_SRC_MATH_ALGEBRA_H