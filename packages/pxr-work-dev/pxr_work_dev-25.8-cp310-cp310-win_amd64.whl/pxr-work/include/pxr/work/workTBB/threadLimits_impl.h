// Copyright 2025 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_WORK_TBB_THREAD_LIMITS_IMPL_H
#define PXR_WORK_TBB_THREAD_LIMITS_IMPL_H

#include "pxr/work/pxr.h"

WORK_NAMESPACE_OPEN_SCOPE

/// TBB Thread Limit Implementations

/// Implements WorkGetPhysicalConcurrencyLimit
///
unsigned WorkImpl_GetPhysicalConcurrencyLimit();

/// Implements WorkSetConcurrencyLimit
///
void WorkImpl_SetConcurrencyLimit(unsigned n);

/// Helps implement Work_InitializeThreading
///
void WorkImpl_InitializeThreading(unsigned threadLimit);

/// Implements WorkGetConcurrencyLimit
///
unsigned WorkImpl_GetConcurrencyLimit();

/// Implements SupportsGranularThreadLimits
///
bool WorkImpl_SupportsGranularThreadLimits();

WORK_NAMESPACE_CLOSE_SCOPE

#endif // PXR_WORK_TBB_THREAD_LIMITS_IMPL_H
