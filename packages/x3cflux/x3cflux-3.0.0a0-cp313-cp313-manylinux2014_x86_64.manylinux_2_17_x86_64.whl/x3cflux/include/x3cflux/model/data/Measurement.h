#ifndef X3CFLUX_SRC_DATA_MEASUREMENT_H
#define X3CFLUX_SRC_DATA_MEASUREMENT_H

#include <ExprTree.h>
#include <boost/dynamic_bitset.hpp>
#include <math/NumericTypes.h>
#include <memory>
#include <utility>
#include <vector>

namespace x3cflux {

/// \brief Base class for measurements
class Measurement {
  private:
    std::string name_;
    bool autoScalable_;

  public:
    /// \brief Creates a measurement.
    /// \param name name of the measurement
    /// \param autoScalable flag for weighting simulation residuals
    Measurement(std::string name, bool autoScalable) : name_(std::move(name)), autoScalable_(autoScalable) {}

    virtual ~Measurement() = default;

    /// \return name of the measurement
    const std::string &getName() const { return name_; }

    /// \return flag for weighting simulation residuals
    bool isAutoScalable() const { return autoScalable_; }

    /// Copy function for measurements
    /// \return deep copy of measurement
    virtual std::unique_ptr<Measurement> copy() const = 0;
};

/// \brief Measured data with associated time points, standard deviation and error model
class MeasurementDataSet {
  private:
    std::vector<Real> timeStamps_;
    std::vector<RealVector> values_;
    std::vector<RealVector> standardDeviations_;
    std::vector<flux::symb::ExprTree> errorModels_;

  public:
    /// \brief Creates measurement data set.
    /// \param timeStamps measurement times (time since measurement start)
    /// \param value measured values
    /// \param standardDeviation standard deviations of the measurement
    /// \param errorModels statistical error models
    MeasurementDataSet(std::vector<Real> timeStamps, std::vector<RealVector> values,
                       std::vector<RealVector> standardDeviations, std::vector<flux::symb::ExprTree> errorModels)
        : timeStamps_(std::move(timeStamps)), values_(std::move(values)),
          standardDeviations_(std::move(standardDeviations)), errorModels_(std::move(errorModels)) {}

    /// \return measurement times (time since measurement start)
    std::vector<Real> getTimeStamps() const { return timeStamps_; }

    /// \return measured values
    const std::vector<RealVector> &getValues() const { return values_; }

    /// \return standard deviations of the measurement
    const std::vector<RealVector> &getStandardDeviations() const { return standardDeviations_; }

    /// \return statistical error models
    const std::vector<flux::symb::ExprTree> &getErrorModels() const { return errorModels_; }

    /// \return number of measurements
    std::size_t getNumMeasurements() const { return timeStamps_.size(); }
};

/// \brief Information on mass spectrometry experiment
class MSSpecification {
  private:
    boost::dynamic_bitset<> mask_;
    std::vector<std::size_t> weights_;

  public:
    /// \brief Create mass spectrometry information.
    /// \param mask indicator for measured carbon positions
    /// \param weights measured molecule weights
    MSSpecification(boost::dynamic_bitset<> mask, std::vector<std::size_t> weights)
        : mask_(std::move(mask)), weights_(std::move(weights)) {}

    /// \return indicator for measured carbon positions
    const boost::dynamic_bitset<> &getMask() const { return mask_; }

    /// \return measured molecule weights
    const std::vector<std::size_t> &getWeights() const { return weights_; }
};

/// \brief Information on multi-isotopic mass spectrometry measurement
class MIMSSpecification {
  private:
    boost::dynamic_bitset<> mask_;
    std::vector<std::vector<std::size_t>> weights_;

  public:
    /// \brief Creates multi-isotopic mass spectrometry information.
    /// \param mask indicator for measured atom positions
    /// \param weights measured molecule weights
    MIMSSpecification(boost::dynamic_bitset<> mask, std::vector<std::vector<std::size_t>> weights)
        : mask_(std::move(mask)), weights_(std::move(weights)) {}

    /// \return indicator for measured atom positions
    const boost::dynamic_bitset<> &getMask() const { return mask_; }

    /// \return measured molecule weights
    const std::vector<std::vector<std::size_t>> &getWeights() const { return weights_; }
};

/// \brief Information on tandem mass spectrometry measurement
class MSMSSpecification {
  private:
    boost::dynamic_bitset<> firstMask_, secondMask_;
    std::vector<std::size_t> firstWeights_, secondWeights_;

