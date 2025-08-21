#ifndef X3CFLUX_CUMOMERMETHOD_H
#define X3CFLUX_CUMOMERMETHOD_H

#include "CascadeIterator.h"
#include "CascadeOrdering.h"

namespace x3cflux {

/// \brief Cumomer modeling method
///
/// This struct provides implementations to use LabelingNetwork
/// with the cumomer modeling method. It provides an iterator
/// for on-the-fly generation of cumomer network levels and
/// reactions as well as sequential cumomer level ordering.
struct CumomerMethod {
    typedef boost::dynamic_bitset<> StateType;
    typedef CascadeIterator IteratorType;
    typedef CascadeOrdering OrderingType;
};

} // namespace x3cflux

#endif // X3CFLUX_CUMOMERMETHOD_H
