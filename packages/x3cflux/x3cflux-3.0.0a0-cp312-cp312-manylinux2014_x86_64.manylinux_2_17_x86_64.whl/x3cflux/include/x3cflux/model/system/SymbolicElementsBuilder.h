#ifndef X3CFLUX_SYMBOLICELEMENTSBUILDER_H
#define X3CFLUX_SYMBOLICELEMENTSBUILDER_H

#include <boost/functional/hash.hpp>

#include "NonLinearElement.h"
#include "SymbolicLinearElement.h"
#include "SystemTraits.h"
#include <model/network/StateTransporter.h>

namespace x3cflux {

template <typename Network, bool Stationary, bool Multi> class SymbolicNonLinearityBuilder;

/// \brief Builder for symbolic elements of cascade system
/// \tparam Network cascade labeling network type
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Network, bool Stationary, bool Multi> class SymbolicElementsBuilder {
  public:
    typedef typename Network::ModelingMethod Method;
    typedef typename Network::Ordering Ordering;
    typedef StateVariableImpl<typename Method::StateType> StateVariable;

    typedef std::unordered_map<std::pair<std::size_t, std::size_t>, std::size_t,
                               boost::hash<std::pair<std::size_t, std::size_t>>>
        CoordinateMap;
    typedef SymbolicNonLinearityBuilder<Network, Stationary, Multi> NonLinearityBuilder;
    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

    typedef SymbolicLinearElement<Stationary> SymbLinearElement;
    typedef SymbolicNonLinearElement<Method, Stationary, Multi> SymbNonLinearElement;

  private:
    const MetaboliteNetwork &network_;
    const Ordering &ordering_;
    const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates_;
    const NonLinearityBuilder &nonLinearityBuilder_;

    std::vector<Index> poolSizeIndices_;
    CoordinateMap linearityPositions_;
    std::unordered_map<Index, Index> nonLinearityPositions_;

    std::vector<SymbLinearElement> symbolicLinearities_;
    std::vector<SymbNonLinearElement> symbolicNonLinearities_;

  public:
    /// Create builder for symbolic elements of cascade system
    /// \param network labeling network
    /// \param ordering ordering of labeling network
    /// \param substrates substrates of experiment
    /// \param nonLinearityBuilder build of non-linear elements
    SymbolicElementsBuilder(const Network &network, const Ordering &ordering,
                            const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates,
                            const NonLinearityBuilder &nonLinearityBuilder)
        : network_(network), ordering_(ordering), substrates_(substrates), nonLinearityBuilder_(nonLinearityBuilder) {
        // Cache pool size indices
        Index poolSizeIndex = 0;
        for (std::size_t poolIndex = 0; poolIndex < network_.getNumPools(); ++poolIndex) {
            if (network_.getPoolInformation(poolIndex).isSubstrate()) {
                poolSizeIndices_.push_back(-1);
            } else {
                poolSizeIndices_.push_back(poolSizeIndex++);
            }
        }
    }

    /// Create symbolic elements from reaction
    /// \param reactionIndex index of metabolic reaction
    /// \param forward forward or backward
    /// \param product state variable product
    /// \param educts state variable educts
    void addReaction(Index reactionIndex, bool forward, const StateVariable &product,
                     const std::vector<StateVariable> &educts) {
        Index rowIndex = ordering_.getSystemIndex(product);
        Index poolSizeIndex = poolSizeIndices_[product.getPoolIndex()];

        // Subtract flux placeholder from diagonal
        auto &diagLinElem = getSymbolicLinearElement(rowIndex, rowIndex, poolSizeIndex);
        diagLinElem.addFlux(reactionIndex, forward);

        if (educts.size() > 1) {
            auto &nonLinElem = getSymbolicNonLinearElement(rowIndex, poolSizeIndex);
            nonLinElem.addNonLinearity(reactionIndex, forward, nonLinearityBuilder_.buildCondensation(educts));
        } else {
            const auto &educt = educts.front();
            const auto &eductInfo = network_.getPoolInformation(educt.getPoolIndex());

            if (eductInfo.isSubstrate()) {
                // Add substrate intake to
                // non-linearities
                auto substrateIntake =
                    nonLinearityBuilder_.buildSubstrateIntake(substrates_, eductInfo.getName(), educt.getState());

                if (substrateIntake) {
                    auto &nonLinElem = getSymbolicNonLinearElement(rowIndex, poolSizeIndex);
                    nonLinElem.addNonLinearity(reactionIndex, forward, substrateIntake);
                }
            } else {
                Index columnIndex = ordering_.getSystemIndex(educt);

                // Add flux placeholder for influx to
                // linearities
                auto &linElem = getSymbolicLinearElement(rowIndex, columnIndex, poolSizeIndex);
                linElem.addFlux(reactionIndex, forward);
            }
        }
    }

    /// \return created symbolic linear elements
    const std::vector<SymbLinearElement> &getSymbolicLinearities() const { return symbolicLinearities_; }

    /// \return created symbolic non-linear elements
    const std::vector<SymbNonLinearElement> &getSymbolicNonLinearities() const { return symbolicNonLinearities_; }

  private:
    SymbLinearElement &getSymbolicLinearElement(Index rowIndex, Index columnIndex, Index poolSizeIndex) {
        auto position = std::make_pair(rowIndex, columnIndex);
        auto posIt = linearityPositions_.find(position);

        if (posIt == linearityPositions_.end()) {
            linearityPositions_[position] = symbolicLinearities_.size();
            symbolicLinearities_.emplace_back(rowIndex, columnIndex, poolSizeIndex);
            return symbolicLinearities_.back();
        } else {
            return symbolicLinearities_[posIt->second];
        }
    }

    SymbNonLinearElement &getSymbolicNonLinearElement(Index rowIndex, Index poolSizeIndex) {
        auto posIt = nonLinearityPositions_.find(rowIndex);

        if (posIt == nonLinearityPositions_.end()) {
            nonLinearityPositions_[rowIndex] = symbolicNonLinearities_.size();
            symbolicNonLinearities_.emplace_back(rowIndex, poolSizeIndex);
            return symbolicNonLinearities_.back();
        } else {
            return symbolicNonLinearities_[posIt->second];
        }
    }
};

} // namespace x3cflux

#endif // X3CFLUX_SYMBOLICELEMENTSBUILDER_H
