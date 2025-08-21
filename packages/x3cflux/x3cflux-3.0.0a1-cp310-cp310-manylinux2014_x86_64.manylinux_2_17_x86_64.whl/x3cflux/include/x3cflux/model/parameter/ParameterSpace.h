#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACE_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACE_H

#include <utility>

#include "InequalitySystem.h"
#include "ParameterClassification.h"
#include "SolutionSpace.h"
#include "Stoichiometry.h"
#include <util/Logging.h>

namespace x3cflux {

/// \brief Parameter space of metabolic stationary models
///
/// A ParameterSpace instance holds information that determine the space of
/// possible parameter configurations. It has a certain structure given by
/// the stoichiometric constraints and user equality constraints
/// \f$\mathbf{C}_{eq} \cdot \mathbf{\theta} = \mathbf{0}\f$ which divide
/// the parameters into free and dependent parameters. Using the user-supplied
/// inequality constraints \f$\mathbf{C}_{ineq} \cdot \mathbf{\theta} \le \mathbf{d}\f$,
/// the space becomes a convex polytope.
class ParameterSpace {
  protected:
    Stoichiometry stoichiometry_;
    SolutionSpace netFluxSolutionSpace_;
    SolutionSpace exchangeFluxSolutionSpace_;
    SolutionSpace poolSizeSolutionSpace_;
    ParameterClassification netFluxClassification_;
    ParameterClassification exchangeFluxClassification_;
    ParameterClassification poolSizeClassification_;
    InequalitySystem netFluxInequalitySystem_;
    InequalitySystem exchangeFluxInequalitySystem_;
    InequalitySystem poolSizeInequalitySystem_;

  public:
    /// \brief Create a parameter space.
    /// \param stoichiometry stoichiometry of the metabolic model
    /// \param netFluxSolutionSpace solution space of net flux equality constraints
    /// \param exchangeFluxSolutionSpace solution space of exchange flux equality constraints
    /// \param poolSizeSolutionSpace solution space of pool size equality constraints
    /// \param netFluxClassification classification of net flux parameters
    /// \param exchangeFluxClassification classification of exchange flux parameters
    /// \param poolSizeClassification classification of pool size parameters
    /// \param netFluxInequalitySystem net flux inequality constraints
    /// \param exchangeFluxInequalitySystem exchange flux inequality constraints
    /// \param poolSizeInequalitySystem pool size inequality constraints
    ParameterSpace(Stoichiometry stoichiometry, SolutionSpace netFluxSolutionSpace,
                   SolutionSpace exchangeFluxSolutionSpace, SolutionSpace poolSizeSolutionSpace,
                   ParameterClassification netFluxClassification, ParameterClassification exchangeFluxClassification,
                   ParameterClassification poolSizeClassification, InequalitySystem netFluxInequalitySystem,
                   InequalitySystem exchangeFluxInequalitySystem, InequalitySystem poolSizeInequalitySystem)
        : stoichiometry_(std::move(stoichiometry)), netFluxSolutionSpace_(std::move(netFluxSolutionSpace)),
          exchangeFluxSolutionSpace_(std::move(exchangeFluxSolutionSpace)),
          poolSizeSolutionSpace_(std::move(poolSizeSolutionSpace)),
          netFluxClassification_(std::move(netFluxClassification)),
          exchangeFluxClassification_(std::move(exchangeFluxClassification)),
          poolSizeClassification_(std::move(poolSizeClassification)),
          netFluxInequalitySystem_(std::move(netFluxInequalitySystem)),
          exchangeFluxInequalitySystem_(std::move(exchangeFluxInequalitySystem)),
          poolSizeInequalitySystem_(std::move(poolSizeInequalitySystem)) {}

    /// \return stoichiometry of the metabolic model
    const Stoichiometry &getStoichiometry() const { return stoichiometry_; }

    /// \return solution space of net flux equality constraints
    const SolutionSpace &getNetFluxSolutionSpace() const { return netFluxSolutionSpace_; }

    /// \return solution space of exchange flux equality constraints
    const SolutionSpace &getExchangeFluxSolutionSpace() const { return exchangeFluxSolutionSpace_; }

    /// \return solution space of pool size equality constraints
    const SolutionSpace &getPoolSizeSolutionSpace() const { return poolSizeSolutionSpace_; }

    /// \return classification of net flux parameters
    const ParameterClassification &getNetFluxClassification() const { return netFluxClassification_; }

    /// \return classification of exchange flux parameters
    const ParameterClassification &getExchangeFluxClassification() const { return exchangeFluxClassification_; }

    /// \return classification of pool size parameters
    const ParameterClassification &getPoolSizeClassification() const { return poolSizeClassification_; }

    /// \return net flux inequality constraints
    const InequalitySystem &getNetFluxInequalitySystem() const { return netFluxInequalitySystem_; }

    /// \return exchange flux inequality constraints
    const InequalitySystem &getExchangeFluxInequalitySystem() const { return exchangeFluxInequalitySystem_; }

    /// \return pool size inequality constraints
    const InequalitySystem &getPoolSizeInequalitySystem() const { return poolSizeInequalitySystem_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACE_H