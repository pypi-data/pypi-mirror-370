#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Progress indicators.

Progress messages are only shown if the provided level is greater than the one
in `level`.

The available levels are: `LVL_NONE`, `LVL_PROGRESS` (the default), `LVL_INFO`,
`LVL_VERBOSE` and `LVL_DEBUG`.

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2024, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import collections
import itertools
import numbers
import os
import sys
import threading
import types

import six
import tqdm


LVL_NONE = 0                      #: No progress indication.
LVL_PROGRESS = 1                  #: Show progress indication.
LVL_INFO = 2                      #: Show additional information.
LVL_VERBOSE = 3                   #: Be verbose when progressing.
LVL_DEBUG = 4                     #: Show debugging information.

_LEVEL = LVL_PROGRESS

if "ipykernel" in sys.modules:
    # we're in a notebook ...
    try:
        import ipywidgets.widgets.widget
        # pylint: disable=protected-access
        if getattr(ipywidgets.widgets.widget.Widget, "_version_validated", None) is not None:
            # ... and widgets are usable
            _CLS = tqdm.tqdm_notebook
        else:
            _CLS = tqdm.tqdm
    #pylint: disable=bare-except
    except:
        _CLS = tqdm.tqdm
else:
    _CLS = tqdm.tqdm


def get_writer(file):
    read_fd, write_fd = os.pipe()

    write_wrapper = os.fdopen(write_fd, "w")
    read_wrapper = os.fdopen(read_fd, "r")

    def reader():
        while True:
            data = read_wrapper.readline()
            if len(data) == 0:
                return
            tqdm.tqdm.write(data, end="", file=file)
    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    return write_wrapper


def level(level_=None):
    """Get/set the current progress indication level."""
    if level_ is not None:
        if level_ < LVL_NONE or LVL_DEBUG < level_:
            raise ValueError(f"Invalid progress level {level_}")
        # pylint: disable=global-statement
        global _LEVEL
        _LEVEL = level_
    return _LEVEL


def _log(fmt, *args):
    with _PRINT_LOCK:
        tqdm.tqdm.write(fmt % (args), file=sys.stderr)

_PRINT_LOCK = threading.Lock()


def log(level_, fmt, *args, **kwargs):
    """Log message with given level."""
    if level_ > _LEVEL:
        return
    _log(fmt, *args, **kwargs)


def info(fmt, *args, **kwargs):
    """Log message with 'info' level."""
    log(LVL_INFO, fmt, *args, **kwargs)


def verbose(fmt, *args, **kwargs):
    """Log message with 'verbose' level."""
    log(LVL_VERBOSE, fmt, *args, **kwargs)


def debug(fmt, *args, **kwargs):
    """Log message with 'debug' level."""
    log(LVL_DEBUG, fmt, *args, **kwargs)


class Progress:
    """A progress indicator.

    Parameters
    ----------
    total : optional
        Objective progress count, or sized object.
    msg : string, optional
        Message to prefix to the progress indicator.

    """

    def __init__(self, total=None, msg=""):
        total = _get_total(total)
        if level() < LVL_PROGRESS:
            self._obj = None
        else:
            self._obj = _CLS(desc=msg, total=total, leave=False, dynamic_ncols=True)

    def __call__(self, increment=1):
        """Increment the progress indicator by the given number."""
        if self._obj is not None:
            self._obj.update(increment)

    def __iadd__(self, other):
        """Increment the total count of the progress indicator."""
        if self._obj.total is None:
            self._obj.total = 0
        self._obj.total += other
        return self


    def _cleanup(self):
        if self._obj is not None:
            self._obj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._cleanup()

    def __del__(self):
        """Delete the progress indicator from screen."""
        self._cleanup()

    def write(self, s, file=None, end="\n", nolock=False):
        if self._obj is not None:
            return self._obj.write(s, file=file, end=end, nolock=nolock)
        else:
            if file is None:
                file = sys.stdout
            return file.write(s, end=end)


