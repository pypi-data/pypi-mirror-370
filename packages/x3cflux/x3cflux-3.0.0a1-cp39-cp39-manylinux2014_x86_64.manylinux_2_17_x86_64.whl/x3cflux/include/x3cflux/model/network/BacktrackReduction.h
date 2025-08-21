#ifndef X3CFLUX_BACKTRACKREDUCTION_H
#define X3CFLUX_BACKTRACKREDUCTION_H

#include "MeasurementConverter.h"
#include "MetaboliteNetwork.h"
#include "StateTransporter.h"
#include <model/data/Measurement.h>
#include <unordered_map>
#include <unordered_set>

// Add std::hash support for boost::dynamic_bitset<> (Boost Version < 1.71.0)
#if (BOOST_VERSION / 100) % 1000 < 71
#include <functional>
namespace std {
template <> struct hash<boost::dynamic_bitset<>> {
    typedef boost::dynamic_bitset<> argument_type;
    typedef std::size_t result_type;
    result_type operator()(const argument_type &a) const noexcept {
        std::hash<unsigned long> hasher;
        return hasher(a.to_ulong()); // todo: use hasher that works for all sizes
    }
};
} // namespace std
#endif

namespace x3cflux {

/// \brief Backtracking based network reduction algorithm
/// \tparam Method modeling method
/// \tparam Transporter transporter of the methods state
/// \tparam Converter measurement converter of the method
///
/// To reduce a labeling network this approach calculates the state variables
/// that can be identified by the given measurements. From these variables the
/// algorithm identifies all necessary state variables and reactions to form the
/// measurement state variable by tracking their states through the networks
/// reactions.
template <typename Method,
          typename Transporter = std::enable_if_t<HasStateTransporter<typename Method::StateType>::value,
                                                  StateTransporter<typename Method::StateType>>,
          typename Converter = std::enable_if_t<HasMeasurementConverter<Method>::value, MeasurementConverter<Method>>>
class BacktrackReduction : public MetaboliteNetwork {
  public:
    typedef StateTransporterTraits<typename Method::StateType> TransporterTraits;
    typedef typename TransporterTraits::StateType State;
    typedef typename TransporterTraits::StateVariableType StateVariable;
    typedef typename TransporterTraits::ReactionType Reaction;

  private:
    std::unordered_map<std::size_t, std::unordered_set<State>> stateVariables_;
    std::vector<Reaction> reactions_;
    IntegerMatrix flowDirectionTable_;

  public:
    /// Create and run backtrack reduction algorithm.
    /// \param networkData raw metabolite and reaction data
    /// \param substrates raw substrate data
    /// \param measurements raw measurement data
    BacktrackReduction(const NetworkData &networkData, const std::vector<std::shared_ptr<Substrate>> &substrates,
                       const std::vector<std::shared_ptr<LabelingMeasurement>> &measurements)
        : MetaboliteNetwork(networkData, substrates) {
        // Use matrix as fast lookup table
        flowDirectionTable_ = IntegerMatrix::Zero(getNumPools(), getNumReactions());
        for (std::size_t reactionIndex = 0; reactionIndex < getNumReactions(); ++reactionIndex) {
            const auto &hyperedge = getHyperedge(reactionIndex);
            const auto &eductIndices = hyperedge.first;
            const auto &productIndices = hyperedge.second;
            for (const auto &eductIndex : eductIndices) {
                flowDirectionTable_(eductIndex, reactionIndex) -= 1;
            }
            for (const auto &productIndex : productIndices) {
                flowDirectionTable_(productIndex, reactionIndex) += 1;
            }

            auto isProduct = [&](std::size_t metabIndex) {
                return std::find(productIndices.begin(), productIndices.end(), metabIndex) != hyperedge.second.end();
            };
            if (std::any_of(eductIndices.begin(), eductIndices.end(), isProduct)) {
                auto it = std::find_if(eductIndices.begin(), eductIndices.end(), isProduct);
                X3CFLUX_WARNING() << "Reaction \"" << this->getReactionInformation(reactionIndex).getName()
                                  << "\" both requires and produces "
                                     "metabolite \""
                                  << this->getPoolInformation(*it).getName()
                                  << "\". "
                                     "This is not yet supported. "
                                     "Thus, the reaction "
                                     "is omitted from the balance "
                                     "equations "
                                     "of the metabolic pool.";
            }
        }

        // Backtracking root
        for (const auto &measurement : measurements) {
            std::size_t poolIndex = getMeasurementPoolIndex(measurement);

            for (const auto &state : Converter::calculateStates(measurement)) {
                backtrackStateVariable(poolIndex, state);
            }
        }
    }

