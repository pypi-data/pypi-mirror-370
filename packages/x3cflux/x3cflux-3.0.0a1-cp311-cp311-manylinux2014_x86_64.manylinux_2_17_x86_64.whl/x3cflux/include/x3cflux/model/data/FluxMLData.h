#ifndef X3CFLUX_SRC_DATA_FLUXMLMODEL_H
#define X3CFLUX_SRC_DATA_FLUXMLMODEL_H

#include "MeasurementConfiguration.h"
#include "NetworkData.h"
#include <boost/date_time/posix_time/posix_time.hpp>

namespace x3cflux {

/// \brief Data from a FluxML file
class FluxMLData {
  private:
    std::string name_;
    std::string modelerName_;
    std::string version_;
    std::string comment_;
    boost::posix_time::ptime date_;

    NetworkData networkData_;
    std::vector<MeasurementConfiguration> configurations_;

  public:
    /// \brief Creates FluxML data.
    /// \param name name of the data
    /// \param modelerName name of the modeler
    /// \param version data version
    /// \param comment comment from the modeler
    /// \param date calendar date and time of last data change
    /// \param networkData metabolic network information (pools and reactions)
    /// \param configurations measurement setups based on the network data
    FluxMLData(std::string name, std::string modelerName, std::string version, std::string comment,
               const boost::posix_time::ptime &date, NetworkData networkData,
               std::vector<MeasurementConfiguration> configurations)
        : name_(std::move(name)), modelerName_(std::move(modelerName)), version_(std::move(version)),
          comment_(std::move(comment)), date_(date), networkData_(std::move(networkData)),
          configurations_(std::move(configurations)) {}

    /// \return name of the data
    const std::string &getName() const { return name_; }

    /// \return name of the modeler
    const std::string &getModelerName() const { return modelerName_; }

    /// \return data version
    const std::string &getVersion() const { return version_; }

    /// \return comment from the modeler
    const std::string &getComment() const { return comment_; }

    /// \return date and time of the last data change
    const boost::posix_time::ptime &getDate() const { return date_; }

    /// \return metabolic network information (pools and reactions)
    const NetworkData &getNetworkData() const { return networkData_; }

    /// \return measurement setups based on the network data
    const std::vector<MeasurementConfiguration> &getConfigurations() const { return configurations_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_FLUXMLMODEL_H