#ifndef X3CFLUX_LOGGING_H
#define X3CFLUX_LOGGING_H

#include <boost/filesystem.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/expressions/message.hpp>
#include <boost/log/sinks/sync_frontend.hpp>
#include <boost/log/sinks/text_ostream_backend.hpp>
#include <boost/log/trivial.hpp>
#include <boost/make_shared.hpp>
#include <iostream>

#include "AssertionError.h"

namespace x3cflux {

/// Define colored data output format.
/// \param view boost record view from which placeholders can be received
/// \param stream boost formatting ostream to push format to
void color_formatter(const boost::log::record_view &view, boost::log::formatting_ostream &stream);

/// Set up Boost logging framework.
/// \param level default log level
void setup_logger(boost::log::trivial::severity_level level);

} // namespace x3cflux

// Logging macros
#define X3CFLUX_TRACE() BOOST_LOG_TRIVIAL(trace)
#define X3CFLUX_DEBUG() BOOST_LOG_TRIVIAL(debug)
#define X3CFLUX_INFO() BOOST_LOG_TRIVIAL(info)
#define X3CFLUX_WARNING() BOOST_LOG_TRIVIAL(warning)
#define X3CFLUX_ERROR() BOOST_LOG_TRIVIAL(error)

// Basic stringify macros
#define X3CFLUX_STRINGIFY(in) #in
#define X3CFLUX_TOSTRING(in) X3CFLUX_STRINGIFY(in)

#ifdef NDEBUG

// Set log level to info in the release getVersion
#define X3CFLUX_LOG_INIT() x3cflux::setup_logger(boost::log::trivial::warning)

// Release error message without filename and line
#define X3CFLUX_ERR_MSG(message) std::string(message)

// Disable condition check by evaluating it to empty
#define X3CFLUX_CHECK(expression)

#else

// Set log level to debug in the developer getVersion
#define X3CFLUX_LOG_INIT() x3cflux::setup_logger(boost::log::trivial::debug)

// Debug error messages with filename and line
#define __FILENAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)
#define X3CFLUX_ERR_MSG(message) (std::string(message) + " (" + __FILENAME__ + ":" + X3CFLUX_TOSTRING(__LINE__) + ")")

// Check if the specified condition is true.
#define X3CFLUX_CHECK(expression)                                                                                      \
    if (not(expression)) {                                                                                             \
        throw x3cflux::AssertionError(X3CFLUX_ERR_MSG(#expression));                                                   \
    }

#endif

#define X3CFLUX_THROW(type, message) throw type(X3CFLUX_ERR_MSG(message))

#endif // X3CFLUX_LOGGING_H