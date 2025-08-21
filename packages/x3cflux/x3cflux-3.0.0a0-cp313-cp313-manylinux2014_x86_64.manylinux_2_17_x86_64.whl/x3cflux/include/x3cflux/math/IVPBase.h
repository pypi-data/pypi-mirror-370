#ifndef X3CFLUX_INITIALVALUEPROBLEMBASE_H
#define X3CFLUX_INITIALVALUEPROBLEMBASE_H

#include "NumericTypes.h"

#include <util/Logging.h>

namespace x3cflux {

/// \brief Base class for initial value problems
/// \tparam StateType Eigen3 matrix or vector
template <typename StateType> class IVPBase {
  public:
    typedef StateType State;

  private:
    Real startTime_;
    Real endTime_;
    State initialValue_;

  public:
    /// Creates initial value problem.
    /// \param startTime initial time point
    /// \param endTime end time point
    /// \param initialValue initial state
    IVPBase(Real startTime, Real endTime, State initialValue)
        : startTime_(startTime), endTime_(endTime), initialValue_(initialValue) {
        X3CFLUX_CHECK(initialValue_.rows() >= 1 and initialValue_.cols() >= 1);
    }

    /// \return size of the state vector
    Index getSize() const { return initialValue_.rows(); }

    /// \return number of states to solved simultaneously
    Index getNumStates() const { return initialValue_.cols(); }

    /// \return initial time point
    const Real &getStartTime() const { return startTime_; }

    /// \return end time point
    Real getEndTime() const { return endTime_; }

    /// \return initial value of the initial value problem
    State getInitialValue() const { return initialValue_; }

    /// Evaluates the right hand side of the ODE.
    /// \param time point in time
    /// \param state solution function value
    /// \return derivative of the solution function
    virtual State operator()(Real time, const State &state) const = 0;
};

/// \brief Base class for linear initial value problems.
/// \tparam StateType Eigen3 matrix or vector
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType> class LinearIVPBase : public IVPBase<StateType> {
  public:
    using typename IVPBase<StateType>::State;
    typedef MatrixType Matrix;

  private:
    Matrix jacobiMatrix_;

  public:
    /// Creates initial value problem.
    /// \param startTime initial time point
    /// \param endTime end time point
    /// \param initialValue initial state
    /// \param jacobiMatrix jacobi matrix of the initial value problem
    LinearIVPBase(Real startTime, Real endTime, State initialValue, Matrix jacobiMatrix)
        : IVPBase<StateType>(startTime, endTime, initialValue), jacobiMatrix_(jacobiMatrix) {
        X3CFLUX_CHECK(jacobiMatrix_.rows() == this->getSize() and jacobiMatrix_.rows() == jacobiMatrix_.cols());
    }

    /// \return jacobi matrix of the initial value problem
    const Matrix &getJacobiMatrix() const { return jacobiMatrix_; }

    /// Evaluates the inhomogeneity of the linear initial value problem.
    /// \param time point in time
    /// \return inhomogenity value at time point
    virtual State evaluateInhomogeneity(Real time) const = 0;

    /// Evaluates the right hand side of the linear ODE.
    /// \param time point in time
    /// \param state solution function value
    /// \return derivative of the solution function
    State operator()(Real time, const State &state) const override {
        return jacobiMatrix_ * state + evaluateInhomogeneity(time);
    }
};
} // namespace x3cflux

#endif // X3CFLUX_INITIALVALUEPROBLEMBASE_H
