/// Robustification of the step size was derived from the CVODE 5.3.0 ODE solver package.
///
/// BSD 3-Clause License Copyright (c) 2002-2019, Lawrence Livermore National Security and Southern Methodist
/// University. All rights reserved. Redistribution and use in source and binary forms, with or without modification,
/// are permitted provided that the following conditions are met:
/// * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
/// disclaimer.
/// * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
/// following disclaimer
///   in the documentation and/or other materials provided with the distribution.
/// * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
/// products derived
///   from this software without specific prior written permission.
///
/// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
/// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
/// FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
/// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
/// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
/// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
/// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
/// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#ifndef X3CFLUX_ADAPTIVEIVPSOLVER_H
#define X3CFLUX_ADAPTIVEIVPSOLVER_H

#include "IVPSolver.h"
#include "RKStepProposal.h"

namespace x3cflux {

/// \brief Adaptive IVP solver
/// \tparam IVPSolverBaseType type of the IVP (e.g. IVPBase or LinearIVPBase)
/// \tparam StepProposal method with advance and correction proposal
///
/// The adaptive IVP solver can be set up with different proposal or stepping methods
/// that calculate the advance of the iterative solution procedure. The proposals must
/// match the IVP base type and must yield a second lower order proposal for local error
/// control.
template <typename IVPSolverBaseType, typename StepProposal> class AdaptiveIVPSolver : public IVPSolverBaseType {
  public:
    using typename IVPSolverBaseType::ProblemBase;
    using typename IVPSolverBaseType::Solution;
    using typename IVPSolverBaseType::State;

    /// Accuracy order of advancing method (local error is in \f$\mathcal{O}(h^{ADVANCE\_ORDER})\f$)
    static constexpr std::size_t ADVANCE_ORDER = StepProposal::ADVANCE_ORDER;

    /// Accuracy order of correction method (local error is in \f$\mathcal{O}(h^{CORRECTION\_ORDER})\f$)
    static constexpr std::size_t CORRECTION_ORDER = StepProposal::CORRECTION_ORDER;

  public:
    std::size_t numMaxStepAttempts_;

  public:
    /// Create adaptive IVP solver.
    /// \param numMaxStepAttempts maximum number of unaccepted steps
    /// \param relativeTolerance absolute local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit AdaptiveIVPSolver(std::size_t numMaxStepAttempts = 100,
                               Real relativeTolerance = std::numeric_limits<Real>::epsilon(),
                               Real absoluteTolerance = 1e-6, std::size_t numMaxSteps = 100'000)
        : IVPSolverBaseType(relativeTolerance, absoluteTolerance, numMaxSteps),
          numMaxStepAttempts_(numMaxStepAttempts) {}

    Solution solve(const ProblemBase &problem) const override {
        std::vector<Real> stepTimes;
        std::vector<State> stepStates;
        std::vector<State> stepDerivatives;

        Real time = problem.getStartTime(), endTime = problem.getEndTime();
        State state = problem.getInitialValue(), derivative = problem(time, state);

        stepTimes.push_back(time);
        stepStates.push_back(state);
        stepDerivatives.push_back(derivative);

        Real currTolerance = std::max(this->getRelativeTolerance() * state.norm(), this->getAbsoluteTolerance());
        Real stepSize = this->getInitialStepSize(problem, currTolerance);
        Real currStepSize = stepSize;
        Real timeRoundOff = 100.0 * std::numeric_limits<Real>::epsilon() * (time + stepSize);
        std::size_t numSteps = 0;
        while ((endTime - time) > timeRoundOff and numSteps <= this->getNumMaxSteps()) {
            if ((time + stepSize - endTime) * currStepSize > 0.) {
                stepSize = (endTime - time) * (1. - 4. * std::numeric_limits<Real>::epsilon());
            }

            Real localError;
            std::size_t numStepAttempts = 0;
            std::tuple<State, State, State> result;
            do {
                currStepSize = stepSize;
                result =
                    StepProposal::proposeAdaptiveStep(problem, state, time, currStepSize, derivative, currTolerance);
                currTolerance =
                    std::max(this->getRelativeTolerance() * std::get<0>(result).norm(), this->getAbsoluteTolerance());
                localError = estimateLocalError(std::get<0>(result), std::get<1>(result));
                stepSize = adjustStepSize(localError, stepSize, currTolerance);
                ++numStepAttempts;
            } while (localError > currTolerance and numSteps <= numMaxStepAttempts_);

            if (numStepAttempts > numMaxStepAttempts_) {
                X3CFLUX_THROW(MathError, "Adaptive IVP solver: "
                                         "Maximum number of attempts for one "
                                         "solver step (here: " +
                                             std::to_string(numMaxStepAttempts_) +
                                             " reached. Increase maximum number of "
                                             "solver step attempts or relax error "
                                             "tolerances.");
            }

            time += currStepSize;
            timeRoundOff = 100.0 * std::numeric_limits<Real>::epsilon() * (time + currStepSize);
            state = std::get<0>(result);
            derivative = std::get<2>(result);
            ++numSteps;

            stepTimes.push_back(time);
            stepStates.push_back(state);
            stepDerivatives.push_back(derivative);
        }

        if (numSteps > this->getNumMaxSteps()) {
            X3CFLUX_THROW(MathError, "Adaptive IVP solver: "
                                     "Maximum number of steps (here: " +
                                         std::to_string(this->getNumMaxSteps()) +
                                         ") reached. Increase maximum number of "
                                         "solver steps or relax solver tolerances.");
        }

        stepTimes.back() = endTime;

        return {std::move(stepTimes), std::move(stepStates), std::move(stepDerivatives)};
    }

    /// \return maximum number of unaccepted steps
    std::size_t getNumMaxStepAttempts() const { return numMaxStepAttempts_; }

    /// \param numMaxStepAttempts maximum number of unaccepted steps
    void setNumMaxStepAttempts(std::size_t numMaxStepAttempts) { numMaxStepAttempts_ = numMaxStepAttempts; }

    std::unique_ptr<IVPSolverBaseType> copy() const override {
        return std::make_unique<AdaptiveIVPSolver<IVPSolverBaseType, StepProposal>>(*this);
    }

  private:
    Real getInitialStepSize(const IVPBase<State> &problem, Real tolerance) const {
        State initValue = problem.getInitialValue();
        Real endTime = problem.getEndTime();
        State derivative = problem(problem.getStartTime(), initValue);

        Real den = std::pow(1. / endTime, ADVANCE_ORDER + 1) + std::pow(initValue.norm(), ADVANCE_ORDER + 1);
        Real stepSize = std::pow(tolerance / den, 1. / (ADVANCE_ORDER + 1));

        // Mimic explicit euler step
        State nextValue = initValue + stepSize * initValue;
        den = std::pow(1. / endTime, ADVANCE_ORDER + 1) + std::pow(nextValue.norm(), ADVANCE_ORDER + 1);
        Real nextStepSize = std::pow(tolerance / den, 1. / (ADVANCE_ORDER + 1));

        return std::min(stepSize, nextStepSize);
    }

    static Real estimateLocalError(const RealVector &advState, const RealVector &corrState) {
        Real comp, err = 0.;
        Index size = advState.size();

        for (Index i = 0; i < size; ++i) {
            comp = (advState(i) - corrState(i)) / (1 + std::max(std::abs(advState(i)), std::abs(corrState(i))));

            err += comp * comp;
        }
        return std::sqrt(err / static_cast<Real>(size));
    }

    static Real estimateLocalError(const RealMatrix &advState, const RealMatrix &corrState) {
        Real compErr, err = 0.;
        Index rows = advState.rows();
        Index cols = advState.cols();

        for (Index i = 0; i < rows; ++i) {
            for (Index j = 0; j < cols; ++j) {
                compErr = (advState(i, j) - corrState(i, j)) /
                          (1 + std::max(std::abs(advState(i, j)), std::abs(corrState(i, j))));

                err += compErr * compErr;
            }
        }
        return std::sqrt(err / static_cast<Real>(cols * rows));
    }

    Real adjustStepSize(Real localErrorEstim, Real stepSize, Real tolerance) const {
        return stepSize *
               std::min(5., std::max(0.2, 0.9 * std::pow(tolerance / localErrorEstim, 1. / (ADVANCE_ORDER + 1))));
    };
};

/// \brief Adaptive IVP solver using the DOPRI54 method
/// \tparam StateType Eigen3 vector or matrix
template <typename StateType>
using DOPRI54Solver = AdaptiveIVPSolver<IVPSolver<StateType>, ERKFStepProposal<StateType, DOPRI54Scheme>>;

/// \brief Adaptive solver for linear IVP's using the SDIRK43 method
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType>
using LinearSDIRK43Solver = AdaptiveIVPSolver<LinearIVPSolver<StateType, MatrixType>,
                                              LinearSDIRKStepProposal<StateType, MatrixType, SDIRK43Scheme>>;

} // namespace x3cflux

#endif // X3CFLUX_ADAPTIVEIVPSOLVER_H
