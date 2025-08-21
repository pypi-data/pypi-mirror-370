#ifndef X3CFLUX_TYPECASTS_H
#define X3CFLUX_TYPECASTS_H

#include <FluxML.h>
#include <Python.h>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {
namespace detail {
template <> struct type_caster<flux::symb::ExprTree> {
  public:
    PYBIND11_TYPE_CASTER(flux::symb::ExprTree, const_name("ExprTree"));

    bool load(handle src, bool) {
        PyObject *source = src.ptr();
        PyObject *stringConverter = PyObject_GetAttrString(source, "__str__");
        PyObject *result = PyObject_CallObject(stringConverter, nullptr);
        if (!result) {
            return false;
        }
        std::string expressionString(PyUnicode_AsUTF8(result));
        value = *flux::symb::ExprTree::parse(expressionString.c_str());
        Py_DECREF(result);

        return not PyErr_Occurred();
    }

    static handle cast(const flux::symb::ExprTree &src, return_value_policy /* policy */, handle /* parent */) {
        auto expression_string = src.toString();

        PyObject *sympy = PyImport_ImportModule("sympy");
        if (!sympy) {
            PyErr_Print();
            std::cerr << "Error: could not import module 'sympy'" << std::endl;
        }
        PyObject *parseExpr = PyObject_GetAttrString(sympy, "parse_expr");
        PyObject *args = Py_BuildValue("(s)", expression_string.c_str());
        PyObject *sympyExpr = PyObject_CallObject(parseExpr, args);
        Py_DECREF(args);
        Py_DECREF(parseExpr);

        return sympyExpr;
    }
};

template <> struct type_caster<boost::dynamic_bitset<>> {
  public:
    PYBIND11_TYPE_CASTER(boost::dynamic_bitset<>, const_name("boost::dynamic_bitset<>"));

    bool load(handle src, bool) {
        PyObject *source = src.ptr();
        PyObject *stringConverter = PyObject_GetAttrString(source, "__str__");
        PyObject *result = PyObject_CallObject(stringConverter, nullptr);
        if (!result) {
            return false;
        }
        std::string bitsetString(PyUnicode_AsUTF8(result));
        value = boost::dynamic_bitset<>(bitsetString);
        Py_DECREF(result);

        return not PyErr_Occurred();
    }

    static handle cast(const boost::dynamic_bitset<> &src, return_value_policy /* policy */, handle /* parent */) {
        std::string bitsetString;
        boost::to_string(src, bitsetString);

        PyObject *stringObject = PyUnicode_FromString(bitsetString.c_str());

        return stringObject;
    }
};

template <> struct type_caster<boost::posix_time::ptime> {
  public:
    PYBIND11_TYPE_CASTER(boost::posix_time::ptime, const_name("DateTime"));

    bool load(handle src, bool) {
        PyObject *source = src.ptr();
        PyObject *stringConverter = PyObject_GetAttrString(source, "isoformat");
        PyObject *result = PyObject_CallObject(stringConverter, nullptr);
        if (!result) {
            return false;
        }
        std::string datetimeString(PyUnicode_AsUTF8(result));
        value = boost::posix_time::from_iso_string(datetimeString);
        Py_DECREF(result);

        return not PyErr_Occurred();
    }

    static handle cast(const boost::posix_time::ptime &src, return_value_policy /* policy */, handle /* parent */) {
        auto datetimeString = boost::posix_time::to_iso_extended_string(src);

        PyObject *datetime = PyImport_ImportModule("datetime");
        if (!datetime) {
            PyErr_Print();
            std::cerr << "Error: could not import module 'datetime'" << std::endl;
        }
        PyObject *classDatetime = PyObject_GetAttrString(datetime, "datetime");
        PyObject *parseDatetime = PyObject_GetAttrString(classDatetime, "fromisoformat");
        PyObject *args = Py_BuildValue("(s)", datetimeString.c_str());
        PyObject *datetimeObject = PyObject_CallObject(parseDatetime, args);
        Py_DECREF(args);
        Py_DECREF(classDatetime);
        Py_DECREF(parseDatetime);

        return datetimeObject;
    }
};
} // namespace detail
} // namespace pybind11

#endif // X3CFLUX_TYPECASTS_H
