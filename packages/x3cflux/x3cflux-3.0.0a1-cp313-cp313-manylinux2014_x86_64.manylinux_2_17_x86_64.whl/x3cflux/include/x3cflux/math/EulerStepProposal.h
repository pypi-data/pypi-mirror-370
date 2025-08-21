#ifndef X3CFLUX_EULERSTEPPROPOSAL_H
#define X3CFLUX_EULERSTEPPROPOSAL_H

#include "IVPSolver.h"
#include "LESSolver.h"

namespace x3cflux {

/// \brief Step proposal using left rectangular rule
/// \tparam StateType Eigen3 vector or matrix
template <typename StateType> struct ExplicitEulerStepProposal {
  public:
    typedef StateType State;
    static constexpr Index ADVANCE_ORDER = 1;

  public:
    static std::pair<State, State> proposeFixedStep(const IVPBase<State> &problem, const State &state, Real time,
                                                    Real stepSize, const State &derivative) {
        auto advState = state + stepSize * derivative;
        return std::make_pair(advState, problem(time + stepSize, advState));
    }
};

/// \brief Step proposal for linear IVP's using right rectangular rule
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType> struct LinearImplicitEulerStepProposal {
  public:
    typedef StateType State;
    typedef MatrixType Matrix;
    static constexpr Index ADVANCE_ORDER = 1;

  public:
    static std::pair<State, State> proposeFixedStep(const LinearIVPBase<State, Matrix> &problem, const State &state,
                                                    Real time, Real stepSize, const State &derivative) {
        std::ignore = derivative;

        LUSolver<Matrix, State> solver;
        RealSparseMatrix identity(problem.getSize(), problem.getSize());
        identity.setIdentity();

        auto inhomEval = problem.evaluateInhomogeneity(time + stepSize);
        LinearEquationSystem<Matrix, State> linSys(identity - stepSize * problem.getJacobiMatrix(),
                                                   state + stepSize * inhomEval);
        auto advState = solver.solve(linSys);

        return std::make_pair(advState, problem.getJacobiMatrix() * state + inhomEval);
    }
};

} // namespace x3cflux

#endif // X3CFLUX_EULERSTEPPROPOSAL_H
