// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_WORK_THREAD_LIMITS_H
#define PXR_WORK_THREAD_LIMITS_H

#include "pxr/work/pxr.h"
#include "pxr/work/api.h"

WORK_NAMESPACE_OPEN_SCOPE

/// \file work/threadLimits.h

/// Return the current concurrency limit, always >= 1.
///
/// This value is determined by the underlying concurrency subsystem.  It may
/// have been set by a third party, by a call to Work API below, or by Work
/// itself if the PXR_WORK_THREAD_LIMIT env setting was set.  If the
/// PXR_WORK_THREAD_LIMIT env setting has been explicitly set to a non-zero
/// value, Work will attempt to configure the underlying concurrency subsystem
/// to use the specified limit and will ignore concurrency limits set via the
/// API calls below.
///
/// Note that this can return a value larger than
/// WorkGetPhysicalConcurrencyLimit() if WorkSetConcurrencyLimit() was called
/// with such a value, or if PXR_WORK_THREAD_LIMIT was set with such a value.
///
WORK_API unsigned WorkGetConcurrencyLimit();

/// Return the concurrency limit setting, computed from the physical
/// concurrency limit and the PXR_WORK_THREAD_LIMIT env setting. This is the
/// concurrency limit that work will try to implement at startup.
/// The concurrency limit will either be "0", meaning work doesn't try to apply
/// any concurrency limit, or a (normalized) positive number of threads.
WORK_API unsigned WorkGetConcurrencyLimitSetting();

/// Return true if WorkGetPhysicalConcurrencyLimit() returns a number greater
/// than 1 and PXR_WORK_THREAD_LIMIT was not set in an attempt to limit the
/// process to a single thread, false otherwise.
///
WORK_API bool WorkHasConcurrency();

/// Return the number of physical execution cores available to the program.
/// This is either the number of physical cores on the machine or the number of
/// cores specified by the process's affinity mask, whichever is smaller.
///
WORK_API unsigned WorkGetPhysicalConcurrencyLimit();

/// Set the concurrency limit to \p n, if \p n is a non-zero value.
///
/// If \p n is zero, then do not change the current concurrency limit.
///
/// Note, calling this function with n > WorkGetPhysicalConcurrencyLimit() may
/// overtax the machine.
///
/// In general, very few places should call this function.  Call it in places
/// where the number of allowed threads is dictated, for example, by a hosting
/// environment.  Lower-level library code should never call this function.
///
WORK_API void WorkSetConcurrencyLimit(unsigned n);

/// Sanitize \p n as described below and set the concurrency limit accordingly.
/// This function is useful for interpreting command line arguments.
///
/// If \p n is zero, then do not change the current concurrency limit.
///
/// If \p n is a positive, non-zero value then call WorkSetConcurrencyLimit(n).
/// Note that calling this method with \p n greater than the value returned by
/// WorkGetPhysicalConcurrencyLimit() may overtax the machine.
///
/// If \p n is negative, then set the concurrency limit to all but abs(\p n)
/// cores. The number of cores is determined by the value returned by
/// WorkGetPhysicalConcurrencyLimit().
/// For example, if \p n is -2, then use all but two cores.  If abs(\p n) is
/// greater than the number of physical cores, then call
/// WorkSetConcurrencyLimit(1), effectively disabling concurrency.
///
WORK_API void WorkSetConcurrencyLimitArgument(int n);

/// Set the concurrency limit to be the maximum recommended for the hardware
/// on which it's running.  Equivalent to:
/// \code
/// WorkSetConcurrencyLimit(WorkGetPhysicalConcurrencyLimit()).
/// \endcode
///
WORK_API void WorkSetMaximumConcurrencyLimit();

/// Returns true if a limit between 1 and the physical concurrency can be set, 
/// and the implementation will make a best effort to respect the limit.
///
/// Returns false if the implementation can only support 1 or the physical 
/// concurrency. If there is an attempt to set a limit between 1 and the 
/// physical concurrency the limit will default to the physical concurrency.
WORK_API bool WorkSupportsGranularThreadLimits();

WORK_NAMESPACE_CLOSE_SCOPE

#endif
