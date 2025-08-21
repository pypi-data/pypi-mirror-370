#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Functions typically used with `~sciexp2.expdef`:

- `~sciexp2.expdef.experiments.Experiments`
- `~sciexp2.expdef.experiments.with_exp`
- `~sciexp2.expdef.experiments.with_exp_tpl`
- `~sciexp2.expdef.experiments.from_function`
- `~sciexp2.expdef.experiments.from_find_files`
- `~sciexp2.common.filter.Filter`
- `~sciexp2.common.filter.and_filters`
- `~sciexp2.common.filter.or_filters`
- `~sciexp2.common.text.TemplateContents`
- `~sciexp2.common.text.TemplatePath`

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2025, Lluís Vilanova"
__license__ = "GPL version 3 or later"


__all__ = []


def _env_add(name, value):
    __all__.append(name)
    globals()[name] = value


def _env_setup():
    from . import experiments
    import sciexp2.common.filter

    _env_add("Experiments", experiments.Experiments)
    _env_add("with_exp", experiments.with_exp)
    _env_add("with_exp_tpl", experiments.with_exp_tpl)
    _env_add("from_function", experiments.from_function)
    _env_add("from_find_files", experiments.from_find_files)
    _env_add("Filter", sciexp2.common.filter.Filter)
    _env_add("and_filters", sciexp2.common.filter.and_filters)
    _env_add("or_filters", sciexp2.common.filter.or_filters)
    _env_add("TemplateContents", sciexp2.common.text.TemplateContents)
    _env_add("TemplatePath", sciexp2.common.text.TemplatePath)

_env_setup()
