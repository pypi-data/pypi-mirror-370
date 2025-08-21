#ifndef X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H
#define X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H

#include <model/system/LabelingSystem.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class ScalableMeasurementSimulation {
  public:
    typedef typename LabelingSystem<Method, true, Multi>::Solution StationarySolution;
    typedef typename LabelingSystem<Method, false, Multi>::Solution InstationarySolution;

  private:
    std::string name_;
    bool autoScalable_;
    std::vector<Real> timeStamps_;
    Index multiIndex_;

  public:
    ScalableMeasurementSimulation(std::string name, bool autoScalable, std::vector<Real> timeStamps, Index multiIndex)
        : name_(std::move(name)), autoScalable_(autoScalable), timeStamps_(std::move(timeStamps)),
          multiIndex_(multiIndex) {}

    const std::string &getName() const { return name_; }

    bool isAutoScalable() const { return autoScalable_; }

    const std::vector<Real> &getTimeStamps() const { return timeStamps_; }

    std::size_t getNumTimeStamps() const { return timeStamps_.size(); }

    Index getMultiIndex() const { return multiIndex_; }

    virtual void setTimeStamps(const std::vector<Real> &timeStamps) { timeStamps_ = timeStamps; }

    virtual std::size_t getSize() const = 0;

    virtual RealVector evaluate(const StationarySolution &solution) const = 0;

    virtual std::vector<RealVector> evaluate(const InstationarySolution &solution) const = 0;

    virtual RealVector evaluateDerivative(const StationarySolution &derivSolution) const = 0;

    virtual std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const = 0;
};

} // namespace x3cflux

#endif // X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H
