#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Support for instances and associated abstractions."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2024, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import collections
import contextlib
import pickle
import weakref

from .filter import Filter
from . import progress
from . import utils
from . import pp


_EXPORT = [set()]

_INVALID = object()


class Instance(dict, pp.Pretty):
    """A map from variable names to values."""

    def __init__(self, source=None):
        """
        Parameters
        ----------
        source : :class:`dict` or ``None``
            Initial values for this instance.

        """
        if source is None:
            dict.__init__(self)
        else:
            dict.__init__(self, source)
        setattr(self, "__translate_cache", {})
        setattr(self, "__translate_cache_enabled", False)

    @contextlib.contextmanager
    def auto_translate(self):
        setattr(self, "__translate_cache_enabled", True)
        yield
        setattr(self, "__translate_cache_enabled", False)

    def __getitem__(self, key):
        if not getattr(self, "__translate_cache_enabled"):
            return dict.__getitem__(self, key)

        cache = getattr(self, "__translate_cache")
        val = cache.get(key, _INVALID)
        if val is _INVALID:
            val = dict.__getitem__(self, key)
            if isinstance(val, str):
                from . import text
                try:
                    val = text.translate(val, self, recursive=True)
                except text.VariableError:
                    pass
            cache[key] = val
        return val

    def __setitem__(self, key, val):
        getattr(self, "__translate_cache").clear()
        return dict.__setitem__(self, key, val)

    def __hash__(self):
        """Hashing function for adding into `InstanceGroup`."""
        return id(self)

    def __iter__(self):
        """Get an iterator to ``(key, value)`` pairs in the Instance."""
        return iter(dict.items(self))

    def copy(self):
        """Return a shallow copy of self."""
        return Instance(self)

    def deepcopy(self, *keys):
        """Return a copy of self, deepcopying the values of given keys."""
        res = Instance(self)
        for key in keys:
            res[key] = self[key].__class__(self[key])
        return res

    # pylint: disable=invalid-name
    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle):
            with p.group(1, "{", "}"):
                for idx, (var, val) in enumerate(sorted(self.items())):
                    if idx:
                        p.text(",")
                        p.breakable()
                    p.pretty(var)
                    p.text(": ")
                    # p.breakable()
                    p.pretty(val)

    def __repr__(self):
        return pp.Pretty.__repr__(self)

    def __getstate__(self):
        # pylint: disable=not-callable
        progress.Stack.CURRENT()
        if not _EXPORT[-1]:
            odict = self.__dict__
        else:
            odict = {}
            for key, val in self.items():
                if key in _EXPORT[-1]:
                    odict[key] = val
        return odict

    def __reduce__(self):
        # pylint: disable=not-callable
        progress.Stack.CURRENT()
        if not _EXPORT[-1]:
            odict = dict(self)
        else:
            odict = {}
            for key in _EXPORT[-1]:
                val = self.get(key, _INVALID)
                if val is not _INVALID:
                    odict[key] = val
        return tuple([Instance, tuple(), odict])

    def __setstate__(self, contents):
        # pylint: disable=not-callable
        progress.Stack.CURRENT()
        self.update(contents)


