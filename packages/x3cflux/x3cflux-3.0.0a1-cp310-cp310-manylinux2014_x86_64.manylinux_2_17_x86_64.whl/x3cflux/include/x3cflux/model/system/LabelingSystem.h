#ifndef X3CFLUX_LABELINGSYSTEM_H
#define X3CFLUX_LABELINGSYSTEM_H

#include "SystemTraits.h"
#include <math/IVPSolver.h>
#include <math/LESSolver.h>

namespace x3cflux {

/// Base class for labeling systems
///
/// \tparam Method labeling state modeling method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
///
/// Labeling systems are created from a vector of parameters using a SystemBuilder.
template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<not(Stationary and SystemTraits<Method, Multi>::TYPE == SystemType::NONLINEAR), bool> = true>
class LabelingSystem {
  public:
    typedef SystemTraits<Method, Multi> Traits;
    typedef typename Traits::FractionType Fraction;
    typedef typename Traits::SystemStateType SystemState;

    typedef std::conditional_t<
        Stationary, std::vector<SystemState>,
        std::conditional_t<Traits::TYPE == SystemType::CASCADED, std::vector<typename IVPSolver<SystemState>::Solution>,
                           typename IVPSolver<SystemState>::Solution>>
        Solution;

    typedef std::conditional_t<
        Stationary, LESSolver<RealSparseMatrix, SystemState>,
        std::conditional_t<Traits::TYPE == SystemType::CASCADED, LinearIVPSolver<SystemState, RealSparseMatrix>,
                           IVPSolver<SystemState>>>
        Solver;

  private:
    std::unique_ptr<Solver> solver_;

  public:
    /// Create labeling system
    /// \param solver labeling system solver
    explicit LabelingSystem(const Solver &solver) : solver_(solver.copy()) {}

    virtual ~LabelingSystem() = default;

    /// \return labeling system solver
    const Solver &getSolver() const { return *solver_; }

    /// Solves labeling system using the configured solver
    /// \return labeling system solution
    virtual Solution solve() const = 0;
};

} // namespace x3cflux

#endif // X3CFLUX_LABELINGSYSTEM_H
