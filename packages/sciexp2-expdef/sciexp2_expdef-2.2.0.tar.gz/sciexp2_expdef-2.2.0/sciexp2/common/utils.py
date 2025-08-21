#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Common utility classes and functions."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2023, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import os
import shutil
import signal
import subprocess
import tempfile
import functools
import collections
import weakref
import numpy as np
import six

from . import pp
from . import progress


# -----------------------------

def assert_kwargs(kwargs):
    """Raise an exception if extra keys are present."""
    if kwargs:
        extra = "s" if len(kwargs) > 1 else ""
        raise TypeError("Unexpected argument%s: %s" % (extra,
                                                       ", ".join(kwargs)))

# -----------------------------

def assert_dir(path):
    """Check that given directory exists, otherwise create it."""
    if path != "" and not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            # might be due to concurrent mkdir
            pass


def assert_path(path):
    """Check that given path exists, otherwise create directories."""
    if not path.endswith(os.sep):
        path = os.path.dirname(path)
    assert_dir(path)


def get_path(path):
    """Get path after expanding user and environment variables."""
    path = os.path.expanduser(path)
    return os.path.expandvars(path)


def get_file(path, mod="w"):
    """Open the given file, creating any intermediate directory."""
    dir_path = os.path.dirname(path)
    assert_dir(dir_path)
    return open(path, mod)


def get_tmp_file(mode="w", delete=True):
    """Get a temporal file."""
    return tempfile.NamedTemporaryFile(mode=mode, delete=delete)


with open(os.devnull, "w") as _null:
    _HAVE_RSYNC = subprocess.call(["which", "rsync"], stdout=_null)

if _HAVE_RSYNC == 0:
    def copy_path_rsync(path_from, path_to, preserve=True, dereference=False):
        """Copy contents using rsync."""
        if os.path.isdir(path_from):
            path_from = path_from + os.sep
            assert_path(path_to)
        else:
            assert_path(os.path.dirname(path_to) + os.sep)

        args = "-rptgoD"
        if preserve:
            args += "t"
        if not dereference:
            args += "l"
        else:
            args += "L"
        if subprocess.call(["rsync", args, path_from, path_to]) != 0:
            raise OSError("Error copying files: %s -> %s" % (
                path_from, path_to))

    def _copy_path(*args, **kwargs):
        copy_path_rsync(*args, **kwargs)

else:
    def copy_path_shutil(path_from, path_to, preserve=True, dereference=False):
        """Copy contents using Python's shutil."""
        if os.path.isdir(path_from):
            # NOTE: will fail if destination already exists
            path_from = path_from + os.sep
            assert_path(path_to)
            shutil.copytree(path_from, path_to, symlinks=not dereference)

        else:
            assert_path(os.path.dirname(path_to) + os.sep)
            if os.path.islink(path_from):
                link_to = os.readlink(path_from)
                os.symlink(link_to, path_to)
            else:
                shutil.copy(path_from, path_to)
            if preserve:
                shutil.copymode(path_from, path_to)

    def _copy_path(*args, **kwargs):
        copy_path_shutil(*args, **kwargs)


def copy_path(path_from, path_to, preserve=True, dereference=False):
    """Copy files."""
    _copy_path(path_from, path_to, preserve=preserve, dereference=dereference)

# -----------------------------

def str2num(arg):
    """Return numeric value of a string, if possible."""
    # NOTE: StringConverter barks at non-numeric strings (str/bytes confusion)
    try:
        return np.lib.npyio.StringConverter().upgrade(arg)
    except:
        return arg

# -----------------------------

def _wraps(wrapped):
    return functools.wraps(wrapped=wrapped,
                           assigned=['__doc__'])


