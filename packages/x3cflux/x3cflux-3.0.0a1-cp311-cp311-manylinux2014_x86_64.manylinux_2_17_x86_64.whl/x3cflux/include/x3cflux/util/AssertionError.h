#ifndef X3CFLUX_ASSERTIONERROR_H
#define X3CFLUX_ASSERTIONERROR_H

#include <stdexcept>
#include <string>

namespace x3cflux {

/// \brief Error for failed assertions
class AssertionError : public std::logic_error {
  public:
    /// \brief Creates assertion error.
    explicit AssertionError(const std::string &message) : std::logic_error(message) {}
};

} // namespace x3cflux

#endif // X3CFLUX_ASSERTIONERROR_H