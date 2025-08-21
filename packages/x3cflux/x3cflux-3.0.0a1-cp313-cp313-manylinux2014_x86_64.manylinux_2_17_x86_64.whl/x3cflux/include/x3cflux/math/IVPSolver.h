#ifndef X3CFLUX_SRC_MATH_IVPSOLVER_H
#define X3CFLUX_SRC_MATH_IVPSOLVER_H

#include "CubicHermiteSpline.h"
#include "IVPBase.h"
#include "NumericTypes.h"

namespace x3cflux {

/// \brief Base for initial value problem solvers
/// \tparam StateType Eigen3 matrix or vector
template <typename StateType> class IVPSolver {
  public:
    typedef StateType State;
    typedef CubicHermiteSpline<State> Solution;
    typedef IVPBase<State> ProblemBase;

  private:
    Real relativeTolerance_, absoluteTolerance_;
    std::size_t numMaxSteps_;

  public:
    /// Creates initial value problem solver.
    /// \param relativeTolerance relative local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit IVPSolver(Real relativeTolerance, Real absoluteTolerance, std::size_t numMaxSteps) {
        setRelativeTolerance(relativeTolerance);
        setAbsoluteTolerance(absoluteTolerance);
        setNumMaxSteps(numMaxSteps);
    }

    /// Solves initial value problem.
    /// \param problem initial value problem to solve
    /// \return interpolated solution and derivative
    inline virtual Solution solve(const ProblemBase &problem) const = 0;

    /// \return relative local error tolerance
    Real getRelativeTolerance() const { return relativeTolerance_; }

    /// \return absolute local error tolerance
    Real getAbsoluteTolerance() const { return absoluteTolerance_; }

    /// \return maximum number of steps allowed
    std::size_t getNumMaxSteps() const { return numMaxSteps_; }

    /// \param relativeTolerance local error tolerance
    void setRelativeTolerance(Real relativeTolerance) {
        if (relativeTolerance < std::numeric_limits<Real>::epsilon()) {
            X3CFLUX_THROW(MathError, "IVPSolver: Relative tolerance below available accuracy (" +
                                         std::to_string(std::numeric_limits<Real>::epsilon()) + ")");
        } else if (relativeTolerance > 1.) {
            X3CFLUX_THROW(MathError, "IVPSolver: Relative tolerance exceeds upper bound (1)");
        }

        relativeTolerance_ = relativeTolerance;
    }

    /// \param relativeTolerance local error tolerance
    void setAbsoluteTolerance(Real absoluteTolerance) {
        if (absoluteTolerance < std::numeric_limits<Real>::epsilon()) {
            X3CFLUX_THROW(MathError, "IVPSolver: Absolute tolerance below available accuracy (" +
                                         std::to_string(std::numeric_limits<Real>::epsilon()) + ")");
        } else if (absoluteTolerance > 1.) {
            X3CFLUX_THROW(MathError, "IVPSolver: Absolute tolerance exceeds upper bound (1)");
        }

        absoluteTolerance_ = absoluteTolerance;
    }

    /// \param maximum number of steps allowed
    void setNumMaxSteps(std::size_t numMaxSteps) { numMaxSteps_ = numMaxSteps; }

    /// \return deep copy of solver
    virtual std::unique_ptr<IVPSolver<State>> copy() const = 0;
};

/// \brief Base for linear initial value problem solvers
/// \tparam StateType Eigen3 matrix or vector
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType> class LinearIVPSolver {
  public:
    typedef StateType State;
    typedef MatrixType Matrix;
    typedef CubicHermiteSpline<State> Solution;
    typedef LinearIVPBase<State, Matrix> ProblemBase;

  private:
    Real relativeTolerance_, absoluteTolerance_;
    std::size_t numMaxSteps_;

  public:
    /// Creates solver for linear initial value problems.
    /// \param relativeTolerance relative local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit LinearIVPSolver(Real relativeTolerance, Real absoluteTolerance, std::size_t numMaxSteps) {
        setRelativeTolerance(relativeTolerance);
        setAbsoluteTolerance(absoluteTolerance);
        setNumMaxSteps(numMaxSteps);
    }

    /// Solves linear initial value problem.
    /// \param problem linear initial value problem to solve
    /// \return interpolated solution and derivative
    inline virtual Solution solve(const ProblemBase &problem) const = 0;

    /// \return relative local error tolerance
    Real getRelativeTolerance() const { return relativeTolerance_; }

    /// \return absolute local error tolerance
    Real getAbsoluteTolerance() const { return absoluteTolerance_; }

    /// \return maximum number of steps allowed
    std::size_t getNumMaxSteps() const { return numMaxSteps_; }

    /// \param relativeTolerance local error tolerance
    void setRelativeTolerance(Real relativeTolerance) {
        if (relativeTolerance < std::numeric_limits<Real>::epsilon()) {
            X3CFLUX_THROW(MathError, "LinearIVPSolver: Relative tolerance below available "
                                     "accuracy (" +
                                         std::to_string(std::numeric_limits<Real>::epsilon()) + ")");
        } else if (relativeTolerance > 1.) {
            X3CFLUX_THROW(MathError, "LinearIVPSolver: Relative tolerance "
                                     "exceeds upper bound (1)");
        }

        relativeTolerance_ = relativeTolerance;
    }

    /// \param relativeTolerance local error tolerance
    void setAbsoluteTolerance(Real absoluteTolerance) {
        if (absoluteTolerance < std::numeric_limits<Real>::epsilon()) {
            X3CFLUX_THROW(MathError, "IVPSolver: Absolute tolerance below available accuracy (" +
                                         std::to_string(std::numeric_limits<Real>::epsilon()) + ")");
        } else if (absoluteTolerance > 1.) {
            X3CFLUX_THROW(MathError, "IVPSolver: Absolute tolerance exceeds upper bound (1)");
        }

        absoluteTolerance_ = absoluteTolerance;
    }

    /// \param maximum number of steps allowed
    void setNumMaxSteps(std::size_t numMaxSteps) { numMaxSteps_ = numMaxSteps; }

    /// \return deep copy of solver
    virtual std::unique_ptr<LinearIVPSolver<State, Matrix>> copy() const = 0;
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MATH_IVPSOLVER_H