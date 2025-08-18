// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_WORK_DETACHED_TASK_H
#define PXR_WORK_DETACHED_TASK_H

/// \file work/detachedTask.h

#include "pxr/work/pxr.h"
#include <pxr/tf/errorMark.h>
#include "pxr/work/api.h"
#include "pxr/work/dispatcher.h"
#include "pxr/work/impl.h"

#include <type_traits>
#include <utility>

WORK_NAMESPACE_OPEN_SCOPE

template <class Fn>
struct Work_DetachedTask
{
    explicit Work_DetachedTask(Fn &&fn) : _fn(std::move(fn)) {}
    explicit Work_DetachedTask(Fn const &fn) : _fn(fn) {}
    void operator()() const {
        TfErrorMark m;
        _fn();
        m.Clear();
    }
private:
    Fn _fn;
};

/// Invoke \p fn asynchronously, discard any errors it produces, and provide
/// no way to wait for it to complete.
template <class Fn>
void WorkRunDetachedTask(Fn &&fn)
{
    using FnType = typename std::remove_reference<Fn>::type;
    Work_DetachedTask<FnType> task(std::forward<Fn>(fn));
    if (WorkHasConcurrency()) {
        PXR_WORK_IMPL_NAMESPACE_USING_DIRECTIVE;
        WorkImpl_RunDetachedTask<Work_DetachedTask<FnType>>(std::move(task));
    }
    else {
        task();
    }
}

WORK_NAMESPACE_CLOSE_SCOPE

#endif // PXR_WORK_DETACHED_TASK_H
