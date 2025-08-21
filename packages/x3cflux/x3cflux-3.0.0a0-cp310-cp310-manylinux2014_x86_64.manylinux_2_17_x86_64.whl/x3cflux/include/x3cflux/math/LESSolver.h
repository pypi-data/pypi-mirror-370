#ifndef X3CFLUX_SRC_MATH_LESSOLVER_H
#define X3CFLUX_SRC_MATH_LESSOLVER_H

#include "MathError.h"
#include "NumericTypes.h"
#include <util/Logging.h>

namespace x3cflux {

/// \brief Linear equation system with an optional initial guess
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LinearEquationSystem {
  public:
    typedef MatrixType_ MatrixType;
    typedef RhsType_ RhsType;

  private:
    MatrixType matrix_;
    RhsType rhs_;
    RhsType initialGuess_;

  public:
    /// Creates an linear equation system from matrix and rhs.
    /// \param matrix system matrix
    /// \param rhs system right hand side
    /// \param initialGuess initially guessed solution value (default zero)
    LinearEquationSystem(MatrixType matrix, RhsType rhs, RhsType initialGuess = RhsType())
        : matrix_(matrix), rhs_(rhs), initialGuess_(initialGuess) {
        if (initialGuess_.rows() == 0) {
            initialGuess_ = RhsType::Zero(rhs.rows(), rhs.cols());
        }
    }

    /// \return number of equations (rows).
    Index getNumEquations() const { return matrix_.rows(); }

    /// \return number of unknowns (columns).
    Index getNumUnknowns() const { return matrix_.cols(); }

    /// \return number of right hand sides (if RhsType is matrix valued)
    Index getNumRhs() const { return rhs_.cols(); }

    /// \return matrix of the linear equation system
    const MatrixType &getMatrix() const { return matrix_; }

    /// \return right hand side of the linear equation system
    const RhsType &getRhs() const { return rhs_; }

    /// \return initially guessed solution value (e.g. for iterative solvers)
    const RhsType &getInitialGuess() const { return initialGuess_; }
};

/// \brief Base for a linear equation system solver
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LESSolver {
  public:
    typedef MatrixType_ MatrixType;
    typedef RhsType_ RhsType;
    typedef typename MatrixType::Scalar Scalar;
    typedef RhsType SolutionType;

  private:
    Real tolerance_;

  public:
    /// \brief Creates linear equation solver.
    /// \param tolerance error tolerance
    explicit LESSolver(Real tolerance = 1e-9) : tolerance_(tolerance) {
        // only eigen matrices are supported
        static_assert(std::is_same<MatrixType, Matrix<Scalar>>::value or
                          std::is_same<MatrixType, SparseMatrix<Scalar>>::value,
                      "unsupported matrix type");
        // only eigen vectors or matrices (with same scalar type) can be rhs
        static_assert(std::is_same<RhsType, Vector<Scalar>>::value or std::is_same<RhsType, Matrix<Scalar>>::value,
                      "unsupported rhs type");
    }

    /// Solves a given linear equation system.
    /// \return solution vector or matrix
    inline virtual SolutionType solve(const LinearEquationSystem<MatrixType, RhsType> &) const = 0;

    /// \return error tolerance
    Real getTolerance() const { return tolerance_; }

    /// \param tolerance error tolerance
    void setTolerance(Real tolerance) { tolerance_ = tolerance; }

    /// \return deep copy of solver
    virtual std::unique_ptr<LESSolver<MatrixType, RhsType>> copy() const = 0;
};

/// \brief LU solver for sparse and dense linear equation systems
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LUSolver : public LESSolver<MatrixType_, RhsType_> {
  public:
    typedef LESSolver<MatrixType_, RhsType_> Base;
    using typename Base::MatrixType;
    using typename Base::RhsType;
    using typename Base::Scalar;
    using typename Base::SolutionType;
    typedef std::conditional_t<std::is_same<MatrixType, Matrix<Scalar>>::value, Eigen::PartialPivLU<Matrix<Scalar>>,
                               Eigen::SparseLU<SparseMatrix<Scalar>>>
        Method;

    explicit LUSolver(Real tolerance = 1e-9) : Base(tolerance) {}

    inline SolutionType solve(const LinearEquationSystem<MatrixType, RhsType> &linearEquationSystem) const override {
        X3CFLUX_CHECK(linearEquationSystem.getNumEquations() == linearEquationSystem.getNumUnknowns());
        Method method(linearEquationSystem.getMatrix());
        if (not check_decomposition(method)) {
            X3CFLUX_THROW(MathError, std::string(std::is_same<Method, Eigen::SparseLU<SparseMatrix<Scalar>>>::value
                                                     ? "SparseLES Solver"
                                                     : "Dense LES Solver") +
                                         ": Singular system");
        }
        return method.solve(linearEquationSystem.getRhs());
    }

    std::unique_ptr<LESSolver<MatrixType, RhsType>> copy() const override {
        return std::make_unique<LUSolver<MatrixType, RhsType>>(*this);
    }

  private:
    inline static bool check_decomposition(const Eigen::PartialPivLU<Matrix<Scalar>> &decomposition) {
        auto absolute_value = std::fabs(decomposition.determinant());
        return absolute_value > std::numeric_limits<decltype(absolute_value)>::epsilon();
    }

    inline static bool check_decomposition(const Eigen::SparseLU<SparseMatrix<Scalar>> &decomposition) {
        return decomposition.info() == Eigen::ComputationInfo::Success;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MATH_LESSOLVER_H