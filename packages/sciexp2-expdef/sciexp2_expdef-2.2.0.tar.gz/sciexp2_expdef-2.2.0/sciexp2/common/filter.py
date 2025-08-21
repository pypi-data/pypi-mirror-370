#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse and apply filter expressions."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2024, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import collections.abc
import re
import linecache


def _re_match(value, pattern):
    cre = re.compile(pattern)
    return cre.match(value) is not None


class Filter:
    """Boolean expression to check against a dict-like object.

    The filter contains an arbitrary Python expression, where every variable
    will be taken from the dict we are matching the filter against.


    Parameters
    ----------
    expression : Filter or dict or str, optional
        Expression to use in the filter.


    Raises
    ------
    SyntaxError
        The expression is not valid.


    Notes
    -----
    If `expression` is a dict-like object, it will define an expression that
    exactly matches its items.

    Every filter will have the following global names defined:

    ============================  ==========================
    ``re_match(var, str)``        Check if ``var`` matches the regular
                                  expression ``str``.
    ============================  ==========================


    See also
    --------
    validate
    match
    and_filters, or_filters


    Examples
    --------
    Filters can be easily composed together:

    >>> f1 = Filter("a < 3")
    >>> f2 = Filter("b == 4")
    >>> and_filters(f1, f2)
    Filter("(a < 3) and (b == 4)")
    >>> or_filters(f1, f2)
    Filter("(a < 3) or (b == 4)")

    Filter objects can be later matched against dict-like objects:

    >>> f = Filter("a < 3 and b == 4")
    >>> f.match(dict(a=2, b=4))
    True
    >>> f.match(dict(a=3, b=4))
    False

    Using a dict as an expression is equivalent to building a perfect match for
    the dict's items:

    >>> Filter({"VAR1": 1, "VAR2": 2})
    Filter("VAR1 == 1 and VAR2 == 2")

    """

    _GLOBALS = {"re_match": _re_match}

    def __init__(self, expression=None):
        if expression is None or expression == "":
            expression = "True"
        elif isinstance(expression, Filter):
            # pylint: disable=protected-access
            expression = expression._expression
        elif isinstance(expression, collections.abc.Mapping):
            keys = sorted(expression.keys())
            expression = " and ".join([f"{key} == {repr(expression[key])}"
                                       for key in keys])
        self._expression = expression
        self._code_id = f"<dynamic-{id(self._expression)}>"
        self._code = compile(self._expression, self._code_id, "eval")
        linecache.cache[self._code_id] = (len(self._expression), None,
                                          self._expression.split("\n"),
                                          self._code_id)

    def __del__(self):
        if self._code_id in linecache.cache:
            del linecache.cache[self._code_id]

    def __str__(self):
        """Return a string representation of the filter."""
        return self._expression

    def __repr__(self):
        return f"Filter(\"{str(self)}\")"

    def validate(self, allowed):
        """Validate that variables in the filter are present in the given set.

        Parameters
        ----------
        allowed : set of variable names
            Set of variable names to allow on the filter.

        Raises
        ------
        NameError
            Filter contains a variable name not present in `allowed`.

        """
        present = set(self._code.co_names)
        missing = present - (set(allowed) | set(["re_match"]))
        if missing:
            missing = list(missing)
            raise NameError(f"name {repr(missing[0])} is not allowed")

    def match(self, source):
        """Check if the given `source` matches this filter.

        Parameters
        ----------
        source : dict-like
            Dictionary to match this filter against.

        Returns
        -------
        bool : Whether the match is positive or not.

        Raises
        ------
        NameError
            Filter contains a variable name not present in `source`.

        See also
        --------
        validate

        """
        # pylint: disable=eval-used
        return eval(self._code, dict(source), self._GLOBALS)


def and_filters(*filters):
    """Convenience function to *and* all `filters` together."""
    filters = [f"({Filter(f)})" for f in filters]
    expression = " and ".join(filters)
    return Filter(expression)


def or_filters(*filters):
    """Convenience function to *or* all `filters` together."""
    filters = [f"({Filter(f)})" for f in filters]
    expression = " or ".join(filters)
    return Filter(expression)


__all__ = [
    "Filter", "and_filters", "or_filters",
]
