#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simplified pretty-printing."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2011-2023, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import IPython.lib.pretty


class Pretty:
    """Provide repr/str through IPython's `pretty` module.

    Child classes must implement the `_repr_pretty_` method.

    """

    def pformat(self, pretty, cycle, name=None):
        """Return pretty representation.

        Automatically handles cycles and adds a proper group with the class
        name.

        This is designed to be used on a *with* statement.

        """
        if name is None:
            name = self.__class__.__name__

        if cycle:
            return pretty.text("%s(...)" % name)

        begin = "%s(" % name
        return pretty.group(len(begin), begin, ")")

    def __repr__(self):
        return IPython.lib.pretty.pretty(self)
