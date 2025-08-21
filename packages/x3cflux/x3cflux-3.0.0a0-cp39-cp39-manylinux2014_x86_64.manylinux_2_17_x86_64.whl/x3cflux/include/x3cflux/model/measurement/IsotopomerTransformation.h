#ifndef X3CFLUX_ISOTOPOMERTRANSFORMATION_H
#define X3CFLUX_ISOTOPOMERTRANSFORMATION_H

#include <math/NumericTypes.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>

namespace x3cflux {

template <typename Method> struct IsotopomerTransformation;

template <> struct IsotopomerTransformation<CumomerMethod> {
    static RealVector apply(const RealVector &fractions, bool toIsotopomer = true) {
        RealVector transformedFractions(fractions);
        Index numFractions = fractions.size();
        auto numAtoms = static_cast<Index>(std::log2(numFractions));

        for (Index ldm = numAtoms; ldm >= 1; ldm--) {
            Index m = (1 << ldm);
            Index mh = (m >> 1);
            for (Index r = 0; r < numFractions; r += m) {
                for (Index j = 0; j < mh; j++) {
                    Index s = numFractions - r - j - 1;
                    Index t = s - mh;

                    if (not toIsotopomer) {
                        transformedFractions[t] += transformedFractions[s];
                    } else {
                        transformedFractions[t] -= transformedFractions[s];
                    }
                }
            }
        }

        return transformedFractions;
    }
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERTRANSFORMATION_H
