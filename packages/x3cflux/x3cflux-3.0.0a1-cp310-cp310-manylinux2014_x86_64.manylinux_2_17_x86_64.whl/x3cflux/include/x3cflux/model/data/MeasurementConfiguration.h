#ifndef X3CFLUX_SRC_DATA_MEASUREMENTCONFIGURATION_H
#define X3CFLUX_SRC_DATA_MEASUREMENTCONFIGURATION_H

#include <utility>

#include "Measurement.h"
#include "ParameterConstraints.h"
#include "Substrate.h"

namespace x3cflux {

/// \brief Metabolic stationary parameter types
enum class ParameterType {
    NET_FLUX,
    EXCHANGE_FLUX,
    POOL_SIZE,
};

/// \brief Definition of a metabolic stationary parameter
class ParameterEntry {
  private:
    std::string name_;
    ParameterType type_;
    Real value_;

  public:
    /// \brief Creates a parameter definition.
    /// \param name parameter name
    /// \param type parameter type
    /// \param value numeric value to assign
    ParameterEntry(std::string name, ParameterType type, Real value)
        : name_(std::move(name)), type_(type), value_(value) {}

    /// \return parameter name
    const std::string &getName() const { return name_; }

    /// \return parameter type
    ParameterType getType() const { return type_; }

    /// \return assigned value
    Real getValue() const { return value_; }
};

/// \brief Measurement setup and data
///
/// A measurement setup is primarily defined by the choice of substrate and
/// and the resulting measurement data. Additionally, biologically motivated
/// constraints can be supplied to narrow down the variety of feasible
/// parameters.
/// Lastly, a previously calculated parameter vector (i.e. to perform a single
/// forward simulation) can be specified.
class MeasurementConfiguration {
  private:
    std::string name_;
    std::string comment_;

    bool stationary_;
    std::vector<std::shared_ptr<Substrate>> substrates_;
    std::vector<std::shared_ptr<Measurement>> measurements_;

    ParameterConstraints netFluxConstraints_;
    ParameterConstraints exchangeFluxConstraints_;
    ParameterConstraints poolSizeConstraints_;

    std::vector<ParameterEntry> parameterEntries_;

  public:
    /// \brief Creates measurement configuration.
    /// \param name name of the configuration
    /// \param comment comment from the designer
    /// \param stationary flag if the experiment was stationary
    /// \param substrates substrates of the experiment
    /// \param measurements measurement data of the experiment
    /// \param netFluxConstraints constraints of the net fluxes
    /// \param exchangeFluxConstraints constraint of the exchange fluxes
    /// \param poolSizeConstraints constraints of the pool sizes
    /// \param parameterEntries pre-calculated parameter vector
    MeasurementConfiguration(std::string name, std::string comment, bool stationary,
                             std::vector<std::shared_ptr<Substrate>> substrates,
                             std::vector<std::shared_ptr<Measurement>> measurements,
                             ParameterConstraints netFluxConstraints, ParameterConstraints exchangeFluxConstraints,
                             ParameterConstraints poolSizeConstraints, std::vector<ParameterEntry> parameterEntries)
        : name_(std::move(name)), comment_(std::move(comment)), stationary_(stationary),
          substrates_(std::move(substrates)), measurements_(std::move(measurements)),
          netFluxConstraints_(std::move(netFluxConstraints)),
          exchangeFluxConstraints_(std::move(exchangeFluxConstraints)),
          poolSizeConstraints_(std::move(poolSizeConstraints)), parameterEntries_(std::move(parameterEntries)) {}

    /// \return configuration name
    const std::string &getName() const { return name_; }

    /// \return designer comment
    const std::string &getComment() const { return comment_; }

    /// \return flag if stationary
    bool isStationary() const { return stationary_; }

    /// \return substrates
    const std::vector<std::shared_ptr<Substrate>> &getSubstrates() const { return substrates_; }

    /// \return measurement data
    const std::vector<std::shared_ptr<Measurement>> &getMeasurements() const { return measurements_; }

    /// \return constraints of net fluxes
    const ParameterConstraints &getNetFluxConstraints() const { return netFluxConstraints_; }

    /// \return constraints of exchange fluxes
    const ParameterConstraints &getExchangeFluxConstraints() const { return exchangeFluxConstraints_; }

    /// \return constraints of pool sizes
    const ParameterConstraints &getPoolSizeConstraints() const { return poolSizeConstraints_; }

    /// \return pre-calculated parameter vector
    const std::vector<ParameterEntry> &getParameterEntries() const { return parameterEntries_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_MEASUREMENTCONFIGURATION_H