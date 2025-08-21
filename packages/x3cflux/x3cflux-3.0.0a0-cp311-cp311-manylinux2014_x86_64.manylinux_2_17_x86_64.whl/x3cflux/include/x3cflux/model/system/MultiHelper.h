#ifndef X3CFLUX_MULTIHELPER_H
#define X3CFLUX_MULTIHELPER_H

#include <vector>

namespace x3cflux {

/// \brief Given type (single) or vector of given type (multi)
template <typename T, bool Multi> using MultiAdapter = std::conditional_t<Multi, std::vector<T>, T>;

/// \brief Helper class for function calls in both multiple/single scenarios
/// \tparam Multi multiple or single experiment
template <bool Multi> struct MultiHelper;

template <> struct MultiHelper<false> {
    template <typename T> using MultiAdapt = MultiAdapter<T, false>;

    template <typename Result, typename InType, typename Function, typename... Args>
    static Result apply(Function func, const InType &arg0, Args... args) {
        return func(arg0, args...);
    }
};

template <> struct MultiHelper<true> {
    template <typename T> using MultiAdapt = MultiAdapter<T, true>;

    template <typename Result, typename InType, typename Function, typename... Args>
    static Result apply(Function func, const std::vector<InType> &arg0, Args... args) {
        std::size_t numMulti = arg0.size();

        Result container(numMulti);
        for (std::size_t parIndex = 0; parIndex < numMulti; ++parIndex) {
            container[parIndex] = func(arg0[parIndex], args...);
        }

        return container;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_MULTIHELPER_H