  public:
    /// \brief Creates tandem mass spectrometry information.
    /// \param firstMask indicator for measured carbon positions before collision
    /// \param secondMask indicator for measured carbon positions after collision
    /// \param firstWeights measured molecule weights before collision
    /// \param secondWeights measured molecule weights after collision
    MSMSSpecification(boost::dynamic_bitset<> firstMask, boost::dynamic_bitset<> secondMask,
                      std::vector<std::size_t> firstWeights, std::vector<std::size_t> secondWeights)
        : firstMask_(std::move(firstMask)), secondMask_(std::move(secondMask)), firstWeights_(std::move(firstWeights)),
          secondWeights_(std::move(secondWeights)) {}

    /// \return indicator for measured carbon positions before collision
    const boost::dynamic_bitset<> &getFirstMask() const { return firstMask_; }

    /// \return indicator for measured carbon positions after collision
    const boost::dynamic_bitset<> &getSecondMask() const { return secondMask_; }

    /// \return measured molecule weights before collision
    const std::vector<std::size_t> &getFirstWeights() const { return firstWeights_; }

    /// \return measured molecule weights after collision
    const std::vector<std::size_t> &getSecondWeights() const { return secondWeights_; }
};

/// \brief Information on hydrogen nuclear magnetic resonance measurement
class HNMRSpecification {
  private:
    std::vector<std::size_t> atomPositions_;

  public:
    /// \brief Creates hydrogen nuclear magnetic resonance information.
    /// \param atomPositions measured carbon positions
    explicit HNMRSpecification(std::vector<std::size_t> atomPositions) : atomPositions_(std::move(atomPositions)) {}

    /// \return measured carbon positions
    const std::vector<std::size_t> &getAtomPositions() const { return atomPositions_; }
};

/// \brief Information on 13C carbon nuclear magnetic resonance measurement
class CNMRSpecification {
  public:
    /// \brief Types of peak observations in 13C-NMR
    enum class CNMRType { SINGLET = 1, DOUBLET_LEFT = 2, DOUBLET_RIGHT = 3, DOUBLET_OF_DOUBLETS = 4, TRIPLETS = 5 };

  private:
    std::vector<std::size_t> atomPositions_;
    std::vector<CNMRType> types_;

  public:
    /// \brief Creates 13C carbon nuclear magnetic resonance information.
    /// \param atomPositions measured carbon positions
    /// \param types observed peak types
    CNMRSpecification(std::vector<std::size_t> atomPositions, std::vector<CNMRType> types)
        : atomPositions_(std::move(atomPositions)), types_(std::move(types)) {}

    /// \return measured carbon positions
    const std::vector<std::size_t> &getAtomPositions() const { return atomPositions_; }

    /// \return observed peak types
    const std::vector<CNMRType> &getTypes() const { return types_; }
};

/// \brief Information on cumomer measurement
class CumomerSpecification {
  private:
    boost::dynamic_bitset<> labeledMask_;
    boost::dynamic_bitset<> wildcardMask_;

  public:
    /// \brief Creates cumomer measurement information.
    /// \param labeledMask indicator for labeled carbon positions
    /// \param wildcardMask indicator for labeled-or-unlabeled carbon positions
    CumomerSpecification(boost::dynamic_bitset<> labeledMask, boost::dynamic_bitset<> wildcardMask)
        : labeledMask_(std::move(labeledMask)), wildcardMask_(std::move(wildcardMask)) {}

    /// \return indicator for labeled carbon positions
    const boost::dynamic_bitset<> &getLabeledMask() const { return labeledMask_; }

    /// \return indicator for labeled-or-unlabeled carbon positions
    const boost::dynamic_bitset<> &getWildcardMask() const { return wildcardMask_; }
};

/// \brief Base class for labeling measurements of a metabolite
class LabelingMeasurement : public Measurement {
  private:
    std::string metaboliteName_;
    std::size_t numAtoms_;

    MeasurementDataSet data_;

  public:
    /// \brief Creates labeling measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param metaboliteName name of the measured metabolite
    /// \param numAtoms number of tracer atoms
    /// \param data measurement data
    LabelingMeasurement(const std::string &name, bool autoScaling, std::string metaboliteName, std::size_t numAtoms,
                        MeasurementDataSet data)
        : Measurement(name, autoScaling), metaboliteName_(std::move(metaboliteName)), numAtoms_(numAtoms),
          data_(std::move(data)) {}

