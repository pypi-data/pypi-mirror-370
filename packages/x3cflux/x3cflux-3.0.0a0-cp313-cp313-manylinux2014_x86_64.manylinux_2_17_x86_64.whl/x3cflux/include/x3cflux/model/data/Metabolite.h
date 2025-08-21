#ifndef X3CFLUX_SRC_DATA_POOL_H
#define X3CFLUX_SRC_DATA_POOL_H

#include <map>
#include <string>

namespace x3cflux {

/// \brief Chemical isotope, e.g. carbon
enum class TracerElement {
    CARBON,
    NITROGEN,
    HYDROGEN,
    OXYGEN,
};

/// \brief Metabolite data
///
/// Stores the metabolite name and the number of traceable atom (carbon,
/// nitrogen, etc.).
class Metabolite {
  private:
    std::string name_;
    std::size_t numAtoms_;
    std::map<TracerElement, std::size_t> numIsotopes_;

  public:
    /// \brief Create a metabolic pool.
    /// \param name name of the metabolite
    /// \param numAtoms number of traceable atoms
    /// \param size fixed size (0 if variable)
    /// \param numIsotopes numbers of atoms from each supported tracer element
    Metabolite(std::string name, std::size_t numAtoms, std::map<TracerElement, std::size_t> numIsotopes)
        : name_(std::move(name)), numAtoms_(numAtoms), numIsotopes_(std::move(numIsotopes)) {}

    /// \return the name of the metabolite
    const std::string &getName() const { return name_; }

    /// \return the number of traceable atoms
    std::size_t getNumAtoms() const { return numAtoms_; }

    /// \return numbers of atoms from each supported tracer element
    const std::map<TracerElement, std::size_t> &getNumIsotopes() const { return numIsotopes_; }
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_POOL_H