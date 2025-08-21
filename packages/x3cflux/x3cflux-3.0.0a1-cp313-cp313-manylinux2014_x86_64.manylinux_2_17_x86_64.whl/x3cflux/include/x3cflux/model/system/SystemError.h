#ifndef X3CFLUX_SYSTEMERROR_H
#define X3CFLUX_SYSTEMERROR_H

#include <stdexcept>
#include <string>

namespace x3cflux {

/// \brief Error for system build and solving
class SystemError : public std::logic_error {
  public:
    /// \brief Creates system error.
    /// \param message description of the error
    explicit SystemError(const std::string &message) : std::logic_error(message) {}
};

} // namespace x3cflux
#endif // X3CFLUX_SYSTEMERROR_H
