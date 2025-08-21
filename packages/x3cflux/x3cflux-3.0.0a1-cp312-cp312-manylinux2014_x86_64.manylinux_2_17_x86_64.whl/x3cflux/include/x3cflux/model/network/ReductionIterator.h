#ifndef X3CFLUX_REDUCTIONITERATOR_H
#define X3CFLUX_REDUCTIONITERATOR_H

#include "StateTransporter.h"

namespace x3cflux {

/// \brief Default reduction iterator (cannot be used)
/// \tparam T modeling state type
///
/// For certain state variables labeling networks can be reduced based
/// on their state type. The iterator is supposed to iterate the reduced
/// state variable reaction set.
template <typename T> class ReductionIterator {};

/// \brief Reduction iterator check (default false)
/// \tparam T modeling state type
///
/// Check should be implemented for types that have a
/// sensible reduction iterator implementation.
template <typename T> struct HasReductionIterator : public std::false_type {};

/// \brief Base class for reduction iterators
/// \tparam T modeling state type
///
/// Supplies useful typedefs.
template <typename T> class ReductionIteratorBase {
  public:
    typedef StateTransporterTraits<T> TransporterTraits;
    typedef typename TransporterTraits::StateType State;
    typedef typename TransporterTraits::ReactionType Reaction;
};

/// \brief Reduction iterator implementation for binary number state
///
/// The implementation works for state variables with binary numbers as state
/// (e.g. Cumomer, EMU). It decomposes the reduced set of reaction into cascade
/// levels and enables iteration over levels and reactions (see CascadeIterator).
template <> class ReductionIterator<boost::dynamic_bitset<>> : public ReductionIteratorBase<boost::dynamic_bitset<>> {
  public:
    typedef ReductionIteratorBase<boost::dynamic_bitset<>> Base;
    using Base::Reaction;
    using Base::State;

    /// \brief Iterator for reactions a on reduced labeling network level
    class ReactionIterator {
      private:
        const std::vector<Reaction> &reactions_;
        std::size_t level_;
        std::size_t reactionIndex_;

      public:
        /// Create reaction iterator for reduced reaction set.
        /// \param reactions reduced reaction
        /// \param level index of cascade level
        /// \param reactionIndex index of first reaction
        ReactionIterator(const std::vector<Reaction> &reactions, std::size_t level, std::size_t reactionIndex);

        /// \param other iterator to compare
        /// \return indicates if iterators are equal
        bool operator==(const ReactionIterator &other) const {
            return level_ == other.level_ and reactionIndex_ == other.reactionIndex_;
        }

        /// \param other iterator to compare
        /// \return indicates if iterators are not equal
        bool operator!=(const ReactionIterator &other) const {
            return level_ != other.level_ or reactionIndex_ != other.reactionIndex_;
        }

        /// Increments iterator that now points to the next state variable reaction.
        /// \return incremented iterator
        ReactionIterator &operator++();

        /// \return current state variable reaction
        const Reaction &operator*() { return reactions_[reactionIndex_]; }

        /// \return current state variable reaction
        const Reaction *operator->() { return &reactions_[reactionIndex_]; }

      private:
        void setNextReactionIndex();
    };

    /// \brief Level of a reduced cascaded labeling network
    ///
    /// The implementation works for state variables with binary numbers as state
    /// (e.g. Cumomer, EMU). The level is a subset of the reduced labeling network
    /// (see CascadeLevel). Its reaction can be iterated.
    class ReductionLevel {
      public:
        const std::vector<Reaction> &reactions_;
        std::size_t index_;

      public:
        /// Create reduced labeling network level.
        /// \param reactions reduced reactions
        /// \param index index of the level
        ReductionLevel(const std::vector<Reaction> &reactions, std::size_t index)
            : reactions_(reactions), index_(index) {}

        /// \return index of the level
        std::size_t getIndex() const { return index_; }

        /// \return begin state reaction iterator
        ReactionIterator begin() const { return {reactions_, index_, 0}; }

        /// \return end state reaction iterator
        ReactionIterator end() const { return {reactions_, index_, reactions_.size()}; }
    };

  private:
    const std::vector<Reaction> &reactions_;
    std::size_t level_;
    std::size_t maxLevel_;
    std::shared_ptr<ReductionLevel> currentLevel_;

  public:
    /// Create reduced cascaded labeling network iterator.
    /// \param reactions reduced reactions
    /// \param begin indicates if begin or end iterator
    ReductionIterator(const std::vector<Reaction> &reactions, bool begin);

    /// \param other iterator to compare
    /// \return indicates if iterators are equal
    bool operator==(const ReductionIterator &other) const { return level_ == other.level_; }

    /// \param other iterator to compare
    /// \return indicates if iterators are not equal
    bool operator!=(const ReductionIterator &other) const { return level_ != other.level_; }

    /// Increments iterator that now points to the next network level.
    /// \return incremented iterator
    ReductionIterator &operator++();

    /// \return current network level
    const ReductionLevel &operator*() { return *currentLevel_; }

    /// \return current network level
    const ReductionLevel *operator->() { return currentLevel_.get(); }
};

/// \brief Reduction iterator check for binary number state
template <> struct HasReductionIterator<boost::dynamic_bitset<>> : public std::true_type {};

} // namespace x3cflux

#endif // X3CFLUX_REDUCTIONITERATOR_H
