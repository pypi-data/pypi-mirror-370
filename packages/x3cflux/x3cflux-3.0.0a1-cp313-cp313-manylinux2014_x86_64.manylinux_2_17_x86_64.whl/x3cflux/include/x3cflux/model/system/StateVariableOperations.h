#ifndef X3CFLUX_STATEVARIABLEOPERATIONS_H
#define X3CFLUX_STATEVARIABLEOPERATIONS_H

#include "SystemTraits.h"

namespace x3cflux {

/// \brief Base operations on state variables
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi> struct StateVariableOperations;

template <bool Multi> struct StateVariableOperations<IsotopomerMethod, Multi> {
    typedef typename SystemTraits<IsotopomerMethod, Multi>::SystemStateType SystemState;
    typedef typename SystemTraits<IsotopomerMethod, Multi>::FractionType Fraction;

    static SystemState blockwiseIfMulti(const RealVector &state, Index numMulti) {
        if constexpr (Multi) {
            auto block = SystemState(state.size(), numMulti);
            block.colwise() = state;
            return block;
        } else {
            return state;
        }
    }

    static void assign(SystemState &state, Index place, const Fraction &value) {
        if constexpr (Multi) {
            state.row(place) = value;
        } else {
            state[place] = value;
        }
    }

    static Fraction get(const SystemState &state, Index place) {
        if constexpr (Multi) {
            return state.row(place);
        } else {
            return state[place];
        }
    }

    static Real get(const Fraction &fraction, Index multiPlace) {
        if constexpr (Multi) {
            return fraction[multiPlace];
        } else {
            return fraction;
        }
    }

    static Fraction computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index) {
        if constexpr (Multi) {
            return (fraction0.array() * fraction1.array()).matrix();
        } else {
            return fraction0 * fraction1;
        }
    }
};

template <bool Multi> struct StateVariableOperations<CumomerMethod, Multi> {
    typedef typename SystemTraits<CumomerMethod, Multi>::SystemStateType SystemState;
    typedef typename SystemTraits<CumomerMethod, Multi>::FractionType Fraction;

    static SystemState blockwiseIfMulti(const RealVector &state, Index numMulti) {
        if constexpr (Multi) {
            auto block = SystemState(state.size(), numMulti);
            block.colwise() = state;
            return block;
        } else {
            return state;
        }
    }

    static void assign(SystemState &state, Index place, const Fraction &value) {
        if constexpr (Multi) {
            state.row(place) = value;
        } else {
            state[place] = value;
        }
    }

    static Fraction get(const SystemState &state, Index place) {
        if constexpr (Multi) {
            return state.row(place);
        } else {
            return state[place];
        }
    }

    static Real get(const Fraction &fraction, Index multiPlace, Index) {
        if constexpr (Multi) {
            return fraction[multiPlace];
        } else {
            return fraction;
        }
    }

    static Fraction computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index) {
        if constexpr (Multi) {
            return (fraction0.array() * fraction1.array()).matrix();
        } else {
            return fraction0 * fraction1;
        }
    }
};

template <bool Multi> struct StateVariableOperations<EMUMethod, Multi> {
    typedef typename SystemTraits<EMUMethod, Multi>::SystemStateType SystemState;
    typedef typename SystemTraits<EMUMethod, Multi>::FractionType Fraction;

    static SystemState blockwiseIfMulti(const RealMatrix &state, Index numMulti) {
        if (Multi) {
            Index size = state.cols();
            auto block = SystemState(state.rows(), size * numMulti);

            block.leftCols(size) = state;
            for (Index parInd = 1; parInd < numMulti - 1; ++parInd) {
                block.middleCols(parInd * size, size) = state;
            }
            block.rightCols(size) = state;

            return block;
        } else {
            return state;
        }
    }

    static void assign(SystemState &state, Index place, const Fraction &value) { state.row(place) = value; }

    static Fraction get(const SystemState &state, Index place) { return state.row(place); }

    static Fraction get(const Fraction &fraction, Index multiPlace, Index levelIndex) {
        Index size = levelIndex + 2;
        return fraction.segment(multiPlace * size, size);
    }

    static Fraction computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index level) {
        Index numMulti = fraction1.size() / (level + 1);
        Index size0 = fraction0.size() / numMulti, size1 = fraction1.size() / numMulti;
        Index sizeProd = size0 + size1 - 1;

        Fraction product = RealVector::Zero(sizeProd * numMulti);

        Eigen::Map<RealMatrix> fracMat0(const_cast<Real *>(fraction0.data()), size0, numMulti);
        Eigen::Map<RealMatrix> fracMat1(const_cast<Real *>(fraction1.data()), size1, numMulti);
        Eigen::Map<RealMatrix> fracMatProd(product.data(), sizeProd, numMulti);
        for (Index i = 0; i < size0; ++i) {
            for (Index j = 0; j < size1; ++j) {
                fracMatProd.row(i + j) +=
                    (fracMat0.row(i).transpose().array() * fracMat1.row(j).transpose().array()).matrix().eval();
            }
        }

        return product;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_STATEVARIABLEOPERATIONS_H
