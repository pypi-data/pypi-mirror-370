// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/tf/pxr.h"
#include "pxr/tf/error.h"

#include "pxr/tf/diagnosticMgr.h"

#include <string>

using std::string;

TF_NAMESPACE_OPEN_SCOPE

TfError::TfError(TfEnum errorCode, const char* errorCodeString,
                 TfCallContext const &context, const string& commentary, 
                 TfDiagnosticInfo info, bool quiet)
    : TfDiagnosticBase(errorCode, errorCodeString, context, commentary, info,
                       quiet)
{
    _serial = TfDiagnosticMgr::GetInstance()._nextSerial.fetch_add(1);
}

TF_NAMESPACE_CLOSE_SCOPE
