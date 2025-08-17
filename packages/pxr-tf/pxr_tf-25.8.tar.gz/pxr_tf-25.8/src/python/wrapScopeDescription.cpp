// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include <pxr/tf/pxr.h>

#include <pxr/tf/scopeDescription.h>
#include <pxr/tf/pyResultConversions.h>

#include <pxr/boost/python/class.hpp>
#include <pxr/boost/python/def.hpp>
#include <pxr/boost/python/return_arg.hpp>
#include <pxr/boost/python/return_value_policy.hpp>

#include <memory>
#include <string>

using std::string;
using std::vector;

TF_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

namespace {

// This class exposes TfScopeDescription to Python clients as a context
// manager and a decorator.
//
// This class uses a small helper that holds a TfScopeDescription because
// TfScopeDescription declares, but doesn't define, the ordinary new/delete
// operators to help prevent clients from creating them on the heap.
//
// It's wrapped as a private class because we extend it using the
// ContextDecorator mixin on the Python side (see __init__.py).
class Tf_PyScopeDescription
{
    // This is used to avoid new/delete on TfScopeDescription directly, which is
    // disallowed.
    struct _Holder {
        explicit _Holder(string const &description)
            : _scopeDescription(description) {}
        TfScopeDescription _scopeDescription;
    };

public:

    // Construct with a description string.
    Tf_PyScopeDescription(string const &description) :
        _description(description) {}

    // Enter creates a description object, pushing onto the stack.
    void __enter__() {
        _descriptionHolder.reset(new _Holder(_description));
    }

    // Exit destroys the scope description, popping from the stack.
    void __exit__(object, object, object) {
        _descriptionHolder.reset();
    }

    void SetDescription(const string& description) {
        _description = description;
        if (_descriptionHolder) {
            _descriptionHolder->_scopeDescription.SetDescription(_description);
        }
    }

private:

    std::unique_ptr<_Holder> _descriptionHolder;
    string _description;
};

} // anonymous namespace 

void wrapScopeDescription()
{
    def("GetCurrentScopeDescriptionStack",
        TfGetCurrentScopeDescriptionStack,
        return_value_policy<TfPySequenceToList>());

    typedef Tf_PyScopeDescription This;

    class_<This, noncopyable>("_ScopeDescription", init<string>())
        .def("__enter__", &This::__enter__, return_self<>())
        .def("__exit__", &This::__exit__)
        .def("SetDescription", &This::SetDescription)
        ;
}
