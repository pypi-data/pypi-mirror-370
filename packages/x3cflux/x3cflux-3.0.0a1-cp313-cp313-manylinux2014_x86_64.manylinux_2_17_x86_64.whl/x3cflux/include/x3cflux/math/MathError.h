#ifndef X3CFLUX_SRC_MATH_MATHERROR_H
#define X3CFLUX_SRC_MATH_MATHERROR_H

namespace x3cflux {

#include <stdexcept>
#include <string>

/// \brief Error for failed mathmatical operations
class MathError : public std::logic_error {
  public:
    /// \brief Creates math error.
    /// \param message description of the error
    explicit MathError(const std::string &message) : std::logic_error(message) {}
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_MATH_MATHERROR_H