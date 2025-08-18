// Copyright 2025 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_WORK_TBB_SORT_IMPL_H
#define PXR_WORK_TBB_SORT_IMPL_H

#include "pxr/work/pxr.h"

#include <tbb/parallel_sort.h>
#include <algorithm>

WORK_NAMESPACE_OPEN_SCOPE

/// TBB Sort Implementation
///
/// Implements WorkParallelSort
///
template <typename C>
void 
WorkImpl_ParallelSort(C* container)
{
    tbb::parallel_sort(container->begin(), container->end());
}

/// Implements WorkParallelSort with custom comparator
///
template <typename C, typename Compare>
void 
WorkImpl_ParallelSort(C* container, const Compare& comp)
{
    tbb::parallel_sort(container->begin(), container->end(), comp);
}

WORK_NAMESPACE_CLOSE_SCOPE

#endif // PXR_WORK_TBB_SORT_IMPL_H
