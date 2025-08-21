#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERERROR_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERERROR_H

#include <stdexcept>
#include <string>

namespace x3cflux {

/// \brief Error for parameter selection
class ParameterError : public std::logic_error {
  public:
    /// \brief Creates parameter error.
    /// \param message description of the error
    explicit ParameterError(const std::string &message) : std::logic_error(message) {}
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERERROR_H