#ifndef X3CFLUX_ISOTOPOMERITERATOR_H
#define X3CFLUX_ISOTOPOMERITERATOR_H

#include <utility>

#include "MetaboliteNetwork.h"
#include "StateTransporter.h"

namespace x3cflux {

/// \brief Reaction of isotopomers
class IsotopomerReaction {
  public:
    typedef StateVariableImpl<boost::dynamic_bitset<>> Isotopomer;

  private:
    std::size_t reactionIndex_;
    bool forward_;
    std::vector<Isotopomer> educts_;
    std::vector<Isotopomer> products_;

  public:
    /// Create reaction of isotopomers.
    /// \param reactionIndex metabolic reaction index
    /// \param forward indicates if reaction is forward or backward
    /// \param educts isotopomer educts
    /// \param products isotopomer products
    IsotopomerReaction(std::size_t reactionIndex, bool forward, std::vector<Isotopomer> educts,
                       std::vector<Isotopomer> products)
        : reactionIndex_(reactionIndex), forward_(forward), educts_(std::move(educts)), products_(std::move(products)) {
    }

    /// \return metabolic reaction index
    std::size_t getReactionIndex() const { return reactionIndex_; }

    /// indicates if reaction is forward or backward
    bool isForward() const { return forward_; }

    /// \return isotopomer educts
    const std::vector<Isotopomer> &getEducts() const { return educts_; }

    /// \return isotopomer products
    const std::vector<Isotopomer> &getProducts() const { return products_; }
};

/// \brief Isotopomer reaction iterator
///
/// This iterator iterates metabolite reactions and
/// generates isotopomer reactions on-the-fly.
class IsotopomerIterator {
  public:
    typedef std::ptrdiff_t difference_type;
    typedef IsotopomerReaction value_type;
    typedef IsotopomerReaction &reference;
    typedef IsotopomerReaction &pointer;
    typedef std::forward_iterator_tag iterator_category;
    typedef typename IsotopomerReaction::Isotopomer Isotopomer;

  private:
    const MetaboliteNetwork &network_;
    std::size_t reactionIndex_;
    bool forward_;
    std::size_t labelingIndex_;
    std::shared_ptr<IsotopomerReaction> currentReaction_;

  public:
    /// Create isotopomer reaction iterator.
    /// \param network network information
    /// \param begin indicates if begin or end iterator
    IsotopomerIterator(const MetaboliteNetwork &network, bool begin);

    /// \param other iterator to compare
    /// \return indicates if iterators are equal
    bool operator==(const IsotopomerIterator &other) const {
        return reactionIndex_ == other.reactionIndex_ and forward_ == other.forward_ and
               labelingIndex_ == other.labelingIndex_;
    }

    /// \param other iterator to compare
    /// \return indicates if iterators are not equal
    bool operator!=(const IsotopomerIterator &other) const {
        return reactionIndex_ != other.reactionIndex_ or forward_ != other.forward_ or
               labelingIndex_ != other.labelingIndex_;
    }

    /// Increments iterator that now points to the next isotopomer reaction.
    /// \return incremented iterator
    IsotopomerIterator &operator++();

    /// \return current isotopomer reaction
    const IsotopomerReaction &operator*() { return *currentReaction_; }

    /// \return current isotopomer reaction
    const IsotopomerReaction *operator->() { return currentReaction_.get(); }

  private:
    void calculateCurrentReaction();

    std::vector<Isotopomer> getIsotopomerReactants(const std::vector<std::size_t> &vertices,
                                                   const boost::dynamic_bitset<> &labeling) const;

    static boost::dynamic_bitset<> getSubrange(const boost::dynamic_bitset<> &set, std::size_t begin, std::size_t end);

    bool isEfflux() const;
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERITERATOR_H
