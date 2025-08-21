#ifndef X3CFLUX_LINEARCVODESOLVER_H
#define X3CFLUX_LINEARCVODESOLVER_H

#include <cvode/cvode.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_nonlinearsolver.h>
#include <sundials/sundials_types.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sunmatrix/sunmatrix_sparse.h>
#include <sunnonlinsol/sunnonlinsol_newton.h>

#include "IVPSolver.h"
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename RhsState> class LinearCVODESolver : public LinearIVPSolver<RhsState, RealSparseMatrix> {
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::ProblemBase;
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::Solution;
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::State;

    struct UserData {
      public:
        const ProblemBase &problem;

      public:
        explicit UserData(const ProblemBase &problem) : problem(problem) {}
    };

  public:
    std::size_t numMaxStepAttempts_;

  public:
    /// Create an IVP solver based on SUNDIALS CVODE (BDF method with step size ond order control).
    /// \param numMaxStepAttempts maximum number of unaccepted steps
    /// \param relativeTolerance absolute local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit LinearCVODESolver(std::size_t numMaxStepAttempts = 100, Real relativeTolerance = 1e-6,
                               Real absoluteTolerance = 1e-9, std::size_t numMaxSteps = 100'000)
        : LinearIVPSolver<RhsState, RealSparseMatrix>(relativeTolerance, absoluteTolerance, numMaxSteps),
          numMaxStepAttempts_(numMaxStepAttempts) {}

    Solution solve(const ProblemBase &problem) const override {
        SUNContext context;
        SUNContext_Create(nullptr, &context);

        Real time = problem.getStartTime(), endTime = problem.getEndTime();
        State initialState = problem.getInitialValue(), initialDerivative = problem(time, initialState);
        N_Vector state = N_VNew_Serial(problem.getSize() * problem.getNumStates(), context),
                 derivative = N_VNew_Serial(problem.getSize() * problem.getNumStates(), context);
        convertToSerial(initialState, state);

        auto *cvodeMemory = CVodeCreate(CV_BDF, context);
        CVodeInit(cvodeMemory, LinearCVODESolver::evaluateGenericRhsFunction, problem.getStartTime(), state);

        auto userData = std::make_shared<UserData>(problem);
        CVodeSetUserData(cvodeMemory, userData.get());

        auto nonlinearSolver = createNonlinearSolver(context);
        CVodeSetNonlinearSolver(cvodeMemory, nonlinearSolver);

        CVodeSetMaxNumSteps(cvodeMemory, numMaxStepAttempts_);
        CVodeSStolerances(
            cvodeMemory, this->getRelativeTolerance(),
            this->getAbsoluteTolerance()); // TODO: Set absolute tolerances automatically with problem knowledge?

        std::vector<Real> stepTimes;
        std::vector<State> stepStates;
        std::vector<State> stepDerivatives;

        stepTimes.push_back(time);
        stepStates.push_back(initialState);
        stepDerivatives.push_back(initialDerivative);

        Real stepSize;
        CVodeGetCurrentStep(cvodeMemory, &stepSize);
        Real timeRoundOff = 100.0 * std::numeric_limits<Real>::epsilon() * (time + stepSize);
        std::size_t numSteps = 0;
        while ((endTime - time) > timeRoundOff and numSteps <= this->getNumMaxSteps()) {
            CVode(cvodeMemory, endTime, state, &time, CV_ONE_STEP);
            CVodeGetDky(cvodeMemory, time, 1, derivative);

            auto stateEigen = initializeEigen(problem.getSize(), problem.getNumStates()),
                 derivativeEigen = initializeEigen(problem.getSize(), problem.getNumStates());
            convertToEigen(state, stateEigen);
            convertToEigen(derivative, derivativeEigen);

            stepTimes.push_back(time);
            stepStates.push_back(stateEigen);
            stepDerivatives.push_back(derivativeEigen);

            CVodeGetCurrentStep(cvodeMemory, &stepSize);
            timeRoundOff = 100.0 * std::numeric_limits<Real>::epsilon() * (time + stepSize);
            ++numSteps;
        };

        if (numSteps > this->getNumMaxSteps()) {
            X3CFLUX_THROW(MathError, "BDF (SUNDIALS) IVP solver: "
                                     "Maximum number of steps (here: " +
                                         std::to_string(this->getNumMaxSteps()) +
                                         ") reached. Increase maximum number of "
                                         "solver steps or relax solver tolerances.");
        }

        N_VDestroy(state);
        N_VDestroy(derivative);
        CVodeFree(&cvodeMemory);
        SUNNonlinSolFree(nonlinearSolver);
        SUNContext_Free(&context);

        return {std::move(stepTimes), std::move(stepStates), std::move(stepDerivatives)};
    }

    /// \return maximum number of unaccepted steps
    std::size_t getNumMaxStepAttempts() const { return numMaxStepAttempts_; }

    /// \param numMaxStepAttempts maximum number of unaccepted steps
    void setNumMaxStepAttempts(std::size_t numMaxStepAttempts) { numMaxStepAttempts_ = numMaxStepAttempts; }

    std::unique_ptr<LinearIVPSolver<State, RealSparseMatrix>> copy() const override {
        return std::make_unique<LinearCVODESolver<State>>(*this);
    }

  private:
    static SUNNonlinearSolver createNonlinearSolver(SUNContext context) {
        SUNNonlinearSolver solver = SUNNonlinSolNewEmpty(context);

        // Attach operations
        solver->ops->gettype = []([[maybe_unused]] SUNNonlinearSolver solver) { return SUNNONLINEARSOLVER_ROOTFIND; };
        solver->ops->solve = []([[maybe_unused]] SUNNonlinearSolver solver, [[maybe_unused]] N_Vector y0, N_Vector yCor,
                                [[maybe_unused]] N_Vector w, [[maybe_unused]] realtype tol,
                                [[maybe_unused]] booleantype callLSetup, void *cvodeMemory) {
            realtype t, gamma, rl1;
            N_Vector yPred, yn, fn, zn1;
            void *userData;

            CVodeGetNonlinearSystemData(cvodeMemory, &t, &yPred, &yn, &fn, &gamma, &rl1, &zn1, &userData);
            const auto &problem = ((UserData *)userData)->problem;
            auto zn1Eigen = initializeEigen(problem.getSize(), problem.getNumStates()),
                 yPredEigen = initializeEigen(problem.getSize(), problem.getNumStates());
            convertToEigen(zn1, zn1Eigen);
            convertToEigen(yPred, yPredEigen);

            RealSparseMatrix identity(problem.getSize(), problem.getSize());
            identity.setIdentity();
            auto supportMatrix = identity - gamma * problem.getJacobiMatrix();
            auto rhs = (gamma * problem(t, yPredEigen) - rl1 * zn1Eigen).eval();
            auto yCorEigen = Eigen::SparseLU<RealSparseMatrix>(supportMatrix).solve(rhs).eval();
            convertToSerial(yCorEigen, yCor);

            return SUN_NLS_SUCCESS;
        };
        solver->ops->setsysfn = []([[maybe_unused]] SUNNonlinearSolver solver,
                                   [[maybe_unused]] SUNNonlinSolSysFn sysFunction) { return 0; };

        return solver;
    }

    static void convertToSerial(const RealVector &state, N_Vector copyState) {
        for (Index i = 0; i < state.size(); ++i) {
            NV_Ith_S(copyState, i) = state[i];
        }
    }

    static void convertToSerial(const RealMatrix &state, N_Vector copyState) {
        for (Index i = 0; i < state.rows(); ++i) {
            for (Index j = 0; j < state.cols(); ++j) {
                NV_Ith_S(copyState, i * state.cols() + j) = state(i, j);
            }
        }
    }

    static void convertToEigen(N_Vector state, RealVector &copyState) {
        Index size = NV_LENGTH_S(state);
        for (Index i = 0; i < size; ++i) {
            copyState[i] = NV_Ith_S(state, i);
        }
    }

    static void convertToEigen(N_Vector state, RealMatrix &copyState) {
        for (Index i = 0; i < copyState.rows(); ++i) {
            for (Index j = 0; j < copyState.cols(); ++j) {
                copyState(i, j) = NV_Ith_S(state, i * copyState.cols() + j);
            }
        }
    }

    static State initializeEigen(Index rows, Index cols) {
        if constexpr (State::ColsAtCompileTime == 1) {
            return State(rows);
        } else {
            return State(rows, cols);
        }
    }

    static int evaluateGenericRhsFunction(realtype time, N_Vector state, N_Vector stateDerivative, void *userData) {
        const auto &problem = reinterpret_cast<UserData *>(userData)->problem;
        auto stateEigen = initializeEigen(problem.getSize(), problem.getNumStates());
        convertToEigen(state, stateEigen);

        auto result = problem(time, stateEigen);

        convertToSerial(result, stateDerivative);
        return 0;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_LINEARCVODESOLVER_H