class ViewError(Exception):
    """Invalid operation in an `InstanceGroup` view."""
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class InstanceGroup(pp.Pretty):
    """A group of `Instance` objects suitable for searching.

    Provides a fast way to retrieve a set of Instance objects that have certain
    variables set or certain variable values.

    Parameters
    ----------
    instances : iterable of Instance objects, optional
        Initial contents. Contents are copied during initialization.
    cache, cache_proactive, cache_others
        Arguments to `cache_set`.
    view_able : bool, optional
        Whether to enable the use of `view`.

    See also
    --------
    cache_set

    Notes
    -----
    .. warning::

       You should **not** modify the results of accessing an InstanceGroup,
       unless you know what you're doing.

       As this operation returns the same data being used internally, changes
       to it must be kept consistent with the cache (see `cache_reset`).

    .. warning::

       You should **not** add or extend a group with instances that have the
       same contents as other instances already present in the group.

       .. todo:: An `InstanceGroup` should mimic an `OrderedSet`

    Examples
    --------
    >>> g = InstanceGroup([{'a':4, 'b':3}, {'a':2, 'b':1}, {'a':4}])
    >>> g
    InstanceGroup([Instance({'a': 4, 'b': 3}),
                   Instance({'a': 2, 'b': 1}),
                   Instance({'a': 4})])

    Testing the existence of variables:

    >>> 'a' in g
    True
    >>> 'c' in g
    False

    Getting all the possible values for a variable:

    >>> g['a']                          # doctest: +NORMALIZE_WHITESPACE
    OrderedDict({4: OrderedSet([Instance({'a': 4, 'b': 3}), Instance({'a': 4})]),
                 2: OrderedSet([Instance({'a': 2, 'b': 1})])})
    >>> g['b']                          # doctest: +NORMALIZE_WHITESPACE
    OrderedDict({3: OrderedSet([Instance({'a': 4, 'b': 3})]),
                 1: OrderedSet([Instance({'a': 2, 'b': 1})])})

    Getting all the instances with a specific value:

    >>> g['a'][4]                          # doctest: +NORMALIZE_WHITESPACE
    OrderedSet([Instance({'a': 4, 'b': 3}), Instance({'a': 4})])

    Extending a group with another:

    >>> h = InstanceGroup([{'a':1}, {'a':2}])
    >>> h
    InstanceGroup([Instance({'a': 1}), Instance({'a': 2})])
    >>> g + h
    InstanceGroup([Instance({'a': 4, 'b': 3}),
                   Instance({'a': 2, 'b': 1}),
                   Instance({'a': 4}),
                   Instance({'a': 1}),
                   Instance({'a': 2})])
    >>> g += h
    >>> g
    InstanceGroup([Instance({'a': 4, 'b': 3}),
                   Instance({'a': 2, 'b': 1}),
                   Instance({'a': 4}),
                   Instance({'a': 1}),
                   Instance({'a': 2})])
    >>> g['a']                          # doctest: +NORMALIZE_WHITESPACE
    OrderedDict({4: OrderedSet([Instance({'a': 4, 'b': 3}), Instance({'a': 4})]),
                 2: OrderedSet([Instance({'a': 2, 'b': 1}), Instance({'a': 2})]),
                 1: OrderedSet([Instance({'a': 1})])})

    """

    def __init__(self, instances=None, cache=True,
                 cache_proactive=False, cache_others=None,
                 view_able=False):
        self._view_able = view_able
        self._base = None
        self._views = {}
        self._instances = utils.OrderedSet(view_able=self._view_able)
        self._reverse = dict()

        self._cache = True
        self._cache_proactive = False
        self._cache_others = None
        self.cache_set(cache, cache_proactive, cache_others)

        if instances is not None:
            for i in instances:
                self.add(Instance(i))

    def set_view_able(self, view_able):
        """Set whether this object can produce "views" from it.

        Objects able to produce views have lower performance when adding new
        elements to them.


        See also
        --------
        InstanceGroup.view

        """
        self._instances.set_view_able(view_able)
        self._view_able = view_able

    def view(self, index):
        """Create a view (sub-set) of this object.

        This object also becomes a view. Modifications to the elements of a view
        will also take effect on all other views of the same object.


        Parameters
        ----------
        index : slice


        See also
        --------
        InstanceGroup.set_view_able

        """
        if not self._view_able:
            raise ValueError("the object is not 'view_able'")
        if not isinstance(index, slice):
            raise TypeError("view index must be a slice")

        res = InstanceGroup([], cache=self._cache,
                            cache_proactive=self._cache_proactive,
                            cache_others=self._cache_others, view_able=True)
        # pylint: disable=protected-access
        res._instances = self._instances.view(index)
        res._reverse = dict(self._reverse)
        res.cache_reset()
        res.add = self._add_view
        self.add = self._add_view
        res._base = self
        self._views[id(self)] = weakref.ref(res)
        return res

    def copy(self):
        """Return a copy."""
        return InstanceGroup(self,
                             cache=self._cache,
                             cache_proactive=self._cache_proactive,
                             cache_others=self._cache_others,
                             view_able=self._view_able)

    def get_index(self, index):
        """Get instance at the  `index`'th position."""
        return self._instances.get_index(index)

    # pylint: disable=no-self-use,unused-argument,method-hidden
    def add(self, instance):
        """Add an `Instance` into this group.

        The caching state will have an impact on the performance of this
        operation.

        See also
        --------
        cache_set

        """
        # actual function set by `_set_cache_proactive`
        assert False

    def _set_cache_proactive(self, proactive, others=None):
        if isinstance(proactive, bool):
            if self._cache_proactive:
                self.add = self._add_cache_all
            else:
                self.add = self._add_cache_none

        else:
            if not proactive and others is None:
                self.add = self._add_cache_direct
            elif others is None:
                proactive = set(proactive)
                self.add = self._add_cache_list
            else:
                for var in others:
                    self._cache_reset(var)
                proactive = tuple(proactive)
                if not proactive:
                    self.add = self._add_cache_direct
                else:
                    self.add = self._add_cache_list_only

            prefetch = [var for var in proactive
                        if var in set(self.variables())]
            self.cache_prefetch(prefetch, skip_cached=False)

        self._cache_proactive = proactive
        self._cache_others = others

    # pylint: disable=no-self-use
    def _add_view(self, instance):
        raise ViewError("cannot add to a view")

    def _add_cache_direct(self, instance):
        assert isinstance(instance, Instance)
        self._instances.add(instance)

    def _add_cache_all(self, instance):
        assert isinstance(instance, Instance)
        self._instances.add(instance)
        for key, val in instance:
            self._cache_add(key, val, instance)

    def _add_cache_none(self, instance):
        assert isinstance(instance, Instance)
        self._instances.add(instance)
        # just initialize existence of variables
        for key, _ in instance:
            self._cache_reset(key)

    def _add_cache_list(self, instance):
        assert isinstance(instance, Instance)
        self._instances.add(instance)
        for key, val in instance:
            if key in self._cache_proactive:
                self._cache_add(key, val, instance)
            else:
                self._cache_reset(key)

    def _add_cache_list_only(self, instance):
        assert isinstance(instance, Instance)
        self._instances.add(instance)
        for k in self._cache_proactive:
            self._cache_add(k, instance[k], instance)

    def __iadd__(self, obj):
        """Extend this group with one more instance or group.

        .. todo::

           Should probably delete extension with instances.

        """
        try:
            self.add(obj)
        # pylint: disable=broad-except
        except Exception:
            if not isinstance(obj, Instance):
                self.extend(obj)
            else:
                raise
        return self

    def extend(self, instances):
        """Extend this group with the contents of another group."""
        assert isinstance(instances, InstanceGroup)
        for instance in instances:
            self.add(instance)

    def __add__(self, instances):
        """x.__add__(y) <==> x + y

        Equivalent to a new `InstanceGroup` extended with both groups.

        """
        res = InstanceGroup(self)
        res.extend(instances)
        return res

    def __contains__(self, variable):
        """Syntax sugar for `has_variable`."""
        return variable in self._reverse

    def has_variable(self, variable):
        """Whether the group contains any Instance with given variable name."""
        return variable in self._reverse

    def has_instance(self, instance):
        """Whether this group contains the given Instance."""
        return instance in self._instances

    def variables(self):
        """The sequence of variables in this group."""
        return self._reverse.keys()

    def __getitem__(self, var):
        """Get all values for the given variable."""
        res = self._reverse[var]
        if res is None:  # JIT caching
            res = collections.OrderedDict()
            for instance in self._instances:
                try:
                    val = instance[var]
                except KeyError:
                    continue
                try:
                    vals = res[val]
                except KeyError:
                    vals = utils.OrderedSet()
                    res[val] = vals
                vals.add(instance)
            if self._cache:
                self._reverse[var] = res
        return res

    def _cache_add(self, key, value, instance):
        try:
            keys = self._reverse[key]
        except KeyError:
            keys = collections.OrderedDict()
            self._reverse[key] = keys

        try:
            vals = keys[value]
        except TypeError:               # 'key' uncached
            keys = collections.OrderedDict()
            self._reverse[key] = keys
            vals = utils.OrderedSet()
            keys[value] = vals
        except KeyError:                # 'value' not present
            vals = utils.OrderedSet()
            keys[value] = vals

        vals.add(instance)

    def _cache_reset(self, key):
        self._reverse[key] = None

    def cache_get(self):
        """Get the caching state."""
        return self._cache

    def cache_set(self, enable, proactive=None, others=None):
        """Set the caching status for this group.

        Caching offers greater speed of getting a specific variable multiple
        times (e.g., ``g['a']``), at the expense of a higher memory footprint.

        Parameters
        ----------
        enable : bool
           Caching status. When the caching is disabled, automatically calls
           `cache_reset`.
        proactive : bool or sequence of variable names, optional
           Proactively cache slected variables when adding new instances
           (default is to keep last value).
        others : sequence of variable names, optional
           List of other variables that the group does/will contain (default is
           to keep last value).

        See also
        --------
        cache_get, cache_reset, cache_prefetch

        Notes
        -----
        If caching is disabled, every call to `add` will reset the cache for
        the variables of the added instance.

        If `proactive` is `True`, it will proactively cache all variables, if
        it is `False` it will not. If it is a sequence of variable names, only
        these variables will be proactively cached.

        You can also provide an empty `proactive` list and an appropriate
        `others` list to get zero-caching during instance addition, which is
        the fastest option available.

        .. warning ::

           Providing `others` will greatly enhance the performance of `add`,
           but the contents will be inconsistent if `others` does not contain
           exactly all the variables of the instances previously present or
           added before interacting with the group.

           You can use `cache_reset` with the `hard` argument to ensure
           consistency.

        """
        assert isinstance(enable, bool)
        if proactive is not None:
            if enable is False:
                raise ValueError("Cannot use proactive caching when "
                                 "caching is disabled")
            if not isinstance(proactive, bool) and (
                    not isinstance(proactive, collections.abc.Iterable) or
                    not all([isinstance(elem, str) for elem in proactive])):
                raise TypeError("Invalid `proactive` caching "
                                "value: %s" % proactive)
        if others is not None:
            if proactive is None:
                raise ValueError(
                    "Cannot use 'others' without proactive caching")
            if not isinstance(others, bool) and (
                    not isinstance(others, collections.abc.Iterable) or
                    not all([isinstance(elem, str) for elem in others])):
                raise TypeError("Invalid `others` caching "
                                "value: %s" % others)

        if self._cache != enable:
            self._cache = enable
            if not enable:
                self.cache_reset()

        if proactive is not None:
            self._set_cache_proactive(proactive, others)

    def cache_reset(self, hard=False):
        """Reset the cache of this group.

        Parameters
        ----------
        hard : bool optional
            Perform a costly "hard" cache reset by inspecting all instances in
            the group.

        See also
        --------
        cache_get, cache_set

        """
        if hard:
            self._reverse = dict()
            for instance in self._instances:
                for var in instance.keys():
                    self._cache_reset(var)
        else:
            for var in self._reverse.keys():
                self._cache_reset(var)

    def cache_prefetch(self, variables=None, skip_cached=True):
        """Enable caching and force it for the given variables.

        Parameters
        ----------
        variables : sequence of variable names, optional
            Variables to prefetch. Uses all variables when ``None``.
        skip_cached : bool, optional
            Do not recompute caching if a variable is already cached.

        See also
        --------
        cache_get, cache_set

        Notes
        -----
        When prefetching a variable that is already cached, not necessarily all
        its values will be present on the cache (only those previously
        referenced); thus the `skip_cached` argument.

        """
        self._cache = True

        # select variables
        if variables is None:
            variables = self.variables()
        else:
            self_variables = list(self.variables())
            for var in variables:
                if var not in self_variables:
                    raise ValueError("No such variable: '%s'" % var)

        # uncache variables to be cached
        variables = set(variables)
        for var in set(variables):
            if self._reverse[var] is not None and skip_cached:
                variables.remove(var)
            else:
                self._cache_reset(var)

        # start caching
        if not variables:
            return
        for instance in self._instances:
            for var in variables:
                if var not in instance:
                    continue
                self._cache_add(var, instance[var], instance)

    def __len__(self):
        """The number of instances in this group."""
        return len(self._instances)

    def __iter__(self):
        """An iterator to the instances in the group."""
        return iter(self._instances)

    def select(self, filter_, allow_unknown=False):
        """Generate a sequence of instances matching the given filter.

        Parameters
        ----------
        filter_ : filter
            Filter establishing which instances to select from this group
            (accepts anything convertible into a filter).
        allow_unknown : bool or callable, optional
            Whether to allow the filter to reference variables not present in
            all instances of the group (in which case the instance is not
            selected). If a callable is used, it will receive the instance and
            its result will be used.

        """
        filter_ = Filter(filter_)
        def generate(instances):
            for instance in instances:
                try:
                    match = filter_.match(instance)
                except NameError:
                    if callable(allow_unknown):
                        if not allow_unknown(instance):
                            raise
                    elif not bool(allow_unknown):
                        raise
                else:
                    if match:
                        yield instance
        return generate(self._instances)

    def sorted(self, *args, **kwargs):
        """Same as `sort`, but returns a sorted copy."""
        res = self.copy()
        res.sort(*args, **kwargs)
        return res

    def sort(self, variables, key=None):
        """Sort group in-place by the given variables.

        Parameters
        ----------
        variables : list of strings
            Variable names for which to sort their values. The instances are
            sorted according to the order of the given variable names.
        key : func, optional
            Function returning a value that will be used for comparison. By
            default compares all instance variables as a list.

        See also
        --------
        functools.cmp_to_key

        """
        # get list of all variables in group
        variables = list(variables)
        for var in self.variables():
            if var not in variables:
                variables.append(var)

        if key is None:
            # transform values into a list, sorted according to `variables`
            def to_list(instance):
                return tuple(instance[var] for var in variables)
            key = to_list

        self._instances.sort(key=key)

    # pylint: disable=invalid-name
    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle):
            p.pretty(list(self._instances))

    #######################################################################
    # pickling
    #######################################################################

    def dump(self, file_obj, export=None):
        """Write a pickled representation.

        Parameters
        ----------
        file_obj : file
            The destination file.
        export : set of strings, optional
            Variables that must be exported. Defaults to all.

        See also
        --------
        pickle

        """
        if export is None:
            export = set()
        _EXPORT.append(set(export))
        start = progress.get_pickle(self)
        stop = start.get_stop()
        pickle.dump((start, self, stop), file_obj, -1)
        _EXPORT.pop()

    def __getstate__(self):
        odict = self.__dict__.copy()
        new_reverse = dict()
        for key in odict["_reverse"]:
            if not _EXPORT[-1] or key in _EXPORT[-1]:
                new_reverse[key] = None
        odict["_reverse"] = new_reverse
        if "add" in odict:
            del odict["add"]
        del odict["_base"]
        del odict["_views"]
        return odict

    @staticmethod
    def load(file_obj):
        """Load a pickled representation.

        See also
        --------
        pickle

        """
        _, res, _ = pickle.load(file_obj)
        assert isinstance(res, InstanceGroup)
        return res

    def __setstate__(self, odict):
        self.__dict__.update(odict)
        self._base = None
        self._views = {}
        self._set_cache_proactive(self._cache_proactive, self._cache_others)


__all__ = [
    "Instance",
    "ViewError", "InstanceGroup",
]
