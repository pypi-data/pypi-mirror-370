#ifndef X3CFLUX_COMBINATION_H
#define X3CFLUX_COMBINATION_H

#include "Logging.h"

namespace x3cflux {

/// \brief Combination of finite set
/// \tparam Binary Binary number representation (e.g. unsigned integer types)
///
/// Combinations sets that contain fixed-size subset of finite sets. Given a
/// set of size \f$n\f$, the \f$k\f$-combination is the set that contain all
/// \f$k\f$-sized subsets of the base set. The size of the \f$k\f$-combination
/// set is \f${n \choose k}\f$.
template <typename Binary> class Combination {
  public:
    class SubsetIterator {
      public:
        typedef std::ptrdiff_t difference_type;
        typedef Binary value_type;
        typedef Binary &reference;
        typedef Binary *pointer;
        typedef std::input_iterator_tag iterator_category;

      private:
        Binary state_;
        Binary maxState_;

      public:
        explicit SubsetIterator(const Binary &initialState, const Binary &maxState)
            : state_(initialState), maxState_(maxState) {}

        bool operator==(const SubsetIterator &other) const { return state_ == other.state_; }

        bool operator!=(const SubsetIterator &other) const { return state_ != other.state_; }

        SubsetIterator &operator++() {
            if (state_ == maxState_) {
                state_++;
                return *this;
            }

            Binary state = state_;

            // Get lowest set bit
            Binary lowestBit = -state;
            lowestBit &= state;
            // Move lowest 1 block one up
            state += lowestBit;

            // First deleted bit after lowest 1 block
            Binary nextLowestBit = -state;
            nextLowestBit &= state;
            // Get lowest block
            nextLowestBit -= lowestBit;
            // Move block to lower end
            while (not(nextLowestBit & 1))
                nextLowestBit >>= 1;
            nextLowestBit >>= 1;
            state |= nextLowestBit;

            // Set next state
            state_ = state;

            return *this;
        }

        reference operator*() { return state_; }

        const pointer *operator->() const { return &state_; }
    };

  private:
    std::size_t length_;
    std::size_t order_;
    Binary beginState_;
    Binary maxState_;

  public:
    /// Create combination by base set size and subset size.
    /// \param length size of the base set
    /// \param order size of the subsets
    Combination(std::size_t length, std::size_t order) : length_(length), order_(order) {
        X3CFLUX_CHECK(length >= order);
        beginState_ = (1 << order) - 1;
        maxState_ = ((1 << order) - 1) << (length - order);
    }

    /// Generates iterator for all subsets of this combination.
    /// The subsets are represented as binary numbers that whether
    /// the i-th element is included (1) or not (0).
    /// \return iterator for first subset (0, ..., 0, 1, ..., 1)
    SubsetIterator begin() const { return SubsetIterator(beginState_, maxState_); }

    /// Generates iterator for all subsets of this combination.
    /// The subsets are represented as binary numbers that whether
    /// the i-th element is included (1) or not (0).
    /// \return iterator for last subset (1, ..., 1, 0, ..., 0)
    SubsetIterator end() const { return SubsetIterator(maxState_ + 1, maxState_); }

    /// \return size of the base set
    std::size_t getLength() const { return length_; }

    /// \return size of the subsets
    std::size_t getOrder() const { return order_; }
};

} // namespace x3cflux

#endif // X3CFLUX_COMBINATION_H