class Null:
    """A "null" progress indicator.

    """

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def __iadd__(self, other):
        return self

    def _cleanup(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __del__(self):
        pass

    def write(self, s, file=None, end="\n", nolock=False):
        if file is None:
            file = sys.stdout
        return file.write(s, end=end)


def _progressable_get_func_wrapper(func, other, progr):
    """Update progress every time `func` is called."""
    # pylint: disable=unused-argument
    def wrapper(self, *args, **kwargs):
        res = func(other, *args, **kwargs)
        progr()
        return res
    return wrapper


def _progressable_get_iter_wrapper(func, other, progr):
    """Update progress every time the result of `func` is iterated."""
    # pylint: disable=unused-argument
    def wrapper(self, *args, **kwargs):
        otheriter = func(other, *args, **kwargs)

        counter = set()

        class _ProgressableIterator(other.__class__):
            def __init__(self):
                pass

            def __iter__(self):
                return self

            # pylint: disable=missing-docstring
            def next(self):
                return next(self)

            # pylint: disable=no-self-use
            def __next__(self):
                res = next(otheriter)
                if counter:
                    # must offset progress by one element
                    # (returned element does not finish until we retrieve next)
                    progr()
                else:
                    counter.add(None)
                return res

            def __getattr__(self, attr):
                try:
                    return getattr(otheriter, attr)
                # pylint: disable=bare-except
                except:
                    return getattr(other, attr)

            def __setattr__(self, attr, val):
                setattr(otheriter, attr, val)

        return _ProgressableIterator()
    return wrapper


# pylint: disable=too-few-public-methods
class Progressable:
    """Indicates objects returned by `progressable`."""


def progressable(other, progr, funcs=None, iters=None):
    """Get a wrapper that invokes a progress indicator on some routines.

    Parameters
    ----------
    other
        Object to wrap.
    progr
        A progress indicator instance.
    funcs : list of str, optional
        List of routines in `other` to wrap.
    iters : list of str, optional
        List of routines in `other` that return an interator to wrap.

    Notes
    -----
    Argument `other` is also passed as the first argument to `get`, such that
    it can return a proper indicator.

    """
    if funcs is None:
        funcs = []
    if iters is None:
        iters = []
    assert funcs or iters
    assert len(funcs) + len(iters) == len(set(funcs) | set(iters))

    class _Progressable(other.__class__, Progressable):
        def __init__(self):
            pass

        def __enter__(self):
            progr.__enter__()
            return self

        def __exit__(self, *args, **kwargs):
            progr.__exit__(*args, **kwargs)

        def __getattr__(self, attr):
            return getattr(other, attr)

        def __setattr__(self, attr, val):
            return other.__class__.__setattr__(other, attr, val)

    res = _Progressable()

    for func in itertools.chain(funcs, iters):
        if not hasattr(other, func):
            raise ValueError(f"Routine {func} not found")
        func_orig = getattr(other.__class__, func)
        if func in funcs:
            func_ = _progressable_get_func_wrapper(func_orig, other, progr)
        else:
            func_ = _progressable_get_iter_wrapper(func_orig, other, progr)
        setattr(_Progressable, func, func_)

    return res


def progressable_simple(contents, length, *args, **kwargs):
    """A simplified version of `progressable`.

    Creates a progress indicator from the given arguments.

    """
    if length is None:
        progr = get(contents, *args, **kwargs)
    else:
        progr = get(length, *args, **kwargs)

    if isinstance(contents, types.GeneratorType):
        # pylint: disable=missing-docstring
        class Wrapper(collections.abc.Iterable, collections.abc.Sized):
            def __iter__(self):
                return iter(contents)

            def __len__(self):
                return len(contents)

        res = Wrapper()
    else:
        res = contents

    return progressable(res, progr, iters=["__iter__"])


class Stack:
    """Stack of currently active progress indicators.

    Provides only static attributes and methods, in order to provide a
    program-wide stateful stack of progress indicators.
    """

    _STACK = []
    CURRENT = None
    """The currently active progress indicator."""

    @staticmethod
    def __call__(*args, **kwargs):
        """Call on the current (latest) progress indicator.

        Parameters
        ----------
        args, kwargs
            Arguments for ``__call__`` to the current progress indicator.
        """
        # pylint: disable=not-callable
        Stack.CURRENT(*args, **kwargs)

    @staticmethod
    def push(klass, *args, **kwargs):
        """Add a new progress indicator to the stack and make it current.

        Parameters
        ----------
        klass : callable
            Class object or function to construct the new progress indicator.
        args, kwargs
            Arguments to `klass`.
        """
        if not callable(klass):
            raise TypeError

        if level() < LVL_PROGRESS:
            obj = Null(*args, **kwargs)
        else:
            obj = klass(*args, **kwargs)

        Stack._STACK.append(obj)
        Stack.CURRENT = Stack._STACK[-1]
        return Stack.CURRENT

    @staticmethod
    def pop():
        """Remove the last progress indicator from the stack."""
        assert len(Stack._STACK) > 1
        res = Stack.CURRENT
        Stack._STACK.pop()
        Stack.CURRENT = Stack._STACK[-1]
        return res

# Add a default null progress reporter
Stack.push(Null)


class UnpicklerStart:
    """Picklable proxy to a progress indicator.

    In order to provide a progress indicator when unpickling large objects, you
    can prefix the pickle stream with a `UnpicklerStart` instance and postfix
    it with its `UnpicklerStop` sister instance::

        def dump (self, file_obj):
            start = UnpicklerStart(len(self))
            pickle.dump((start, self, start.get_stop()), file_obj)

    When unpickled, the first will call `Stack.push` and the last will call
    `Stack.pop`, so that your object will be able to update the
    `~Stack.CURRENT` progress indicator by calling `Stack`.

    When pickled, it will also push a progress indicator for your code to use
    while pickling your large object.

    Parameters
    ----------
    obj
        Object to show the progress indicator for
    no_pickle : bool, optional
        Do not create a progress indicator while pickling
    msg_pickle : string, optional
        Message during pickling (otherwise use default)
    no_unpickle : bool, optional
        Do not create a progress indicator while unpickling
    msg_unpickle : string, optional
        Message during unpickling (otherwise use default)togg

    """

    def __init__(self, obj, **kwargs):
        no_pickle = kwargs.pop("no_pickle", False)
        msg_pickle = kwargs.pop("msg_pickle", "saving to file")
        no_unpickle = kwargs.pop("no_unpickle", False)
        msg_unpickle = kwargs.pop("msg_unpickle", "loading from file")
        # pylint: disable=cyclic-import
        # pylint: disable=import-outside-toplevel
        from . import utils
        utils.assert_kwargs(kwargs)

        total = _get_total(obj)

        if no_pickle:
            self._pickle = None
        else:
            cls = _get_class()
            self._pickle = (cls, total, msg_pickle)

        if no_unpickle:
            self._unpickle = None
        else:
            self._unpickle = (Progress, total, msg_unpickle)

    def get_stop(self):
        """Get the sister `UnpicklerStop` object."""
        return UnpicklerStop(self._pickle is not None,
                             self._unpickle is not None)

    def __getstate__(self):
        if self._pickle is not None:
            Stack.push(*self._pickle)
        contents = self.__dict__.copy()
        del contents["_pickle"]
        return contents

    def __setstate__(self, contents):
        self.__dict__.update(contents)
        if self._unpickle is not None:
            cls, total, msg = self._unpickle
            cls = _get_class()
            Stack.push(cls, total, msg)


class UnpicklerStop:
    """Remove the progress indicators created by `UnpicklerStart`."""

    def __init__(self, do_pickle, do_unpickle):
        """
        Parameters
        ----------
        do_pickle, do_unpickle : boolean
            Remove a progress indicator after pickling / unpickling.
        """
        self._pickle = do_pickle
        self._unpickle = do_unpickle

    def __getstate__(self):
        contents = self.__dict__.copy()
        del contents["_pickle"]
        if self._pickle:
            progress = Stack.pop()
            #pylint: disable=protected-access
            progress._cleanup()
        return contents

    def __setstate__(self, contents):
        self.__dict__.update(contents)
        if self._unpickle:
            progress = Stack.pop()
            #pylint: disable=protected-access
            progress._cleanup()


def _get_class():
    if level() >= LVL_PROGRESS:
        return Progress
    return Null


def _get_total(obj):
    if isinstance(obj, six.string_types):
        return None
    if isinstance(obj, collections.abc.Sized):
        return len(obj)
    if isinstance(obj, numbers.Number):
        return obj
    return None


def get(obj, msg=""):
    """Return a progress indicator.

    """
    cls = _get_class()
    return cls(obj, msg)


def get_pickle(obj, **kwargs):
    """Return an object to show a progress indicator during (un)pickling.

    The progress indicator can be reached through Stack.CURRENT.

    Parameters
    ----------
    obj
        Object to show the progress indicator for
    kwargs
        Additional arguments for UnpicklerStart.

    """
    return UnpicklerStart(obj, **kwargs)
