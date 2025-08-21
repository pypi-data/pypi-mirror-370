#ifndef X3CFLUX_PARAMETERACCESSOR_H
#define X3CFLUX_PARAMETERACCESSOR_H

namespace x3cflux {

/// \brief Accessor that maps (net, xch) to (fwd, bwd) parameters
class ParameterAccessor {
  private:
    Index numReactions_;
    Index numMetabolites_;
    const RealVector &parameters_;

  public:
    /// Create parameter accessor
    /// \param numReactions number of metabolic reactions
    /// \param numMetabolites number of metabolites
    /// \param parameters vector of parameter values
    ParameterAccessor(Index numReactions, Index numMetabolites, const RealVector &parameters)
        : numReactions_(numReactions), numMetabolites_(numMetabolites), parameters_(parameters) {
        X3CFLUX_CHECK(2 * numReactions_ + numMetabolites_ == parameters_.size() or
                      2 * numReactions_ == parameters_.size());
    }

    /// \return number of metabolic reactions
    Index getNumReactions() const { return numReactions_; }

    /// \return number of metabolites
    Index getNumMetabolites() const { return numMetabolites_; }

    /// \return vector of parameter values
    const RealVector &getParameters() const { return parameters_; }

    /// \param reactionIndex index of the reaction
    /// \param forward forward or backward
    /// \return flux value
    Real getFlux(Index reactionIndex, bool forward) const {
        X3CFLUX_CHECK(reactionIndex < numReactions_);

        Real netFlux = parameters_(reactionIndex), xchFlux = parameters_(numReactions_ + reactionIndex);

        if (forward) {
            return xchFlux + std::max(netFlux, 0.);
        } else {
            return xchFlux + std::max(-netFlux, 0.);
        }
    }

    /// \param metaboliteIndex index of metabolites
    /// \return pool size of metabolite
    Real getPoolSize(Index metaboliteIndex) const {
        X3CFLUX_CHECK(2 * numReactions_ + numMetabolites_ == parameters_.size() and metaboliteIndex < numMetabolites_);

        return parameters_(2 * numReactions_ + metaboliteIndex);
    }
};

/// \brief Accessor that maps (net, xch) to (fwd, bwd) parameters including partial derivatives
class DerivativeParameterAccessor : public ParameterAccessor {
  private:
    const RealVector &parameterDerivatives_;

  public:
    /// Create derivative parameter accessor
    /// \param numReactions number of metabolic reactions
    /// \param numMetabolites number of metabolites
    /// \param parameters parameter values
    /// \param parameterDerivatives parameter partial derivative values
    DerivativeParameterAccessor(Index numReactions, Index numMetabolites, const RealVector &parameters,
                                const RealVector &parameterDerivatives)
        : ParameterAccessor(numReactions, numMetabolites, parameters), parameterDerivatives_(parameterDerivatives) {
        X3CFLUX_CHECK(2 * getNumReactions() + getNumMetabolites() == parameterDerivatives_.size() or
                      2 * getNumReactions() == parameterDerivatives_.size());
    }

    /// \param reactionIndex index of reaction
    /// \param forward forward or backward
    /// \return partial flux derivative value
    Real getFluxDerivative(Index reactionIndex, bool forward) const {
        X3CFLUX_CHECK(reactionIndex < getNumReactions());

        const auto &parameters = getParameters();

        Real netFlux = parameters(reactionIndex), netFluxDeriv = parameterDerivatives_(reactionIndex),
             xchFluxDeriv = parameterDerivatives_(getNumReactions() + reactionIndex);

        if (forward) {
            Real maxDeriv;
            if (netFlux > 0) {
                maxDeriv = 1.;
            } else if (netFlux < 0) {
                maxDeriv = 0.;
            } else {
                X3CFLUX_TRACE() << "Derivative of forward flux "
                                   "with net flux of 0 requested";
                maxDeriv = 0.5;
            }

            return xchFluxDeriv + maxDeriv * netFluxDeriv;
        } else {
            Real maxDeriv;
            if (netFlux < 0) {
                maxDeriv = 1.;
            } else if (netFlux > 0) {
                maxDeriv = 0.;
            } else {
                X3CFLUX_TRACE() << "Derivative of backward flux "
                                   "with net flux of 0 requested";
                maxDeriv = 0.5;
            }

            return xchFluxDeriv - maxDeriv * netFluxDeriv;
        }
    }

    /// \param metaboliteIndex index of metabolite
    /// \return partial pool size derivative value
    Real getPoolSizeDerivative(Index metaboliteIndex) const {
        X3CFLUX_CHECK(2 * getNumReactions() + getNumMetabolites() == parameterDerivatives_.size() and
                      metaboliteIndex < getNumMetabolites());

        return parameterDerivatives_(2 * getNumReactions() + metaboliteIndex);
    }
};

} // namespace x3cflux

#endif // X3CFLUX_PARAMETERACCESSOR_H
