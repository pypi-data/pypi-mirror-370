#ifndef X3CFLUX_CASCADEITERATOR_H
#define X3CFLUX_CASCADEITERATOR_H

#include "MetaboliteNetwork.h"
#include "StateTransporter.h"
#include <util/Combination.h>

namespace x3cflux {

/// \brief Level of a cascaded labeling network
///
/// For binary number states, some state variables (e.g. cumomer, EMU) allow
/// decomposition of the network into cascaded levels. Reactions on this level
/// require that products have the same number of 1's in their state
/// which is equal to the level's index.
class CascadeLevel {
  public:
    /// \brief Iterator for reactions on a labeling network level
    class ReactionIterator {
      public:
        using State = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateType;
        using StateVariable = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType;
        using StateReaction = typename StateTransporterTraits<boost::dynamic_bitset<>>::ReactionType;
        using StateIterator = Combination<std::size_t>::SubsetIterator;

        using iterator_category = std::forward_iterator_tag;
        using value_type = StateReaction;
        using difference_type = std::ptrdiff_t;
        using pointer = StateReaction *;
        using reference = StateReaction &;

      private:
        const MetaboliteNetwork &network_;
        std::size_t level_;
        std::size_t reactionIndex_;
        bool forward_;
        std::size_t reactantIndex_;
        StateIterator currentState_;
        StateIterator endState_;
        std::shared_ptr<StateReaction> currentReaction_;

      public:
        /// Create level reaction iterator.
        /// \param network network information
        /// \param level index of the level
        /// \param reactionIndex index of the first reaction
        ReactionIterator(const MetaboliteNetwork &network, std::size_t level, std::size_t reactionIndex);

        /// \param other iterator to compare
        /// \return indicates if iterators are equal
        bool operator==(const ReactionIterator &other) const {
            return reactionIndex_ == other.reactionIndex_ and forward_ == other.forward_ and
                   reactantIndex_ == other.reactantIndex_ and currentState_ == other.currentState_;
        }

        /// \param other iterator to compare
        /// \return indicates if iterators are not equal
        bool operator!=(const ReactionIterator &other) const {
            return reactionIndex_ != other.reactionIndex_ or forward_ != other.forward_ or
                   reactantIndex_ != other.reactantIndex_ or currentState_ != other.currentState_;
        }

        /// Increments iterator that now points to the next state variable reaction.
        /// \return incremented iterator
        ReactionIterator &operator++();

        /// \return current state variable reaction
        const StateReaction &operator*() { return *currentReaction_; }

        /// \return current state variable reaction
        const StateReaction *operator->() { return currentReaction_.get(); }

      private:
        bool setNextLabelingState();

        bool setNextReactant();

        bool setNextDirection();

        bool setLevelProduct();

        bool setLevelReaction();

        void calculateCurrentReaction();

        bool isEfflux() const;

        bool isLevelReactant() const;
    };

  private:
    const MetaboliteNetwork &network_;
    std::size_t index_;

  public:
    /// Create labeling network cascade level.
    /// \param network network information
    /// \param index level index
    CascadeLevel(const MetaboliteNetwork &network, std::size_t index);

    /// \return level index
    std::size_t getIndex() const { return index_; }

    /// \return begin state reaction iterator
    ReactionIterator begin() const { return {network_, index_, 0}; }

    /// \return end state reaction iterator
    ReactionIterator end() const { return {network_, index_, network_.getNumReactions()}; }
};

/// \brief Cascaded labeling network iterator
///
/// For binary states, some state variables (e.g. cumomer, EMU) allow
/// decomposition of the network into cascaded levels. The levels are subnetworks
/// that are sequentially dependent. Reactions from the state variables on the \f$k\f$-th
/// level can only produce state variables on the same or higher level. The level index
/// is given by the number of 1's in a variables' state. The highest possible level is
/// equal to the largest number of traceable atoms of a metabolite. The level 0 is useless
/// and therefore omitted.
class CascadeIterator {
  public:
    using iterator_category = std::forward_iterator_tag;
    using value_type = CascadeLevel;
    using difference_type = std::ptrdiff_t;
    using pointer = CascadeLevel *;
    using reference = CascadeLevel &;

  private:
    const MetaboliteNetwork &network_;
    std::size_t level_;
    std::size_t maxLevel_;
    std::shared_ptr<CascadeLevel> currentLevel_;

  public:
    /// Create cascaded labeling network iterator.
    /// \param network network information
    /// \param begin indicates if begin or end iterator
    __attribute__((unused)) CascadeIterator(const MetaboliteNetwork &network, bool begin);

    /// \param other iterator to compare
    /// \return indicates if iterators are equal
    bool operator==(const CascadeIterator &other) const { return level_ == other.level_; }

    /// \param other iterator to compare
    /// \return indicates if iterators are not equal
    bool operator!=(const CascadeIterator &other) const { return level_ != other.level_; }

    /// Increments iterator that now points to the next network level.
    /// \return incremented iterator
    CascadeIterator &operator++();

    /// \return current network level
    const CascadeLevel &operator*() { return *currentLevel_; }

    /// \return current network level
    const CascadeLevel *operator->() { return currentLevel_.get(); }
};

} // namespace x3cflux

#endif // X3CFLUX_CASCADEITERATOR_H