class ViewError(Exception):
    """Invalid operation in `OrderedSet` view."""
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class OrderedSet(collections.abc.MutableSet, pp.Pretty):
    """A mutable set preserving order of insertion.

    .. todo::

       All help should come from `~collections.abc.MutableSet` instead of
       using `_wraps`.

    """

    @_wraps(collections.abc.Container.__init__)
    def __init__(self, iterable=None, view_able=False):
        self._view_able = view_able
        if self._view_able:
            self._list = np.array([], dtype=object)
        else:
            self._list = []
        self._set_methods(False)
        self._base = None
        self._views = {}
        self._set = set()
        if iterable is not None:
            self |= iterable

    def set_view_able(self, view_able):
        """Set whether this object can produce "views" from it.

        Objects able to produce views have lower performance when adding new
        elements to them.

        See also
        --------
        OrderedSet.view

        """
        if view_able != self._view_able:
            if view_able:
                self._list = np.array(self._list, dtype=object)
            else:
                if self._views:
                    raise ValueError(
                        "cannot disable 'view_able' when views already exist")
                self._list = list(self._list)
            self._view_able = view_able
            self._set_methods(False)

    def view(self, index):
        """Create a view (sub-set) of this object.

        This object also becomes a view. Modifications to the elements of a view
        will also take effect on all other views of the same object.


        Parameters
        ----------
        index : slice


        See also
        --------
        OrderedSet.set_view_able

        """
        if not self._view_able:
            raise ValueError("the object is not 'view_able'")
        if not isinstance(index, slice):
            raise TypeError("view index must be a slice")

        self._set_methods(True)

        res = OrderedSet([], True)
        # pylint: disable=protected-access
        res._list = self._list[index]
        for elem in res._list:
            res._set.add(elem)
        res._base = self
        res._set_methods(True)

        self._views[id(res)] = weakref.ref(res)

        return res

    def __del__(self):
        if self._base is not None:
            # pylint: disable=protected-access
            del self._base._views[id(self)]

    def _set_methods(self, is_view):
        if self._view_able:
            if is_view:
                self._append = self._append_array_view
                self._remove = self._remove_array_view
                self._pop = self._pop_array_view
            else:
                self._append = self._append_array
                self._remove = self._remove_array
                self._pop = self._pop_array
        else:
            assert not is_view
            self._append = self._append_list
            self._remove = self._remove_list
            self._pop = self._pop_list

    def _append_list(self, value):
        self._list.append(value)

    def _remove_list(self, value):
        if self._base is not None:
            self._base.remove(value)
        else:
            self._list.remove(value)
            for view in six.itervalues(self._views):
                # pylint: disable=protected-access
                view()._list.remove(value)
                view()._set.remove(value)

    def _pop_list(self, index):
        self._list.pop(index)

    def _append_array(self, value):
        self._list = np.append(self._list, value)

    def _remove_array(self, value):
        self._list = np.delete(self._list, np.where(self._list == value))

    def _pop_array(self, index):
        self._list = np.delete(self._list, index)

    # pylint: disable=no-self-use
    def _append_array_view(self, value):
        raise ViewError("cannot append to a view")

    # pylint: disable=no-self-use
    def _remove_array_view(self, value):
        raise ViewError("cannot remove from a view")

    # pylint: disable=no-self-use
    def _pop_array_view(self, index):
        raise ViewError("cannot pop from a view")

    # pylint: disable=invalid-name
    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle):
            p.pretty(list(self._list))

    def __repr__(self):
        return pp.Pretty.__repr__(self)

    def get_index(self, index):
        """Get item at the 'index'th position."""
        return self._list[index]

    def copy(self):
        """Make a shallow copy of this `OrderedSet`."""
        return OrderedSet(self, self._view_able)

    def sorted(self, *args, **kwargs):
        """Same as `sort`, but returns a sorted copy."""
        res = self.copy()
        res.sort(*args, **kwargs)
        return res

    def sort(self, key=None, reverse=False):
        """Sort set in-place.

        Follows the same semantics of Python's built-in `sorted`.

        """
        if self._view_able:
            contents = list(self._list)
        else:
            contents = self._list

        contents.sort(key=key, reverse=reverse)

        if self._view_able:
            self._list[:] = contents

    # Container

    @_wraps(set.__contains__)
    def __contains__(self, key):
        return key in self._set

    # Sized

    @_wraps(set.__len__)
    def __len__(self):
        return len(self._list)

    # Iterable

    @_wraps(set.__iter__)
    def __iter__(self):
        return iter(self._list)

    # MutableSet

    # pylint: disable=missing-docstring
    def add(self, key):
        old_length = len(self._list)
        self._set.add(key)
        if len(self._set) != old_length:
            try:
                self._append(key)
            except ViewError:
                self._set.remove(key)
                raise
    add.__doc__ = collections.abc.MutableSet.add.__doc__

    # pylint: disable=missing-docstring
    def discard(self, key):
        old_length = len(self._list)
        self._set.remove(key)
        if len(self._set) != old_length:
            try:
                self._remove(key)
            except ViewError:
                self._set.add(key)
                raise
    discard.__doc__ = collections.abc.MutableSet.discard.__doc__
    discard.__doc__ += "\n\nThis operation has a cost of O(n)."

    # pylint: disable=missing-docstring
    @_wraps(collections.abc.MutableSet.pop)
    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self._pop(-1) if last else self._pop(0)
        self._set.remove(key)
        return key

    # Pickling

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["_append"]
        del odict["_remove"]
        del odict["_pop"]
        del odict["_base"]
        del odict["_views"]
        return odict

    def __setstate__(self, odict):
        self.__dict__.update(odict)
        self._base = None
        self._views = {}
        self._set_methods(False)


