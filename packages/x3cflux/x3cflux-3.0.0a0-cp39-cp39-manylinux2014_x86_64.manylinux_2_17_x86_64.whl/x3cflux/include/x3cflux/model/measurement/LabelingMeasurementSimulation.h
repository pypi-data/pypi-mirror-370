#ifndef X3CFLUX_LABELINGMEASUREMENTSIMULATION_H
#define X3CFLUX_LABELINGMEASUREMENTSIMULATION_H

#include "ScalableMeasurementSimulation.h"

namespace x3cflux {

template <typename Method, bool Multi = false>
class LabelingMeasurementSimulation : public ScalableMeasurementSimulation<Method, Multi> {
  public:
    typedef typename ScalableMeasurementSimulation<Method, Multi>::StationarySolution StationarySolution;
    typedef typename ScalableMeasurementSimulation<Method, Multi>::InstationarySolution InstationarySolution;

  private:
    std::string poolName_;

  public:
    LabelingMeasurementSimulation(std::string name, bool autoScalable, std::vector<Real> timeStamps,
                                  std::size_t multiIndex, std::string poolName)
        : ScalableMeasurementSimulation<Method, Multi>(name, autoScalable, timeStamps, multiIndex),
          poolName_(std::move(poolName)) {}

    const std::string &getPoolName() const { return poolName_; }
};

} // namespace x3cflux

#endif // X3CFLUX_LABELINGMEASUREMENTSIMULATION_H
