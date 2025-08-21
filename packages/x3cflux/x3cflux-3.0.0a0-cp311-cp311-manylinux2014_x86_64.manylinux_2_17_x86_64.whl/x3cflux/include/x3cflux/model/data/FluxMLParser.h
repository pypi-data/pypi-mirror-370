#ifndef X3CFLUX_SRC_DATA_FLUXMLPARSER_H
#define X3CFLUX_SRC_DATA_FLUXMLPARSER_H

#include <FluxML.h>
#include <MMDocument.h>

#include "FluxMLData.h"
#include "ParseError.h"

namespace x3cflux {

/// \brief FluxML file parser
///
/// Calls the FluxML library to parse FluxML file. Then converts data structures
/// of the FluxML library into a FluxMLData object.
///
/// The current public interface mimics the future FluxML parser. Like this,
/// the next parts of //////13CFLUX3////// can safely depend on it and the FluxML parser
/// can simply be exchanged when the FluxML library is rewritten.
class FluxMLParser {
  private:
    static std::unique_ptr<FluxMLParser> instance_;

  public:
    /// \brief Creates singleton instance if necessary and returns it.
    /// \return singleton instance
    static FluxMLParser &getInstance();

    /// \brief Parses FluxML file data and returns it as FluxMLData instance.
    /// \param filePath system file path of the FluxML file
    /// \return FluxML data
    /// \throws ParseError if FluxML file parsing fails
    FluxMLData parse(const std::string &filePath) const;

  private:
    FluxMLParser() = default;

    static void initialize();

    static NetworkData parseNetworkData(const charptr_map<flux::data::Pool *> &poolMap,
                                        const std::list<flux::data::IsoReaction *> &reactionList);

    static ParameterConstraints parseParameterConstraints(const std::list<flux::data::Constraint> &equalities,
                                                          const std::list<flux::data::Constraint> &inequalities,
                                                          flux::data::ParameterType paramType);

    static std::shared_ptr<Measurement> parseMeasurement(flux::xml::MGroup *group);

    static MeasurementConfiguration parseMeasurementConfiguration(const flux::data::Configuration &configuration);
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_FLUXMLPARSER_H