    /// \return name of the measured metabolic pool
    const std::string &getMetaboliteName() const { return metaboliteName_; }

    /// \return number of tracer atoms of the metabolic pool
    std::size_t getNumAtoms() const { return numAtoms_; }

    /// \return measurement data
    const MeasurementDataSet &getData() const { return data_; }
};

/// \brief Implementation of LabelingMeasurement
/// \tparam MethodSpecification_ Specification type for measurement method
template <typename MethodSpecification_> class LabelingMeasurementImpl : public LabelingMeasurement {
  public:
    typedef MethodSpecification_ Specification;

  private:
    Specification specification_;

  public:
    /// \brief Creates implementation of labeling measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param metaboliteName name of the measured metabolite
    /// \param numAtoms number of tracer atoms
    /// \param specification specification information of the used method
    /// \param data measurement data
    LabelingMeasurementImpl(const std::string &name, bool autoScaling, std::string metaboliteName, std::size_t numAtoms,
                            Specification specification, MeasurementDataSet data)
        : LabelingMeasurement(name, autoScaling, metaboliteName, numAtoms, data),
          specification_(std::move(specification)) {}

    /// \return specification information of the used method
    const Specification &getSpecification() const { return specification_; }

    std::unique_ptr<Measurement> copy() const override {
        return std::make_unique<LabelingMeasurementImpl<Specification>>(*this);
    }
};

typedef LabelingMeasurementImpl<MSSpecification> MSMeasurement;
typedef LabelingMeasurementImpl<MIMSSpecification> MIMSMeasurement;
typedef LabelingMeasurementImpl<MSMSSpecification> MSMSMeasurement;
typedef LabelingMeasurementImpl<HNMRSpecification> HNMRMeasurement;
typedef LabelingMeasurementImpl<CNMRSpecification> CNMRMeasurement;
typedef LabelingMeasurementImpl<CumomerSpecification> CumomerMeasurement;

/// \brief Information on flux measurement
class FluxSpecification {
  private:
    std::vector<std::string> fluxNames_;
    bool isNet_;

  public:
    /// \brief Creates flux measurement information.
    /// \param fluxNames names of the fluxes that impacted the measurement
    /// \param isNet indicates if all fluxes are net or exchange
    FluxSpecification(std::vector<std::string> fluxNames, bool isNet)
        : fluxNames_(std::move(fluxNames)), isNet_(isNet) {}

    /// \return names of the fluxes that impacted the measurement
    const std::vector<std::string> &getFluxNames() const { return fluxNames_; }

    /// \return indicates if all fluxes are net or exchange
    bool isNet() const { return isNet_; }
};

/// \brief Information on pool size measurements
class PoolSizeSpecification {
  private:
    std::vector<std::string> poolNames_;

  public:
    /// \brief Creates pool sizes measurement information.
    /// \param poolNames names of the pools that impacted the measurement
    explicit PoolSizeSpecification(std::vector<std::string> poolNames) : poolNames_(std::move(poolNames)) {}

    /// \return names of the pools that impacted the measurement
    const std::vector<std::string> &getPoolNames() const { return poolNames_; }
};

/// \brief Measurement of a combination of metabolic stationary parameters
///
/// Measurement data of parameter measurements is not stored in a list like in
/// labeling-based measurements. That is, because they must be time-independent
/// under isotopic steady-state assumptions.
class ParameterMeasurement : public Measurement {
  private:
    flux::symb::ExprTree measurementFormula_;
    Real value_;
    Real standardDeviation_;
    flux::symb::ExprTree errorModel_;

  public:
    /// \brief Creates parameter measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param measurementFormula formula to calculate the measurement data
    /// \param value measured value
    /// \param standardDeviation standard deviation of the measurement
    /// \param errorModel statistical error model
    ParameterMeasurement(const std::string &name, bool autoScaling, const flux::symb::ExprTree &measurementFormula,
                         Real value, Real standardDeviation, const flux::symb::ExprTree &errorModel)
        : Measurement(name, autoScaling), measurementFormula_(measurementFormula), value_(value),
          standardDeviation_(standardDeviation), errorModel_(errorModel) {}