    /// \return reduced state variable
    const std::unordered_map<std::size_t, std::unordered_set<State>> &getStateVariables() const {
        return stateVariables_;
    }

    /// \return reduced state variable reactions
    const std::vector<Reaction> &getReactions() const { return reactions_; }

  private:
    Index getMeasurementPoolIndex(const std::shared_ptr<LabelingMeasurement> &measurement) const {
        Index poolIndex;

        for (poolIndex = 0; poolIndex < static_cast<Index>(getNumPools()); ++poolIndex) {
            if (getPoolInformation(poolIndex).getName() == measurement->getMetaboliteName()) {
                break;
            }
        }
        X3CFLUX_CHECK(poolIndex < static_cast<Index>(getNumPools()));

        return poolIndex;
    }

    void backtrackStateVariable(Index poolIndex, const State &state) {
        auto &visitedStates = stateVariables_[poolIndex];

        // Check if state has already been visited
        if (std::find(visitedStates.begin(), visitedStates.end(), state) != visitedStates.end()) {
            return;
        }

        visitedStates.emplace(state);

        // Check if in which reactions the current pool is involved
        for (Index reactionIndex = 0; reactionIndex < static_cast<Index>(getNumReactions()); ++reactionIndex) {
            // Skip non-related reactions and effluxes
            if (flowDirectionTable_(poolIndex, reactionIndex) == 0 or getHyperedge(reactionIndex).second.size() == 0) {
                continue;
            }

            // Fetch reaction information
            StateVariable product(poolIndex, state);
            const auto &reactionInfo = getReactionInformation(reactionIndex);
            const auto &hyperedge = getHyperedge(reactionIndex);

            if (flowDirectionTable_(poolIndex, reactionIndex) < 0 and reactionInfo.isBidirectional()) {
                const auto &productIndices = hyperedge.first;

                auto it = std::find(productIndices.begin(), productIndices.end(), poolIndex);
                do {
                    auto reactantIndex = std::distance(productIndices.begin(), it);
                    auto educts = Transporter::transport(*this, reactionIndex, false, reactantIndex, state);

                    reactions_.emplace_back(reactionIndex, false, product, educts);
                    for (const auto &unknown : educts) {
                        backtrackStateVariable(unknown.getPoolIndex(), unknown.getState());
                    }

                    it = std::find(++it, productIndices.end(), poolIndex);
                } while (it != productIndices.end());
            } else if (flowDirectionTable_(poolIndex, reactionIndex) > 0) {
                const auto &productIndices = hyperedge.second;

                auto it = std::find(productIndices.begin(), productIndices.end(), poolIndex);
                do {
                    auto reactantIndex = std::distance(productIndices.begin(), it);
                    auto educts = Transporter::transport(*this, reactionIndex, true, reactantIndex, state);

                    reactions_.emplace_back(reactionIndex, true, product, educts);
                    for (const auto &unknown : educts) {
                        backtrackStateVariable(unknown.getPoolIndex(), unknown.getState());
                    }

                    it = std::find(++it, productIndices.end(), poolIndex);
                } while (it != productIndices.end());
            }
        }
    }
};

} // namespace x3cflux

#endif // X3CFLUX_BACKTRACKREDUCTION_H
