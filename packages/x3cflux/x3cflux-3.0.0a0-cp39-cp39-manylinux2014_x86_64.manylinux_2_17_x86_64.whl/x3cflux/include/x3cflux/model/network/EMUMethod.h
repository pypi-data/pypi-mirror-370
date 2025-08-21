#ifndef X3CFLUX_EMUMETHOD_H
#define X3CFLUX_EMUMETHOD_H

#include "CascadeIterator.h"
#include "CascadeOrdering.h"

namespace x3cflux {

/// \brief EMU modeling method
///
/// This struct provides implementations to use LabelingNetwork
/// with the EMU modeling method. It provides an iterator
/// for on-the-fly generation of EMU network levels and
/// reactions as well as sequential EMU level ordering.
struct EMUMethod {
    typedef boost::dynamic_bitset<> StateType;
    typedef CascadeIterator IteratorType;
    typedef CascadeOrdering OrderingType;
};

} // namespace x3cflux

#endif // X3CFLUX_EMUMETHOD_H
