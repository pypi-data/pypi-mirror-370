#ifndef X3CFLUX_SRC_DATA_PARSEERROR_H
#define X3CFLUX_SRC_DATA_PARSEERROR_H

namespace x3cflux {

#include <stdexcept>
#include <string>

/// \brief Error for failed data parsing
class ParseError : public std::logic_error {
  public:
    /// \brief Creates parse error.
    /// \param message description of the error
    explicit ParseError(const std::string &message) : std::logic_error(message) {}
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_PARSEERROR_H