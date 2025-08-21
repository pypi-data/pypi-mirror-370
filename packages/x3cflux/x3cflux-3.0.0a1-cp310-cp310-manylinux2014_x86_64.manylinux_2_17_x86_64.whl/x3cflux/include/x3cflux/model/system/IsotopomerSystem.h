#ifndef X3CFLUX_ISOTOPOMERSYSTEM_H
#define X3CFLUX_ISOTOPOMERSYSTEM_H

#include "LabelingSystem.h"
#include "MultiHelper.h"
#include "NonLinearElement.h"
#include <math/IVPBase.h>
#include <math/NumericTypes.h>
#include <model/data/Substrate.h>
#include <model/network/LabelingNetwork.h>

#include <utility>

namespace x3cflux {

template <bool Multi = false>
class IsotopomerSystem : public LabelingSystem<IsotopomerMethod, false, Multi>,
                         public IVPBase<typename SystemTraits<IsotopomerMethod, Multi>::SystemStateType> {
  public:
    typedef LabelingSystem<IsotopomerMethod, false, Multi> Base;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    typedef NumericNonLinearElement<IsotopomerMethod, false, Multi> NonLinearElement;
    typedef StateVariableOperations<IsotopomerMethod, Multi> StateVarOps;

  private:
    RealSparseMatrix linearCoefficients_;
    std::vector<NonLinearElement> nonLinearities_;

  public:
    IsotopomerSystem(const RealSparseMatrix &linearCoefficients, std::vector<NonLinearElement> nonLinearities,
                     const SystemState &initialValue, Real endTime, const Solver &solver)
        : Base(solver), IVPBase<SystemState>(0., endTime, initialValue), linearCoefficients_(linearCoefficients),
          nonLinearities_(std::move(nonLinearities)) {}

    const RealSparseMatrix &getLinearCoefficients() const { return linearCoefficients_; }

    const std::vector<NonLinearElement> &getNonLinearities() const { return nonLinearities_; }

    SystemState evaluateNonLinearities(Real time, const SystemState &state) const {
        SystemState eval = SystemState::Zero(this->getSize(), this->getNumStates());
        for (const auto &nonLin : nonLinearities_) {
            StateVarOps::assign(eval, nonLin.getRowIndex(), nonLin.evaluate(time, state));
        }
        return eval;
    }

    SystemState operator()(Real time, const SystemState &state) const override {
        return linearCoefficients_ * state + evaluateNonLinearities(time, state);
    }

    Solution solve() const override { return this->getSolver().solve(*this); }
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERSYSTEM_H
