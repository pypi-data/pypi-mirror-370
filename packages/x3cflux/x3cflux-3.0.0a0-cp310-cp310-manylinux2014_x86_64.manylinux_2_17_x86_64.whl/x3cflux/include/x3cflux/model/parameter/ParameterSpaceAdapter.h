#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H

#include "ParameterSpace.h"

namespace x3cflux {

class ParameterSpaceAdapterBase : public ParameterSpace {
  private:
    Real constraintViolationTolerance_;

  public:
    explicit ParameterSpaceAdapterBase(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.)
        : ParameterSpace(std::move(parameterSpace)), constraintViolationTolerance_(constraintViolationTolerance) {}

    /// \return Absolute tolerance of inequality constraint violation
    Real getConstraintViolationTolerance() const { return constraintViolationTolerance_; }

    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    void setConstraintViolationTolerance(Real constraintViolationTolerance) {
        constraintViolationTolerance_ = constraintViolationTolerance;
    }

    static boost::dynamic_bitset<> buildFreeParameterMask(std::size_t numParams,
                                                          const ParameterClassification &paramClass,
                                                          const SolutionSpace &paramSolutionSpace) {
        boost::dynamic_bitset<> freeParamMask(
            paramClass.getNumFreeParameters() + paramClass.getNumConstraintParameters(), false);

        const auto &constrParams = paramClass.getConstraintParameters();
        std::unordered_map<Index, Real> paramLookUp(constrParams.begin(), constrParams.end());

        auto origOrder = paramSolutionSpace.getPermutation().indices();
        for (std::size_t permOrderInd = paramClass.getNumDependentParameters(); permOrderInd < numParams;
             ++permOrderInd) {
            Index origOrderInd = origOrder(static_cast<Index>(permOrderInd));

            if (paramLookUp.find(origOrderInd) == paramLookUp.end()) {
                freeParamMask.set(permOrderInd - paramClass.getNumDependentParameters());
            }
        }

        return freeParamMask;
    }

    static RealVector buildFullParameterVector(const RealVector &freeParameters,
                                               const boost::dynamic_bitset<> &freeParamMask,
                                               const ParameterClassification &paramClass,
                                               const SolutionSpace &paramSolutionSpace) {
        std::size_t numNonDepParams = paramClass.getNumFreeParameters() + paramClass.getNumConstraintParameters();
        const auto &constrParams = paramClass.getConstraintParameters();

        Index freeParamInd = 0, constrParamInd = 0;
        RealVector nonDepParams(numNonDepParams);
        for (Index paramInd = 0; paramInd < nonDepParams.size(); ++paramInd) {
            if (freeParamMask[paramInd]) {
                nonDepParams(paramInd) = freeParameters(freeParamInd++);
            } else {
                nonDepParams(paramInd) = constrParams[constrParamInd++].second;
            }
        }

        return paramSolutionSpace.getParticularSolution() + paramSolutionSpace.getKernelBasis() * nonDepParams;
    }