    /// \return formula to calculate the measurement data
    const flux::symb::ExprTree &getMeasurementFormula() const { return measurementFormula_; }

    /// \return measured value
    Real getValue() const { return value_; }

    /// \return standard deviation of the measurement
    Real getStandardDeviation() const { return standardDeviation_; }

    /// \return statistical error model
    const flux::symb::ExprTree &getErrorModel() const { return errorModel_; }
};

/// \brief Implementation of ParameterMeasurement
/// \tparam MethodSpecification_ Specification type for measurement method
///
/// Measurement data of parameter measurements is not stored in a list like in
/// labeling-based measurements. That is, because they must be time-independent
/// under isotopic steady-state assumptions.
template <typename MethodSpecification_> class ParameterMeasurementImpl : public ParameterMeasurement {
  public:
    typedef MethodSpecification_ Specification;

  private:
    Specification specification_;

  public:
    /// \brief Creates implementation of parameter measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param measurementFormula formula to calculate the measurement data
    /// \param specification specification information of the parameter type
    /// \param value measured value
    /// \param standardDeviation standard deviation of the measurement
    /// \param errorModel statistical error model
    ParameterMeasurementImpl(const std::string &name, bool autoScaling, const flux::symb::ExprTree &measurementFormula,
                             Specification specification, Real value, Real standardDeviation,
                             const flux::symb::ExprTree &errorModel)
        : ParameterMeasurement(name, autoScaling, measurementFormula, value, standardDeviation, errorModel),
          specification_(specification) {}

    /// \return specification information of the parameter type
    const Specification &getSpecification() const { return specification_; }

    std::unique_ptr<Measurement> copy() const override {
        return std::make_unique<ParameterMeasurementImpl<Specification>>(*this);
    }
};

typedef ParameterMeasurementImpl<FluxSpecification> FluxMeasurement;
typedef ParameterMeasurementImpl<PoolSizeSpecification> PoolSizeMeasurement;

/// \brief Measurements of combinations of labeling measurements
class GenericMeasurement : public Measurement {
  public:
    /// \brief Measurement of a combination of labeling measurements
    class SubMeasurement {
      private:
        flux::symb::ExprTree formula_;
        std::vector<std::string> variableNames_;
        std::vector<std::shared_ptr<LabelingMeasurement>> measurements_;

      public:
        /// \brief Creates generic sub measurement.
        /// \param formula formula to calculate the measurement value
        /// \param variableNames names that represent labeling measurements in the
        /// formula
        /// \param measurements labeling measurements that impacted the measurement
        SubMeasurement(const flux::symb::ExprTree &formula, std::vector<std::string> variableNames,
                       std::vector<std::shared_ptr<LabelingMeasurement>> measurements)
            : formula_(formula), variableNames_(std::move(variableNames)), measurements_(std::move(measurements)) {}

        /// Deep-copies generic sub measurement
        /// \param other other generic submeasurement
        SubMeasurement(const SubMeasurement &other) : formula_(other.formula_), variableNames_(other.variableNames_) {
            for (auto meas : other.measurements_) {
                measurements_.emplace_back(dynamic_cast<LabelingMeasurement *>(meas->copy().release()));
            }
        }

        /// \return formula to calculate the measurement value
        const flux::symb::ExprTree &getFormula() const { return formula_; }

        /// \return names that represent labeling measurements in the formula
        const std::vector<std::string> &getVariableNames() const { return variableNames_; }

        /// \return labeling measurements that impacted the measurement
        const std::vector<std::shared_ptr<LabelingMeasurement>> &getMeasurements() const { return measurements_; }
    };

  private:
    std::vector<SubMeasurement> subMeasurements_;

    MeasurementDataSet data_;

  public:
    /// \brief Creates generic measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param subMeasurements component measurements
    /// \param data measurement data
    GenericMeasurement(const std::string &name, bool autoScaling, std::vector<SubMeasurement> subMeasurements,
                       MeasurementDataSet data)
        : Measurement(name, autoScaling), subMeasurements_(std::move(subMeasurements)), data_(std::move(data)) {}

    /// \return component measurements
    const std::vector<SubMeasurement> &getSubMeasurements() const { return subMeasurements_; }

    /// \return measurement data
    const MeasurementDataSet &getData() const { return data_; }

    std::unique_ptr<Measurement> copy() const override { return std::make_unique<GenericMeasurement>(*this); }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_MEASUREMENT_H