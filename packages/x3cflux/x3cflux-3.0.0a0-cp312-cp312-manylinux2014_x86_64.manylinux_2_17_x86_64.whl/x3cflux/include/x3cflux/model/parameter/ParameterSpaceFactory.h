#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEFACTORY_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEFACTORY_H

#include <unordered_map>

#include "ParameterError.h"
#include "ParameterSpace.h"

#include <math/LESSolver.h>
#include <model/data/NetworkData.h>
#include <model/data/ParameterConstraints.h>
#include <model/data/Substrate.h>

namespace x3cflux {

/// \brief Factory for building instances of ParameterSpace
///
/// A ParameterSpace instance represents a polytope subset from the space
/// of free metabolic parameters. This requires to construct stoichiometric
/// matrix, solve equality constraint systems and transform inequality constraint
/// system into an only free parameter-dependent form. This factory computes the
/// components and constructs a ParameterSpace instance from the results.
///
/// The solution space of the equality constraints given by the user
/// can be expressed as \f$\mathbf{C}_{eq} \cdot \mathbf{\theta} = \mathbf{0}\f$.
/// Hereby, \f$\mathbf{\theta}\f$ refers to either net/xch fluxes or pool sizes.
/// The system is solved in a way that there are parameters \f$\mathbf{\theta}_f\f$
/// which can be chosen freely. A representation of the solution space is the
/// particular solution \f$\mathbf{p}\f$ and the matrix \f$\mathbf{K}\f$ that maps
/// the free parameter space to the kernel space of the constraint matrix.
/// All parameters that fulfill the constraints can than be calculate by
/// \f$\mathbf{\theta} = \mathbf{p} + \mathbf{K} \cdot \mathbf{\theta}_f\f$.
///
/// With this, inequality systems \f$\mathbf{C}_{ineq} \cdot \mathbf{\theta} \le \mathbf{d}\f$
/// are transformed to free parameter space.
class ParameterSpaceFactory {
  public:
    /// \brief Factory method that creates a ParameterSpace instance.
    /// \param networkData reactions and metabolites of the metabolic model
    /// \param inputSubstrates input substrates of metabolic model
    /// \param netFluxConstraints user-supplied net flux constraints
    /// \param exchangeFluxConstraints user-supplied exchange flux constraints
    /// \param poolSizeConstraints user-supplied pool size constraints
    /// \param freeNetFluxSelection indicates free net fluxes
    /// \param freeExchangeFluxSelection indicates free exchange fluxes
    /// \param freePoolSizeSelection indicates free pool sizes
    /// \return a ParameterSpace instance
    /// \throw ParameterError if ParameterSpace build fails
    static ParameterSpace create(const std::vector<Metabolite> &innerMetabolites,
                                 const std::vector<Reaction> &reactions, const ParameterConstraints &netFluxConstraints,
                                 const ParameterConstraints &exchangeFluxConstraints,
                                 const ParameterConstraints &poolSizeConstraints,
                                 const boost::dynamic_bitset<> &freeNetFluxSelection = boost::dynamic_bitset<>(),
                                 const boost::dynamic_bitset<> &freeExchangeFluxSelection = boost::dynamic_bitset<>(),
                                 const boost::dynamic_bitset<> &freePoolSizeSelection = boost::dynamic_bitset<>());

    static ParameterConstraints
    removeParametersFromConstraints(const ParameterConstraints &constraints,
                                    const std::unordered_map<std::string, std::size_t> &parameterIndices);

    static boost::dynamic_bitset<>
    removeParametersFromFreeParameterSelection(const boost::dynamic_bitset<> &freeParameterSelection,
                                               const std::vector<Index> &parametersToRemove);

    static Stoichiometry buildStoichiometry(const std::vector<Metabolite> &metabolites,
                                            const std::vector<Reaction> &reactions);

    static LinearEquationSystem<RealMatrix, RealVector>
    buildEqualityConstraintSystem(std::size_t numParams, const std::vector<LinearConstraint> &equalityConstraints,
                                  const std::unordered_map<std::string, std::size_t> &paramIndices);

    static SolutionSpace computeSolutionSpace(const RealMatrix &constraintMatrix, const RealVector &constraintVector,
                                              const boost::dynamic_bitset<> &freeParamSelection);

    static ParameterClassification
    buildParameterClassification(std::size_t numParams, const std::vector<std::string> &paramNames,
                                 const SolutionSpace &paramSolutionSpace,
                                 const boost::dynamic_bitset<> &constrParamSelection,
                                 const std::unordered_map<std::string, Real> &constrParamValues,
                                 const std::vector<LinearConstraint> &inequalityConstraints);

    static std::tuple<SolutionSpace, SolutionSpace, SolutionSpace, ParameterClassification, ParameterClassification,
                      ParameterClassification>
    prepareParameters(
        const Stoichiometry &stoichiometry, const std::unordered_map<std::string, std::size_t> &reactionIndices,
        const std::unordered_map<std::string, std::size_t> &metaboliteIndices,
        const ParameterConstraints &netFluxConstraints, const ParameterConstraints &exchangeFluxConstraints,
        const ParameterConstraints &poolSizeConstraints, const boost::dynamic_bitset<> &freeNetFluxSelection,
        const boost::dynamic_bitset<> &freeExchangeFluxSelection, const boost::dynamic_bitset<> &freePoolSizeSelection);

    static std::pair<std::vector<Index>, std::vector<Index>>
    findInactiveFluxesAndUnreachablePools(const Stoichiometry &stoichiometry,
                                          const ParameterClassification &netFluxClassification,
                                          const ParameterClassification &exchangeFluxClassification,
                                          const ParameterClassification &poolSizeClassification);

    static InequalitySystem
    buildInequalityConstraintSystem(const std::vector<LinearConstraint> &inequalityConstraints,
                                    const SolutionSpace &paramSolutionSpace,
                                    const std::unordered_map<std::string, Real> &constrParams,
                                    const std::unordered_map<std::string, std::size_t> &paramIndices);
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEFACTORY_H