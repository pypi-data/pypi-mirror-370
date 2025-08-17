// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H
#define PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H

#include "pxr/tf/pxr.h"

#include "pxr/tf/spinMutex.h"

TF_NAMESPACE_OPEN_SCOPE

// Helper class for getting the TfScopeDescription stacks as human readable text
// for crash reporting.
class Tf_ScopeDescriptionStackReportLock
{
    Tf_ScopeDescriptionStackReportLock(
        Tf_ScopeDescriptionStackReportLock const &) = delete;
    Tf_ScopeDescriptionStackReportLock &operator=(
        Tf_ScopeDescriptionStackReportLock const &) = delete;
public:
    // Try to lock and compute the report message, waiting up to lockWaitMsec to
    // acquire each lock.  If lockWaitMsec <= 0 do not wait for locks: skip any
    // threads whose lock cannot be acquired immediately.  Destructor unlocks.
    Tf_ScopeDescriptionStackReportLock(int lockWaitMsec = 10);

    // Get the report message.  This could be nullptr if it was impossible to
    // obtain the report.
    char const *GetMessage() const { return _msg; }
    
private:
    TfSpinMutex::ScopedLock _lock;
    char const *_msg;
};

TF_NAMESPACE_CLOSE_SCOPE

#endif // PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H