    static RealVector buildFullParameterDerivativeVector(std::size_t freeParameterIndex,
                                                         const boost::dynamic_bitset<> &freeParamMask,
                                                         const SolutionSpace &paramSolutionSpace) {
        std::size_t nonDepParamIndex = freeParamMask.find_first();
        for (std::size_t incrInd = 1; incrInd <= freeParameterIndex; ++incrInd) {
            nonDepParamIndex = freeParamMask.find_next(nonDepParamIndex);
        }

        return paramSolutionSpace.getKernelBasis().col(static_cast<Index>(nonDepParamIndex));
    }
};

/// \brief Base class for ParameterSpace adapter
/// \tparam IsStationary stationary or non-stationary
///
/// Metabolic stationary parameter spaces are different for
/// isotopically stationary or isotopically non-stationary models.
/// The first class has no pool size parameters, the second has
/// them. Thus, the dimension of the vector space of which the
/// parameter space is a subset of differs as well as generell
/// inequality constraint system.
template <bool IsStationary> class ParameterSpaceAdapter;

/// \brief Adapter for isotopically stationary metabolic model
template <> class ParameterSpaceAdapter<true> : public ParameterSpaceAdapterBase {
  private:
    boost::dynamic_bitset<> freeNetFluxMask_;
    boost::dynamic_bitset<> freeExchangeFluxMask_;

  public:
    /// \brief Create adapter for stationary metabolic parameter space.
    /// \param parameterSpace Metabolic model information
    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    explicit ParameterSpaceAdapter(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.)
        : ParameterSpaceAdapterBase(std::move(parameterSpace), constraintViolationTolerance) {
        const auto &stoichiometry = this->getStoichiometry();

        freeNetFluxMask_ = ParameterSpaceAdapterBase::buildFreeParameterMask(
            stoichiometry.getNumReactions(), this->getNetFluxClassification(), this->getNetFluxSolutionSpace());

        freeExchangeFluxMask_ = ParameterSpaceAdapterBase::buildFreeParameterMask(stoichiometry.getNumReactions(),
                                                                                  this->getExchangeFluxClassification(),
                                                                                  this->getExchangeFluxSolutionSpace());
    }

    /// \return number of free stationary metabolic parameter
    Index getNumFreeParameters() const {
        const auto &netClass = this->getNetFluxClassification();
        const auto &xchClass = this->getExchangeFluxClassification();

        return static_cast<Index>(netClass.getNumFreeParameters() + xchClass.getNumFreeParameters());
    }

    /// \return number of stationary metabolic parameters
    Index getNumParameters() const {
        const auto &stoichiometry = this->getStoichiometry();
        return 2 * stoichiometry.getNumReactions();
    }

    /// \return names of free stationary parameters
    std::vector<std::string> getFreeParameterNames() const {
        std::vector<std::string> paramNames;

        const auto &netNames = this->getNetFluxClassification().getParameterNames();
        const auto &netIndices = this->getNetFluxClassification().getFreeParameters();
        for (auto index : netIndices) {
            paramNames.push_back(netNames[index] + ".n");
        }

        const auto &xchNames = this->getExchangeFluxClassification().getParameterNames();
        const auto &xchIndices = this->getExchangeFluxClassification().getFreeParameters();
        for (auto index : xchIndices) {
            paramNames.push_back(xchNames[index] + ".x");
        }

        return paramNames;
    }

    /// \return names of all stationary parameters
    std::vector<std::string> getParameterNames() const {
        std::vector<std::string> paramNames;

        const auto &netParamNames = this->getNetFluxClassification().getParameterNames();
        for (const auto &paramName : netParamNames) {
            paramNames.push_back(paramName + ".n");
        }

        const auto &xchParamNames = this->getExchangeFluxClassification().getParameterNames();
        for (const auto &paramName : xchParamNames) {
            paramNames.push_back(paramName + ".x");
        }

        return paramNames;
    }

    /// \return inequality constraints of free stationary metabolic parameters
    InequalitySystem getInequalitySystem() const {
        const auto &netIneqSystem = this->getNetFluxInequalitySystem();
        auto numFreeNetFluxes = static_cast<Index>(this->getNetFluxClassification().getNumFreeParameters());
        Index numNetFluxIneqs = netIneqSystem.getNumInequalities();

        const auto &xchIneqSystem = this->getExchangeFluxInequalitySystem();
        auto numFreeXchFluxes = static_cast<Index>(this->getExchangeFluxClassification().getNumFreeParameters());
        Index numXchFluxIneqs = xchIneqSystem.getNumInequalities();

        Index numParams = numFreeNetFluxes + numFreeXchFluxes;
        Index numIneqs = numNetFluxIneqs + numXchFluxIneqs;

        RealMatrix fullMatrix = RealMatrix::Zero(numIneqs, numParams);
        RealVector fullBound = RealVector::Zero(numIneqs);

        fullMatrix.topLeftCorner(numNetFluxIneqs, numFreeNetFluxes) = netIneqSystem.getMatrix();
        fullBound.head(numNetFluxIneqs) = netIneqSystem.getBound();

        fullMatrix.bottomRightCorner(numXchFluxIneqs, numFreeXchFluxes) = xchIneqSystem.getMatrix();
        fullBound.tail(numXchFluxIneqs) = xchIneqSystem.getBound();

        return {fullMatrix, fullBound};
    }

    /// \brief Check if free parameters fulfill inequality constraints.
    /// \param freeParameters free parameter space vector
    /// \return fulfilled or not
    bool contains(const RealVector &freeParameters) const {
        X3CFLUX_CHECK(freeParameters.size() == getNumFreeParameters());
        auto ineqSystem = getInequalitySystem();
        return ((ineqSystem.getMatrix() * freeParameters).array() <=
                ineqSystem.getBound().array() + this->getConstraintViolationTolerance())
            .all();
    }

    /// \brief Compute all parameters from a vector of free parameters.
    /// \param freeParameters free parameter space vector
    /// \return vector of stationary metabolic parameters
    RealVector computeParameters(const RealVector &freeParameters) const {
        X3CFLUX_CHECK(contains(freeParameters));

        RealVector parameters(getNumParameters());

        const auto &stoichiometry = this->getStoichiometry();
        Index numReactions = stoichiometry.getNumReactions();

        parameters.head(numReactions) = ParameterSpaceAdapterBase::buildFullParameterVector(
            freeParameters.head(static_cast<Index>(freeNetFluxMask_.count())), freeNetFluxMask_,
            this->getNetFluxClassification(), this->getNetFluxSolutionSpace());

        parameters.tail(numReactions) = ParameterSpaceAdapterBase::buildFullParameterVector(
            freeParameters.tail(static_cast<Index>(freeExchangeFluxMask_.count())), freeExchangeFluxMask_,
            this->getExchangeFluxClassification(), this->getExchangeFluxSolutionSpace());

        return parameters;
    }

    /// \brief Compute derivatives of all parameters with respect to a free parameter.
    /// \param freeParameterIndex index of free parameter to derive for
    /// \return vector of stationary metabolic parameter derivatives
    RealVector computeParameterDerivatives(Index freeParameterIndex) const {
        X3CFLUX_CHECK(freeParameterIndex < getNumFreeParameters());

        RealVector parameters = RealVector::Zero(getNumParameters());

        const auto &stoichiometry = this->getStoichiometry();
        Index numReactions = stoichiometry.getNumReactions();
        auto numFreeNetFluxes = static_cast<Index>(this->getNetFluxClassification().getNumFreeParameters());

        if (freeParameterIndex < numFreeNetFluxes) {
            parameters.head(numReactions) = ParameterSpaceAdapterBase::buildFullParameterDerivativeVector(
                freeParameterIndex, freeNetFluxMask_, this->getNetFluxSolutionSpace());
        } else {
            parameters.tail(numReactions) = ParameterSpaceAdapterBase::buildFullParameterDerivativeVector(
                freeParameterIndex - numFreeNetFluxes, freeExchangeFluxMask_, this->getExchangeFluxSolutionSpace());
        }

        return parameters;
    }

    /// Calculates \f$\mathbf{S} \cdot \mathbf{\theta_{net}}$\f where \f$\mathbf{S}$\f
    /// is the stoichiometric matrix and \f$\mathbf{\theta}_{net}$\f the net
    /// flux parameters. The produc is expected to be \f$\mathbf{0}$\f. The \f$L^2$\f
    /// norm of the result vector is thus equal to the error of the stoichiometric equations.
    ///
    /// \brief Calculate L2 error of stoichiometric equations.
    /// \param parameters vector of all stationary metabolic parameters
    /// \return L2 error
    Real computeStoichiometryError(const RealVector &parameters) const {
        X3CFLUX_CHECK(parameters.size() == getNumParameters());
        const auto &stoichiometry = this->getStoichiometry();
        return (stoichiometry.getStoichiometricMatrix().template cast<Real>() *
                parameters.head(stoichiometry.getNumReactions()))
            .norm();
    }

    /// \brief Checks if L2 error of stoichiometric equation is small enough.
    /// \param parameters vector of all stationary metabolic parameters
    /// \param precision error tolerance (default: machine epsilon)
    /// \return L2 error small enough or not
    bool isFeasible(const RealVector &parameters, Real precision = std::numeric_limits<Real>::epsilon()) const {
        return computeStoichiometryError(parameters) < precision;
    }
};

typedef ParameterSpaceAdapter<true> StationaryParameterSpace;

/// \brief Adapter for isotopically non-stationary metabolic model
template <> class ParameterSpaceAdapter<false> : public ParameterSpaceAdapterBase {
  private:
    boost::dynamic_bitset<> freeNetFluxMask_;
    boost::dynamic_bitset<> freeExchangeFluxMask_;
    boost::dynamic_bitset<> freePoolSizeMask_;

  public:
    /// \brief Create adapter for non-stationary metabolic parameter space.
    /// \param parameterSpace Metabolic model information
    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    explicit ParameterSpaceAdapter(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.)
        : ParameterSpaceAdapterBase(std::move(parameterSpace), constraintViolationTolerance) {
        const auto &stoichiometry = this->getStoichiometry();

        freeNetFluxMask_ = ParameterSpaceAdapterBase::buildFreeParameterMask(
            stoichiometry.getNumReactions(), this->getNetFluxClassification(), this->getNetFluxSolutionSpace());

        freeExchangeFluxMask_ = ParameterSpaceAdapterBase::buildFreeParameterMask(stoichiometry.getNumReactions(),
                                                                                  this->getExchangeFluxClassification(),
                                                                                  this->getExchangeFluxSolutionSpace());

        freePoolSizeMask_ = ParameterSpaceAdapterBase::buildFreeParameterMask(
            stoichiometry.getNumMetabolites(), this->getPoolSizeClassification(), this->getPoolSizeSolutionSpace());
    }

    /// \return number of free non-stationary metabolic parameters
    Index getNumFreeParameters() const {
        const auto &netClass = this->getNetFluxClassification();
        const auto &xchClass = this->getExchangeFluxClassification();
        const auto &poolClass = this->getPoolSizeClassification();

        return static_cast<Index>(netClass.getNumFreeParameters() + xchClass.getNumFreeParameters() +
                                  poolClass.getNumFreeParameters());
    }

    /// \return number of non-stationary metabolic parameters
    Index getNumParameters() const {
        const auto &stoichiometry = this->getStoichiometry();
        return 2 * stoichiometry.getNumReactions() + stoichiometry.getNumMetabolites();
    }

    /// \return names of free non-stationary metabolic parameters
    std::vector<std::string> getFreeParameterNames() const {
        std::vector<std::string> paramNames;

        const auto &netNames = this->getNetFluxClassification().getParameterNames();
        const auto &netIndices = this->getNetFluxClassification().getFreeParameters();
        for (auto index : netIndices) {
            paramNames.push_back(netNames[index] + ".n");
        }

        const auto &xchNames = this->getExchangeFluxClassification().getParameterNames();
        const auto &xchIndices = this->getExchangeFluxClassification().getFreeParameters();
        for (auto index : xchIndices) {
            paramNames.push_back(xchNames[index] + ".x");
        }

        const auto &poolNames = this->getPoolSizeClassification().getParameterNames();
        const auto &poolIndices = this->getPoolSizeClassification().getFreeParameters();
        for (auto index : poolIndices) {
            paramNames.push_back(poolNames[index]);
        }

        return paramNames;
    }

    /// \return names of all non-stationary metabolic parameters
    std::vector<std::string> getParameterNames() const {
        std::vector<std::string> paramNames;

        const auto &netParamNames = this->getNetFluxClassification().getParameterNames();
        for (const auto &paramName : netParamNames) {
            paramNames.push_back(paramName + ".n");
        }

        const auto &xchParamNames = this->getExchangeFluxClassification().getParameterNames();
        for (const auto &paramName : xchParamNames) {
            paramNames.push_back(paramName + ".x");
        }

        const auto &poolParamNames = this->getPoolSizeClassification().getParameterNames();
        paramNames.insert(paramNames.end(), poolParamNames.begin(), poolParamNames.end());

        return paramNames;
    }

    /// \return inequality constraints of free non-stationary metabolic parameters
    InequalitySystem getInequalitySystem() const {
        const auto &netIneqSystem = this->getNetFluxInequalitySystem();
        auto numFreeNetFluxes = static_cast<Index>(this->getNetFluxClassification().getNumFreeParameters());
        Index numNetFluxIneqs = netIneqSystem.getNumInequalities();

        const auto &xchIneqSystem = this->getExchangeFluxInequalitySystem();
        auto numFreeXchFluxes = static_cast<Index>(this->getExchangeFluxClassification().getNumFreeParameters());
        Index numXchFluxIneqs = xchIneqSystem.getNumInequalities();

        const auto &poolIneqSystem = this->getPoolSizeInequalitySystem();
        auto numFreePoolSizes = static_cast<Index>(this->getPoolSizeClassification().getNumFreeParameters());
        Index numPoolSizeIneqs = poolIneqSystem.getNumInequalities();

        Index numParams = numFreeNetFluxes + numFreeXchFluxes + numFreePoolSizes;
        Index numIneqs = numNetFluxIneqs + numXchFluxIneqs + numPoolSizeIneqs;

        RealMatrix fullMatrix = RealMatrix::Zero(numIneqs, numParams);
        RealVector fullBound = RealVector::Zero(numIneqs);

        fullMatrix.topLeftCorner(numNetFluxIneqs, numFreeNetFluxes) = netIneqSystem.getMatrix();
        fullBound.head(numNetFluxIneqs) = netIneqSystem.getBound();

        fullMatrix.block(numNetFluxIneqs, numFreeNetFluxes, numXchFluxIneqs, numFreeXchFluxes) =
            xchIneqSystem.getMatrix();
        fullBound.segment(numNetFluxIneqs, numXchFluxIneqs) = xchIneqSystem.getBound();

        fullMatrix.bottomRightCorner(numPoolSizeIneqs, numFreePoolSizes) = poolIneqSystem.getMatrix();
        fullBound.tail(numPoolSizeIneqs) = poolIneqSystem.getBound();

        return {fullMatrix, fullBound};
    }

    /// \brief Check if free parameters fulfill inequality constraints.
    /// \param freeParameters free parameter space vector
    /// \return fulfilled or not
    bool contains(const RealVector &freeParameters) const {
        X3CFLUX_CHECK(freeParameters.size() == getNumFreeParameters());
        auto ineqSystem = getInequalitySystem();
        return ((ineqSystem.getMatrix() * freeParameters).array() <=
                ineqSystem.getBound().array() + this->getConstraintViolationTolerance())
            .all();
    }

    /// \brief Calculate all parameters from a vector of free parameters.
    /// \param freeParameters free parameter space vector
    /// \return vector of non-stationary metabolic parameters
    RealVector computeParameters(const RealVector &freeParameters) const {
        X3CFLUX_CHECK(contains(freeParameters));

        RealVector parameters(getNumParameters());

        const auto &stoichiometry = this->getStoichiometry();
        Index numReactions = stoichiometry.getNumReactions(), numMetabolites = stoichiometry.getNumMetabolites();

        parameters.head(numReactions) = ParameterSpaceAdapterBase::buildFullParameterVector(
            freeParameters.head(static_cast<Index>(freeNetFluxMask_.count())), freeNetFluxMask_,
            this->getNetFluxClassification(), this->getNetFluxSolutionSpace());

        parameters.segment(numReactions, numReactions) = ParameterSpaceAdapterBase::buildFullParameterVector(
            freeParameters.segment(static_cast<Index>(freeNetFluxMask_.count()),
                                   static_cast<Index>(freeExchangeFluxMask_.count())),
            freeExchangeFluxMask_, this->getExchangeFluxClassification(), this->getExchangeFluxSolutionSpace());

        parameters.tail(numMetabolites) = ParameterSpaceAdapterBase::buildFullParameterVector(
            freeParameters.tail(static_cast<Index>(freePoolSizeMask_.count())), freePoolSizeMask_,
            this->getPoolSizeClassification(), this->getPoolSizeSolutionSpace());

        return parameters;
    }

    /// \brief Compute derivatives of all parameters with respect to a free parameter.
    /// \param freeParameterIndex index of free parameter to derive for
    /// \return vector of non-stationary metabolic parameter derivatives
    RealVector computeParameterDerivatives(Index freeParameterIndex) const {
        X3CFLUX_CHECK(freeParameterIndex < getNumFreeParameters());

        RealVector parameters = RealVector::Zero(getNumParameters());

        const auto &stoichiometry = this->getStoichiometry();
        Index numReactions = stoichiometry.getNumReactions(), numMetabolites = stoichiometry.getNumMetabolites();
        auto numFreeNetFluxes = static_cast<Index>(this->getNetFluxClassification().getNumFreeParameters()),
             numFreeXchFluxes = static_cast<Index>(this->getExchangeFluxClassification().getNumFreeParameters());

        if (freeParameterIndex < numFreeNetFluxes) {
            parameters.head(numReactions) = ParameterSpaceAdapterBase::buildFullParameterDerivativeVector(
                freeParameterIndex, freeNetFluxMask_, this->getNetFluxSolutionSpace());

            return parameters;
        } else if (freeParameterIndex < numFreeNetFluxes + numFreeXchFluxes) {
            parameters.segment(numReactions, numReactions) =
                ParameterSpaceAdapterBase::buildFullParameterDerivativeVector(
                    freeParameterIndex - numFreeNetFluxes, freeExchangeFluxMask_, this->getExchangeFluxSolutionSpace());
        } else {
            parameters.tail(numMetabolites) = ParameterSpaceAdapterBase::buildFullParameterDerivativeVector(
                freeParameterIndex - (numFreeNetFluxes + numFreeXchFluxes), freePoolSizeMask_,
                this->getPoolSizeSolutionSpace());
        }

        return parameters;
    }

    /// Calculates \f$\mathbf{S} \cdot \mathbf{\theta_{net}}$\f where \f$\mathbf{S}$\f
    /// is the stoichiometric matrix and \f$\mathbf{\theta}_{net}$\f the net
    /// flux parameters. The produc is expected to be \f$\mathbf{0}$\f. The \f$L^2$\f
    /// norm of the result vector is thus equal to the error of the stoichiometric equations.
    ///
    /// \brief Calculate L2 error of stoichiometric equations.
    /// \param parameters vector of all non-stationary metabolic parameters
    /// \return L2 error
    Real computeStoichiometryError(const RealVector &parameters) const {
        X3CFLUX_CHECK(parameters.size() == getNumParameters());
        const auto &stoichiometry = this->getStoichiometry();
        return (stoichiometry.getStoichiometricMatrix().template cast<Real>() *
                parameters.head(stoichiometry.getNumReactions()))
            .norm();
    }

    /// \brief Checks if L2 error of stoichiometric equation is small enough.
    /// \param parameters vector of all non-stationary metabolic parameters
    /// \param precision error tolerance (default: machine epsilon)
    /// \return L2 error small enough or not
    bool isFeasible(const RealVector &parameters, Real precision = std::numeric_limits<Real>::epsilon()) const {
        return computeStoichiometryError(parameters) < precision;
    }
};

typedef ParameterSpaceAdapter<false> NonStationaryParameterSpace;

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H