# -----------------------------

def _template_get_initial_dir(template, template_is_abs):
    # pylint: disable=cyclic-import
    from . import text

    start_dir = ""
    for part in template.split(os.sep):
        if part == "":
            continue
        if start_dir == "" and not template_is_abs:
            cur_dir = part
        else:
            cur_dir = os.sep.join([start_dir, part])
        try:
            text.translate(cur_dir, {})
        except text.VariableError:
            break
        if os.path.isdir(cur_dir):
            start_dir = cur_dir
        else:
            break
    return start_dir


def find_files(template, path=None, absolute_path=False, sort=True):
    """Find files matching a given template.

    Returns an 'InstanceGroup' with all paths of existing files matching the
    given template. Each matching file path is an `Instance` with the extracted
    variables in the `template`.

    Parameters
    ----------
    template : str
        Template of file paths to find.
    path : str, optional
        On each resulting Instance, add a variable with the given name with the
        file path.
    absolute_path : bool, optional
        Make the value in `path` absolute.
    sort : bool, optional
        Sort the file paths according to the alphanumeric order of each of the
        variables in `template`, in that specific order.

    Raises
    ------
    ValueError
        The variable in `path` is already present in `template`.

    See Also
    --------
    sciexp2.common.text.extract
        Argument `template` is interpreted following the extraction syntax.

    Notes
    -----
    If `template` ends with ``/`` it will search for matching paths, and will
    search for matching files otherwise.

    Environment variables and user home directories in `template` will be expanded.

    """
    # pylint: disable=cyclic-import
    from . import text
    from .instance import InstanceGroup, Instance

    if not isinstance(template, six.string_types):
        raise ValueError("Not an expression: " + template)
    if path is not None and not isinstance(path, six.string_types):
        raise ValueError("path must be either None or a string")
    if path in text.get_variables(template):
        raise ValueError("path variable is already present in template")

    template_is_dir = template[-1] == "/" if template else False
    template_is_abs = os.path.isabs(template)
    template = get_path(template) + "$"
    start_dir = _template_get_initial_dir(template, template_is_abs)

    extractor = text.Extractor(template)
    res = InstanceGroup()

    def add(env, target_path):
        # use numbers whenever possible (for later number-aware sorting)
        for key, val in six.iteritems(env):
            env[key] = str2num(val)
        if path is not None:
            if absolute_path:
                target_path = os.path.abspath(target_path)
            env[path] = target_path
        res.add(Instance(env))

    for dir_path, _, file_list in os.walk(start_dir):
        if template_is_dir:
            try:
                env = extractor.extract(dir_path + os.path.sep)
            except text.ExtractError:
                pass
            else:
                add(env, dir_path)
        else:
            for file_path in file_list:
                target_path = os.path.join(dir_path, file_path)
                try:
                    env = extractor.extract(target_path)
                except text.ExtractError:
                    pass
                else:
                    add(env, target_path)

    if sort:
        # sort result according to file sorting
        variables = text.get_variables(template)
        res.sort(variables)

    return res


# -----------------------------

def execute_with_sigint(cmd, **kwargs):
    """Execute a command and forward SIGINT to it.

    Parameters
    ----------
    cmd : list of string
        Command to execute
    kwargs : dict
        Additional arguments to subprocess.Popen.

    Returns
    -------
    Integer with the command's return code.

    """
    preexec_fn = kwargs.pop("preexec_fn", None)
    def preexec():
        os.setpgrp()
        if preexec_fn:
            preexec_fn()

    signals = [
        ("SIGINT", signal.SIGINT),
        ("SIGTERM", signal.SIGTERM),
        ("SIGKILL", signal.SIGKILL),
    ]

    state = dict(proc=None,
                 error=False,
                 signal_idx=0)

    def run():
        if state["proc"] is None:
            if not state["error"]:
                # pylint: disable=subprocess-popen-preexec-fn
                state["proc"] = subprocess.Popen(cmd, preexec_fn=preexec, **kwargs)
            else:
                return
        state["proc"].wait()

    def run_with_except(depth=0):
        try:
            run()
        except KeyboardInterrupt:
            state["error"] = True
            info = signals[state["signal_idx"]]
            progress.log(progress.LVL_NONE,
                         "WARNING: Interrupting child command with %s" % info[0])
            state["proc"].send_signal(info[1])
            if state["signal_idx"] < len(signals) - 1:
                state["signal_idx"] += 1
            run_with_except(depth + 1)
            if depth == 0:
                raise

    run_with_except()
    return state["proc"].returncode
