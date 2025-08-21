#ifndef X3CFLUX_RKSTEPPROPOSAL_H
#define X3CFLUX_RKSTEPPROPOSAL_H

#include "IVPBase.h"
#include "LESSolver.h"

namespace x3cflux {

/// \brief Step proposal for Runge Kutta methods in Butcher representation
/// \tparam Support calculation method for supports
template <typename Support> struct RKStepProposal {
    typedef typename Support::ProblemBase ProblemBase;
    typedef typename Support::State State;
    typedef typename Support::Scheme Scheme;

    static constexpr Index ADVANCE_ORDER = Scheme::ADVANCE_ORDER;
    static constexpr Index CORRECTION_ORDER = Scheme::EMBEDDED_ORDER;
    static constexpr Index NUM_STAGES = Scheme::NUM_STAGES;

    static std::pair<State, State> proposeFixedStep(const ProblemBase &problem, const State &state, Real time,
                                                    Real stepSize, const State &derivative) {
        auto supports = Support::computeSupports(problem, state, time, stepSize, derivative);

        // Calculate step x_next = x + h * sum(b_i * k_i, i=1..s)
        State advSuppComb = Scheme::ADVANCE_COEFFS(0) * supports[0];
        for (Index suppIndex = 1; suppIndex < NUM_STAGES; ++suppIndex) {
            advSuppComb += Scheme::ADVANCE_COEFFS(suppIndex) * supports[suppIndex];
        }

        return std::make_pair(state + stepSize * advSuppComb, supports.back());
    }

    static std::tuple<State, State, State> proposeAdaptiveStep(const ProblemBase &problem, const State &state,
                                                               Real time, Real stepSize, const State &derivative,
                                                               Real tolerance = std::numeric_limits<Real>::epsilon()) {
        auto supports = Support::computeSupports(problem, state, time, stepSize, derivative, tolerance);

        // Calculate step x_next = x + h * sum(b_i * k_i, i=1..s) with
        // advancing method (higher order) and embedded method (lower order)
        State advSuppComb = Scheme::ADVANCE_COEFFS(0) * supports[0];
        State embSuppComb = Scheme::EMBEDDED_COEFFS(0) * supports[0];
        for (Index suppIndex = 1; suppIndex < NUM_STAGES; ++suppIndex) {
            advSuppComb += Scheme::ADVANCE_COEFFS(suppIndex) * supports[suppIndex];
            embSuppComb += Scheme::EMBEDDED_COEFFS(suppIndex) * supports[suppIndex];
        }

        return std::make_tuple(state + stepSize * advSuppComb, state + stepSize * embSuppComb, supports.back());
    }
};

/// \brief Support calculation for explicit RK methods with Fehlberg property
/// \tparam StateType Eigen3 vector or matrix
/// \tparam SchemeType butcher scheme of the ERKF method
template <typename StateType, typename SchemeType> struct ERKFSupport {
    typedef IVPBase<StateType> ProblemBase;
    typedef typename ProblemBase::State State;
    typedef SchemeType Scheme;

    static constexpr Index ADVANCE_ORDER = Scheme::ADVANCE_ORDER;
    static constexpr Index NUM_STAGES = Scheme::NUM_STAGES;

    static std::vector<State> computeSupports(const ProblemBase &problem, const State &state, Real time, Real stepSize,
                                              const State &derivative, Real tolerance) {
        std::ignore = tolerance;

        std::vector<State> supports;

        // Calculate k_i = f(x + h * sum(k_j, j=1..i-1), t + h * c_i)
        supports.push_back(derivative);
        for (Index suppIndex = 1; suppIndex < NUM_STAGES; ++suppIndex) {
            State supportComb = Scheme::SUPPORT_COEFFS(suppIndex, 0) * supports[0];
            for (Index j = 1; j < suppIndex; ++j) {
                supportComb += Scheme::SUPPORT_COEFFS(suppIndex, j) * supports[j];
            }

            supports.push_back(
                problem(time + stepSize * Scheme::TIME_COEFFS(suppIndex), state + stepSize * supportComb));
        }

        return supports;
    }
};

/// \brief Step proposal for ERKF methods in Butcher representation
/// \tparam StateType Eigen3 vector or matrix
/// \tparam Scheme butcher scheme of the ERKF method
template <typename StateType, typename Scheme> using ERKFStepProposal = RKStepProposal<ERKFSupport<StateType, Scheme>>;

/// \brief Support calculation for SDIRK methods on linear IVP's
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
/// \tparam SchemeType butcher scheme of the SDIRK method
template <typename StateType, typename MatrixType, typename SchemeType> struct LinearSDIRKSupport {
    typedef LinearIVPBase<StateType, MatrixType> ProblemBase;
    typedef typename ProblemBase::State State;
    typedef typename ProblemBase::Matrix Matrix;
    typedef SchemeType Scheme;

    static constexpr Index ADVANCE_ORDER = Scheme::ADVANCE_ORDER;
    static constexpr Index NUM_STAGES = Scheme::NUM_STAGES;

    static std::vector<State> computeSupports(const LinearIVPBase<State, Matrix> &problem, const State &state,
                                              Real time, Real stepSize, const State &derivative, Real tolerance) {
        std::ignore = derivative;
        std::ignore = tolerance;

        Index size = problem.getSize();
        std::vector<State> supports;
        supports.reserve(NUM_STAGES);

        // Generate I - h * gamma * J and set up iterative solver
        RealSparseMatrix identity(size, size);
        identity.setIdentity();
        auto supportMatrix = identity - stepSize * Scheme::SUPPORT_COEFFS(0, 0) * problem.getJacobiMatrix();
        Eigen::SparseLU<Matrix> solver(supportMatrix);

        // Calculate k_i = f(x + h * sum(k_j, j=1..i), t + h * c_i) by solving
        // a linear equation system for k_i
        supports.push_back(solver.solve(problem(time + stepSize * Scheme::TIME_COEFFS(0), state)));
        for (Index suppIndex = 1; suppIndex < NUM_STAGES; ++suppIndex) {
            State supportComb = Scheme::SUPPORT_COEFFS(suppIndex, 0) * supports[0];
            for (Index j = 1; j < suppIndex; ++j) {
                supportComb += Scheme::SUPPORT_COEFFS(suppIndex, j) * supports[j];
            }

            supports.push_back(solver.solve(
                problem(time + stepSize * Scheme::TIME_COEFFS(suppIndex), state + stepSize * supportComb)));
        }

        return supports;
    }
};

/// \brief Step proposal for SDIRK methods in Butcher representation
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
/// \tparam Scheme butcher scheme of the SDIRK method
template <typename StateType, typename MatrixType, typename Scheme>
using LinearSDIRKStepProposal = RKStepProposal<LinearSDIRKSupport<StateType, MatrixType, Scheme>>;

/// \brief Butcher scheme of the DOPRI54 method
struct DOPRI54Scheme {
    typedef Eigen::Matrix<Real, 7, 7> RealMatrix7;
    typedef Eigen::Matrix<Real, 7, 1> RealVector7;

    static const RealMatrix7 SUPPORT_COEFFS;
    static const RealVector7 TIME_COEFFS;

    static const RealVector7 ADVANCE_COEFFS;
    static const RealVector7 EMBEDDED_COEFFS;

    static constexpr Index ADVANCE_ORDER = 5;
    static constexpr Index EMBEDDED_ORDER = 4;
    static constexpr Index NUM_STAGES = 7;
};

/// \brief Butcher scheme of the SDIRK43 method
struct SDIRK43Scheme {
    typedef Eigen::Matrix<Real, 5, 5> RealMatrix5;
    typedef Eigen::Matrix<Real, 5, 1> RealVector5;

    static const RealMatrix5 SUPPORT_COEFFS;
    static const RealVector5 TIME_COEFFS;

    static const RealVector5 ADVANCE_COEFFS;
    static const RealVector5 EMBEDDED_COEFFS;

    static constexpr Index ADVANCE_ORDER = 4;
    static constexpr Index EMBEDDED_ORDER = 3;
    static constexpr Index NUM_STAGES = 5;
};

} // namespace x3cflux

#endif // X3CFLUX_RKSTEPPROPOSAL_H
