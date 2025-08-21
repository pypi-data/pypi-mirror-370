#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERCLASSIFICATION_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERCLASSIFICATION_H

#include <utility>

namespace x3cflux {

/// \brief Classification of metabolic model parameter
class ParameterClassification {
  private:
    std::vector<std::string> parameterNames_;
    std::vector<Index> freeParameters_;
    std::vector<std::pair<Index, Real>> constraintParameters_;
    std::vector<std::pair<Index, std::vector<std::pair<Index, Real>>>> dependentParameters_;
    std::vector<std::pair<Index, Real>> quasiConstraintParameters_;
    std::map<Index, std::pair<Real, Real>> parameterBounds_;

  public:
    /// \brief Creates parameter classification.
    /// \param parameterNames names of all parameters
    /// \param freeParameters indices of free parameters
    /// \param constraintParameters indices and values of constraint parameters
    /// \param dependentParameters indices and free parameter dependencies of dependent parameters
    /// \param quasiConstraintParameters indices and values of parameters that only depend on constraint
    /// parameters
    /// \param parameterBounds indices to lower/upper bounds of parameter
    ParameterClassification(std::vector<std::string> parameterNames, std::vector<Index> freeParameters,
                            std::vector<std::pair<Index, Real>> constraintParameters,
                            std::vector<std::pair<Index, std::vector<std::pair<Index, Real>>>> dependentParameters,
                            std::vector<std::pair<Index, Real>> quasiConstraintParameters,
                            std::map<Index, std::pair<Real, Real>> parameterBounds)
        : parameterNames_(std::move(parameterNames)), freeParameters_(std::move(freeParameters)),
          constraintParameters_(std::move(constraintParameters)), dependentParameters_(std::move(dependentParameters)),
          quasiConstraintParameters_(std::move(quasiConstraintParameters)),
          parameterBounds_(std::move(parameterBounds)) {}

    /// \return total number of parameters
    std::size_t getNumParameters() const { return parameterNames_.size(); }

    /// \return names of all parameters
    const std::vector<std::string> &getParameterNames() const { return parameterNames_; }

    /// \return number of free parameters
    std::size_t getNumFreeParameters() const { return freeParameters_.size(); }

    /// \return indices of free parameters
    const std::vector<Index> &getFreeParameters() const { return freeParameters_; }

    /// \return number of constraint parameters
    std::size_t getNumConstraintParameters() const { return constraintParameters_.size(); }

    /// \return names and values of constraint parameters
    const std::vector<std::pair<Index, Real>> &getConstraintParameters() const { return constraintParameters_; }

    /// \return number of dependent parameters
    std::size_t getNumDependentParameters() const { return dependentParameters_.size(); }

    /// \return names of dependent parameters
    const std::vector<std::pair<Index, std::vector<std::pair<Index, Real>>>> &getDependentParameters() const {
        return dependentParameters_;
    }

    /// \return names and values of parameters that only depend on constraint parameters
    std::size_t getNumQuasiConstraintParameters() const { return quasiConstraintParameters_.size(); }

    /// Quasi-constraint parameter names and values. Quasi-constraint parameters are also
    /// dependent, which means they also appear in the list of dependent parameters.
    ///
    /// \return names and values of parameters that only depend on constraint parameters
    const std::vector<std::pair<Index, Real>> &getQuasiConstraintParameters() const {
        return quasiConstraintParameters_;
    }

    /// \return indices to lower/upper bounds of parameter
    const std::map<Index, std::pair<Real, Real>> &getParameterBounds() const { return parameterBounds_; };
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERCLASSIFICATION_H