#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Automate generation of parametrized launchers."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2025, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import collections
import contextlib
import concurrent
import functools
import itertools
import operator
import os
import shutil
import six
import sys
import threading
import warnings

from sciexp2.common import progress
from sciexp2.common import utils
from sciexp2.common.instance import InstanceGroup, Instance
from sciexp2.common.filter import *
from sciexp2.common.utils import execute_with_sigint
from sciexp2.common import pp
from sciexp2.common import text
from . import templates
from . import launcher


class _sorted_dict(object):
    """Helper class to print dicts with sorted keys."""
    def __init__(self, object):
        self._object = object
    def __repr__(self):
        keys = sorted(self._object.keys())
        return "{%s}" % ", ".join("%r: %r" % (key, self._object[key])
                                  for key in keys)

def get_executor_workers(parallel):
    if not parallel:
        return 1
    elif parallel is True:
        return os.cpu_count()
    else:
        return parallel


######################################################################
# Experiments

def _is_dummy(experiments):
    if isinstance(experiments, Experiments):
        return (len(experiments._experiments) == 1 and
                len(experiments._experiments.get_index(0)) == 0)
    else:
        return len(experiments) == 1 and len(experiments[0]) == 0


def _val_is_translate(val):
    return (isinstance(val, six.string_types) and
            len(text.get_variables(val)) > 0) or \
            isinstance(val, _WithExp) or \
            isinstance(val, _WithExpTpl)


def _get_translate_exp(exp):
    res = utils.OrderedSet()
    for key, vals in exp.items():
        if isinstance(vals, six.string_types):
            if _val_is_translate(vals):
                res.add(key)
        elif isinstance(vals, collections.abc.Iterable):
            if any(_val_is_translate(val) for val in vals):
                res.add(key)
    return res

def _get_translate(experiments):
    translate = utils.OrderedSet()
    for exp in experiments:
        translate |= _get_translate_exp(exp)
    return translate


def _do_execute(experiments, cmd, **kwargs):
    if len(experiments) == 0:
        experiments_list = [Instance()]
    else:
        experiments_list = experiments

    if isinstance(cmd, six.string_types):
        is_shell = True
        cmd = [cmd]
    else:
        is_shell = False

    parallel = kwargs.pop("parallel", None)
    repeat = kwargs.pop("repeat", "warn")
    if repeat not in ["ignore", "warn", "error"]:
        raise ValueError("invalid repeat value: %r" % repeat)
    std_args = {
        'stdin':  kwargs.pop("stdin",  None),
        'stdout': kwargs.pop("stdout", None),
        'stderr': kwargs.pop("stderr", None),
    }
    utils.assert_kwargs(kwargs)

    def std_translator(name):
        arg = std_args[name]
        if isinstance(arg, six.string_types):
            return text.Translator(arg)
        else:
            return None
    std_translator = {
        'stdin':  std_translator('stdin'),
        'stdout': std_translator('stdout'),
        'stderr': std_translator('stderr'),
    }


    # flatten command to get faster translation
    cmd_arg_sep = "|;argsep;|"
    cmd_flat = cmd_arg_sep.join(cmd)
    def get_cmd(cmd):
        return cmd.split(cmd_arg_sep)

    translator = text.Translator(cmd_flat)
    exp_cmds = translator.translate_many(experiments_list, with_envs=True)

    def execute(exp_cmd, progr):
        cmd = get_cmd(exp_cmd[0])
        exp = exp_cmd[1][0]
        exp_rest = exp_cmd[1][1:]

        progress.verbose(" ".join(cmd))
        if len(exp_rest) > 0:
            if repeat == "warn":
                warnings.warn(
                    "Repeated command translation for experiments %r and %r" % (
                        exp, exp_rest[0]))
            elif repeat == "error":
                raise RuntimeError(
                    "repeated command translation for experiments %r and %r" % (
                        exp, exp_rest[0]))


        def get_stdfile(name, env):
            @contextlib.contextmanager
            def as_context(arg):
                yield arg

            translator = std_translator[name]
            if translator is None and name == "stdout":
                return progress.get_writer(sys.stdout)
            elif translator is None and name == "stderr":
                return progress.get_writer(sys.stderr)
            elif translator is None:
                return as_context(std_args[name])
            else:
                with env.auto_translate():
                    path = translator.translate(env)
                return open(path, "w")

        with get_stdfile("stdin",  exp) as stdin,\
             get_stdfile("stdout", exp) as stdout,\
             get_stdfile("stderr", exp) as stderr:
            res = execute_with_sigint(
                *cmd,
                shell=is_shell,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr)
        if res != 0:
            raise Exception("Command did not finish correctly: "
                            "%s -> %d" % (" ".join(cmd), res))

        return len(exp_cmd[1])

    # use progr() explicitly to ensure progress is made after each command
    with progress.get(experiments_list, msg="Executing commands...") as progr:
        max_workers = get_executor_workers(parallel)

        def execute_with_progress(exp):
            count = execute(exp, progr)
            progr(count)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(execute_with_progress, exp_cmds))


def _do_recombine(experiments, exp_filters, variables, var_filters, append):
    exp_filters = and_filters(*exp_filters)
    var_filters = and_filters(*var_filters)

    # normalize variable value types
    for key, val in variables.items():
        if not isinstance(val, collections.abc.Iterable) or \
           isinstance(val, six.string_types):
            variables[key] = [val]
        elif isinstance(val, collections.abc.Sized):
            variables[key] = list(val)

    # calculate various properties about variable values
    var_translate = _get_translate_exp(variables)
    var_from_func = [var for var, vals in variables.items()
                     if any(isinstance(val, _FromFunctionKey) for val in vals)]
    var_size = functools.reduce(operator.mul,
                                (len(vals) for vals in variables.values()),
                                1)

    # validate variable filters
    var_filters.validate((set(experiments.variables()) | set(variables.keys())) - var_translate)

    new_experiments = InstanceGroup()
    new_dups = set()

    total_size = len(experiments) * var_size
    if append:
        total_size += var_size

    def cartesian_product(base, variables_missing=None):
        """Yield cartesian product of `variables` and overlay each on `base`"""
        if variables_missing is None:
            variables_missing = sorted(variables.keys())

        if len(variables_missing) == 0:
            yield {}

        else:
            key = variables_missing[0]
            variables_missing = variables_missing[1:]

            for val in variables[key]:
                for exp in cartesian_product(base, variables_missing):
                    new_exp = Instance(base)
                    new_exp.update(exp)
                    new_exp[key] = val
                    yield new_exp

    def cartesian_product_ff(base, ff_info, ffs_missing=None):
        """Yield cartesian product of `ff_info` and overlay each on `base`"""
        if ffs_missing is None:
            ffs_missing = sorted(ff_info.keys())

        if len(ffs_missing) == 0:
            yield {}

        else:
            ff = ffs_missing[0]
            ffs_missing = ffs_missing[1:]

            for val in ff_info[ff][0]:
                for exp in cartesian_product_ff(base, ff_info, ffs_missing):
                    new_exp = Instance(base)
                    new_exp.update(exp)
                    for var in ff_info[ff][1]:
                        new_exp[var[0]] = val[var[1]]
                    yield new_exp

    def merge_old_experiment(exp, force=False):
        exp_dups = tuple(exp.items())
        if exp_dups not in new_dups:
            new_experiments.add(exp)
            new_dups.add(exp_dups)
        elif force:
            new_experiments.add(exp)

    def merge_new_experiment_noff(progr, exp):
        if var_filters.match(exp):
            merge_old_experiment(exp)
        progr()

    def merge_new_experiment(progr, exp):
        ff_vars = dict(((var, exp[var]) for var in var_from_func
                        if isinstance(exp[var], _FromFunctionKey)))

        if len(ff_vars) == 0:
            merge_new_experiment_noff(progr, exp)

        else:
            exp = dict((key, val) for key, val in exp.items()
                       if key not in ff_vars)

            ff_info = {}
            progr_size_add = 1
            for var, val in ff_vars.items():
                val = val._from_func
                if val not in ff_info:
                    exp_ff = dict(exp)
                    vals = val._get_results(exp)
                    if len(vals) == 0:
                        # experiment dropped, but still increase progress
                        progr()
                        return
                    ff_info[val] = (vals, [])
                    progr_size_add *= len(vals)
                ff_info[val][1].append((var, ff_vars[var]._key_name))

            assert progr_size_add > 0
            progr += progr_size_add

            for exp_prod in cartesian_product_ff(exp, ff_info):
                merge_new_experiment_noff(progr, exp_prod)


    with progress.get(total_size,
                      msg="recombining variables...") as progr:

        if append:
            for exp in experiments:
                merge_old_experiment(exp, force=True)
                progr(var_size)

            for exp_prod in cartesian_product({}):
                merge_new_experiment(progr, exp_prod)
        else:
            for exp_base in experiments:
                try:
                    is_match = exp_filters.match(exp_base)
                except NameError:
                    is_match = False

                if is_match:
                    for exp_prod in cartesian_product(exp_base):
                        merge_new_experiment(progr, exp_prod)
                else:
                    merge_old_experiment(exp_base)
                    progr(var_size)

    return new_experiments, var_translate


def _do_pack(experiments, template_from, template_to, dereference):
    if len(experiments) == 0:
        experiments_list = [Instance()]
    else:
        experiments_list = experiments
    if dereference is None:
        dereference = experiments.dereference

    translate_from = text.Translator(template_from)
    translate_to = text.Translator(template_to)

    done_first = {}
    done_exp = {}
    with progress.get(len(experiments_list), msg="packing files...") as progr:
        for exp in experiments_list:
            with exp.auto_translate():
                path_from = utils.get_path(translate_from.translate(exp))
                path_to = utils.get_path(translate_to.translate(exp))
                path_to = os.path.join(experiments.out, path_to)

                done_idx = path_from + "+" + path_to
                if done_idx in done_first:
                    if done_first[done_idx]:
                        done_first[done_idx] = False
                        progress.info(
                            "Skipping already packed file: %s -> %s",
                            path_from, path_to)
                    progress.verbose(
                        "Conflicting experiments during pack:\n%s\n%s",
                        done_exp[done_idx], exp)
                else:
                    done_first[done_idx] = True
                    done_exp[done_idx] = exp

                    progress.debug("Packing: %s -> %s", path_from, path_to)
                    utils.copy_path(path_from, path_to, dereference=dereference)

                progr()


def _do_translate(experiments, exp_filters, exp_translate,
                  templates, with_exps, with_unique):
    exp_filters = and_filters(*exp_filters)
    parsed_templates = [text.Translator(template)
                        for template in templates]

    if with_exps:
        if with_unique:
            translations = collections.OrderedDict()
            if len(templates) == 1:
                def add(translated, exp):
                    translated = translated[0]
                    if translated not in translations:
                        translations[translated] = []
                    translations[translated].append(dict(exp))
            else:
                def add(translated, exp):
                    if translated not in translations:
                        translations[translated] = []
                    translations[translated].append(dict(exp))
            def result():
                return translations.items()
        else:
            translations = []
            if len(templates) == 1:
                def add(translated, exp):
                    translations.append((translated[0], [dict(exp)]))
            else:
                def add(translated, exp):
                    translations.append((translated, [dict(exp)]))
            def result():
                return translations
    else:
        if with_unique:
            translations = utils.OrderedSet()
            if len(templates) == 1:
                def add(translated, exp):
                    translations.add(translated[0])
            else:
                def add(translated, exp):
                    translations.add(tuple(translated))
            def result():
                return translations
        else:
            translations = []
            if len(templates) == 1:
                def add(translated, exp):
                    translations.append(translated[0])
            else:
                def add(translated, exp):
                    translations.append(tuple(translated))
            def result():
                return translations

    for exp in experiments.select(exp_filters):
        with exp.auto_translate():
            try:
                is_match = exp_filters.match(exp)
            except NameError:
                is_match = False

            if is_match:
                _WithExp.set_experiment(exp)
                _WithExpTpl.set_experiment(exp)
                translated = [template.translate(exp)
                              for template in parsed_templates]
                add(translated, exp)

    return list(result())


def _do_generate(experiments, template_from, template_to,
                 pre_exp_fun, post_exp_fun, parallel):
    out = os.path.abspath(utils.get_path(experiments.out))
    translate_from = text.Translator(template_from)
    translate_to = text.Translator(template_to)

    done_set_lock = threading.Lock()
    done_set = {}
    class done_state:
        def __init__(self):
            self.lock = threading.Lock()
            self.is_first = True
            self.is_second = False
            self.first_exp = None
        def set_first(self, exp):
            with self.lock:
                is_first = self.is_first
                if is_first:
                    self.is_first = False
                    self.first_exp = exp
                    is_second = True
                else:
                    is_second = False
            return is_first, is_second
    def get_done(path_from, path_to):
        key = (path_from, path_to)
        with done_set_lock:
            if key not in done_set:
                done_set[key] = done_state()
            return done_set[key]

    with progress.get(len(experiments), msg="generating files...") as progr:

        def generate_with_progress(exp_info):
            idx, exp = exp_info
            with exp.auto_translate():
                _WithExp.set_experiment(exp)
                _WithExpTpl.set_experiment(exp)

                path_from = utils.get_path(translate_from.translate(exp))
                path_to = utils.get_path(translate_to.translate(exp))
                path_to = os.path.join(out, path_to)

                done = get_done(path_from, path_to)
                is_first, is_second = done.set_first(exp)
                if not is_first:
                    msg = f"WARNING: Skipping already generated file: {path_from} -> {path_to}"
                    msg += "\n"
                    msg += f"Source file template: {template_from}"
                    msg += "\n"
                    msg += f"Destination file template: {template_to}"
                    msg += "\n"
                    msg += f"Conflicting experiments:\n{done.first_exp}\n{exp}"
                    if is_second:
                        progress.info(msg)
                    else:
                        progress.verbose(msg)
                else:
                    progress.debug(f"Generating: {path_from} -> {path_to}")

                    exp, contents_to = pre_exp_fun(idx, exp, path_from, path_to)

                    utils.assert_dir(os.path.dirname(path_to))
                    if os.path.isfile(path_to):
                        with open(path_to, "r") as f:
                            contents_to_old = f.read()
                    else:
                        contents_to_old = ""
                        utils.get_file(path_to, "w")
                    shutil.copymode(path_from, path_to)

                    if contents_to != contents_to_old:
                        with open(path_to, "w") as f:
                            f.write(contents_to)

                    post_exp_fun(idx, exp, path_to)

            progr()

        max_workers = get_executor_workers(parallel)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(generate_with_progress, enumerate(experiments)))


def _do_generate_user(experiments, template_from, template_to, parallel,
                      backend, backend_options):
    @functools.lru_cache(16)
    def get_translator(path_from):
        file_from = text.TemplatePath(path_from)
        return text.Translator(file_from, backend=backend,
                               backend_options=backend_options)
    def pre_exp_fun(idx, exp, path_from, path_to):
        translator = get_translator(path_from)
        return exp, translator.translate(exp)
    def post_exp_fun(idx, exp, path_to):
        pass
    _do_generate(experiments, template_from, template_to,
                 pre_exp_fun, post_exp_fun, parallel)

def _do_generate_jobs(experiments, system, template_to, export, depends,
                      submit_args, job_desc, parallel):
    template = templates.get(system)

    depends = set(depends) | set(["{{LAUNCHER}}"])

    # export all variables in depends
    export = set(export)
    for elem in depends:
        if not isinstance(elem, six.string_types):
            raise TypeError("depends element is not a string: %r" % elem)
        for elem_var in text.get_variables(elem, nested="all"):
            if elem_var == "LAUNCHER":
                continue
            export.add(elem_var)

    if isinstance(experiments, ExperimentsView):
        experiments_vars = list(experiments._base._experiments.variables())
    else:
        experiments_vars = list(experiments._experiments.variables())
    for export_elem in export:
        if not isinstance(export_elem, six.string_types):
            raise TypeError("export element is not a string: %r" % export_elem)
        if export_elem not in experiments_vars:
            raise ValueError("missing variable to export: %s" % export_elem)
    export = export | set(template.system.assumes())

    out = os.path.abspath(utils.get_path(experiments.out))
    job_desc = os.path.join(out, job_desc)
    job_desc = os.path.abspath(utils.get_path(job_desc))
    if not job_desc.startswith(out):
        raise ValueError("job descriptor file must be inside output directory")
    job_desc_base = os.path.dirname(job_desc[len(out)+1:])

    # load template file and apply overrides
    path_from = template.template_path
    with open(path_from, "r") as f:
        template_from = f.read()
    overrides = dict(template.overrides)
    for var in text.get_variables(template_from):
        if var not in overrides:
            overrides[var] = "{{%s}}" % var
    template_from = text.translate(text.TemplatePath(template.template_path),
                                   overrides, recursive=False)
    template_from_vars = text.get_variables(template_from)
    translate_from = text.Translator(text.TemplateContents(template_from))

    def pre_exp_fun(idx, exp, path_from, path_to):
        exp = dict(exp)

        if "LAUNCHER" in exp:
            raise ValueError("experiment has reserved variable 'LAUNCHER'")
        exp["LAUNCHER"] = path_to[len(out)+1:]

        for key, val in template.defaults.items():
            if key not in exp:
                exp[key] = val

        contents_to = translate_from.translate(exp)

        return exp, contents_to

    experiments_generated = [None] * len(experiments)

    def post_exp_fun(idx, exp, path_to):
        for var in export:
            if var not in exp:
                continue
            val = exp[var]
            if not _val_is_translate(val):
                continue
            exp[var] = text.translate(val, exp)
        experiments_generated[idx] = Instance(exp)

    _do_generate(experiments, template.template_path, template_to,
                 pre_exp_fun, post_exp_fun, parallel)

    experiments_generated = InstanceGroup(
        (exp for exp in experiments_generated if exp is not None))

    launcher.save(job_desc, job_desc_base,
                  template.system, experiments_generated,
                  export, depends, submit_args)


class Experiments(pp.Pretty):
    """Define and generate experiment sets.

    Each experiment corresponds to a `dict` that maps variable names to their
    values, and can be accessed as if `Experiments` was a list.

    Parameters
    ----------
    experiments : sequence of dict, optional
        Initial experiment set.
    out : optional
        Initial value for the `out` attribute.
    dereference : bool, optional
        Initial value for the `dereference` attribute.

    Attributes
    ----------
    out : str
        Output directory for all non-absolute paths.
    dereference : bool
        Whether to dereference source symlinks during `pack`.

    See also
    --------
    with_exp, with_exp_tpl
        Use functions as variable values.
    from_function, from_find_files
        Use functions to create new variable values.
    sciexp2.common.text.translate
        Used to interpret template arguments in the `Experiments` methods, used
        with the variable maps of each experiment.
    sciexp2.common.text.extract
        Used to interpret template arguments in the `Experiments` methods, used
        to build the variable maps of new experiments.
    sciexp2.common.filter.Filter
        Values accepted for the filter arguments of the methods in
        `Experiments`. A list of strings will be used as an argument to
        `sciexp2.common.filter.and_filters`.

    """

    #: Output directory for all non-absolute paths.
    out = "./out"

    #: Whether to dereference source symlinks during pack.
    dereference = False

    def __init__(self, experiments=None, **kwargs):
        out = kwargs.pop("out", None)
        dereference = kwargs.pop("dereference", None)
        utils.assert_kwargs(kwargs)

        if experiments is None:
            experiments = InstanceGroup()
            # add dummy experiment
            experiments += Instance()
        if isinstance(experiments, Experiments) or\
           isinstance(experiments, ExperimentsView):
            if dereference is None:
                dereference = experiments.dereference
            if out is None:
                out = experiments.out
            self._experiments = experiments._experiments
            self._translate = utils.OrderedSet(experiments._translate)
        else:
            self._experiments = InstanceGroup()
            dups = set()
            for exp in experiments:
                exp_dups = tuple(exp.items())
                if exp_dups not in dups:
                    self._experiments.add(Instance(exp))
                    dups.add(exp_dups)
            self._translate = _get_translate(self._experiments)

        if out is not None:
            self.out = out
        if dereference is not None:
            self.dereference = dereference


    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle):
            have_prev = False
            if len(self) > 0:
                p.pretty(list(map(lambda elem: _sorted_dict(elem), self)))
                have_prev = True
            if self.out != Experiments.out:
                if have_prev:
                    p.text(",")
                    p.breakable()
                p.text("out=%r" % self.out)
                have_prev = True
            if self.dereference != Experiments.dereference:
                if have_prev:
                    p.text(",")
                    p.breakable()
                p.text("dereference=%r" % self.dereference)


    def __iter__(self):
        if _is_dummy(self):
            return iter([])
        else:
            return iter(self._experiments)

    def __len__(self):
        if _is_dummy(self):
            return 0
        else:
            return len(self._experiments)

    def __getitem__(self, index):
        if _is_dummy(self):
            return list()[index]
        else:
            return self._experiments.get_index(index)

    def __eq__(self, other):
        return isinstance(other, Experiments) and \
            self.out == other.out and \
            self.dereference == other.dereference and \
            list(self._experiments) == list(other._experiments) and \
            list(self._translate) == list(other._translate)

    def view(self, *filters):
        """Get a view to a portion of this of this experiment set.

        Any changes to the experiments on a view will be reflected on the base
        experiment set and all its views. Adding new experiments to a view will
        maintain the relative order between experiments on the base experiment
        set.

        Parameters
        ----------
        filters : list of filters
            Filters to select a matching subset of the experiments.

        Examples
        --------
        A view shows a subset of the experiments:

        >>> e = Experiments()
        >>> e.params(a=range(2), b=range(2))
        >>> e
        Experiments([{'a': 0, 'b': 0},
                     {'a': 0, 'b': 1},
                     {'a': 1, 'b': 0},
                     {'a': 1, 'b': 1}])
        >>> v = e.view("a == b")
        >>> v
        ExperimentsView([{'a': 0, 'b': 0}, {'a': 1, 'b': 1}])

        All operations are performed only on selected elements, but apply to the
        underlying experiment set as if they happened "in-place":

        >>> v = e.view("a == b")
        >>> v.params(c=range(2))
        >>> v
        ExperimentsView([{'a': 0, 'b': 0, 'c': 0},
                         {'a': 0, 'b': 0, 'c': 1},
                         {'a': 1, 'b': 1, 'c': 0},
                         {'a': 1, 'b': 1, 'c': 1}])
        >>> e
        Experiments([{'a': 0, 'b': 0, 'c': 0},
                     {'a': 0, 'b': 0, 'c': 1},
                     {'a': 0, 'b': 1},
                     {'a': 1, 'b': 0},
                     {'a': 1, 'b': 1, 'c': 0},
                     {'a': 1, 'b': 1, 'c': 1}])

        For convenience, you can also get the inverse of a view, which is a view
        with the negated filters:

        >>> i = v.view_inverse()
        >>> i
        ExperimentsView([{'a': 0, 'b': 1}, {'a': 1, 'b': 0}])
        >>> i.params(d=range(2))
        >>> e
        Experiments([{'a': 0, 'b': 0, 'c': 0},
                     {'a': 0, 'b': 0, 'c': 1},
                     {'a': 0, 'b': 1, 'd': 0},
                     {'a': 0, 'b': 1, 'd': 1},
                     {'a': 1, 'b': 0, 'd': 0},
                     {'a': 1, 'b': 0, 'd': 1},
                     {'a': 1, 'b': 1, 'c': 0},
                     {'a': 1, 'b': 1, 'c': 1}])

        Finally, you can also create new views from other views:

        >>> n = v.view("c == 0")
        >>> n.params(e=[10, 20])
        >>> n.view_inverse().params(e=[30, 40])
        >>> e
        Experiments([{'a': 0, 'b': 0, 'c': 0, 'e': 10},
                     {'a': 0, 'b': 0, 'c': 0, 'e': 20},
                     {'a': 0, 'b': 0, 'c': 1, 'e': 30},
                     {'a': 0, 'b': 0, 'c': 1, 'e': 40},
                     {'a': 0, 'b': 1, 'd': 0},
                     {'a': 0, 'b': 1, 'd': 1},
                     {'a': 1, 'b': 0, 'd': 0},
                     {'a': 1, 'b': 0, 'd': 1},
                     {'a': 1, 'b': 1, 'c': 0, 'e': 10},
                     {'a': 1, 'b': 1, 'c': 0, 'e': 20},
                     {'a': 1, 'b': 1, 'c': 1, 'e': 30},
                     {'a': 1, 'b': 1, 'c': 1, 'e': 40}])

        """
        return ExperimentsView(self, Filter("True"), Filter(*filters))

    def execute(self, cmd, **kwargs):
        """Execute one program for each experiment on the set.

        If `cmd` is a single string, it's interpreted as a shell command,
        otherwise it's interpreted as a program name and its argument list.

        Arguments `stdin`, `stdout`, `stderr`, and all elements in `cmd` are
        interpreted as templates to translate with each experiment.

        Parameters
        ----------
        cmd : list of str
            Command to execute.
        repeat : str, optional
            What to do when more than one experiment is translated into the same
            command. Can be ``"ignore"``, ``"warn"`` (default), or ``"error"``.
        stdin, stdout, stderr : file or str, optional
            Paths for the standard input/output/error for the command (defaults
            to None).
        parallel : optional
            Whether to execute commands in parallel (default is `False`).

        Notes
        -----
        Command execution is internally handled by `subproces.Popen` and thus
        the `stdin`, `stdout` and `stderr` arguments can also have any value
        accepted by it.

        See also
        --------
        sciexp2.common.parallel.get_parallelism
            Used to interpret argument `parallel`.

        """
        _do_execute(self, cmd, **kwargs)


    def params(self, *filters, **variables):
        """Add new parameter permutations to experiment set.

        Performs the cartesian product between the current experiment set and
        all permutations of the given variable values (i.e., a parameter can
        have a sequence of values).

        Parameters
        ----------
        filters : list of filters, optional
            Ensures new experiments match the given filters (default is to
            accept all).
        variables : dict
            A dictionary of variable name / values pairs to perform
            permutations.

        Notes
        -----
        Values in `variables` can be templates referencing other variables
        (either existing in the experiment set or provided in `variables`), and
        will thus be translated accordingly.

        Providing a variable in `params` that already exists in the experiment
        set will override its value.

        Examples
        --------
        Can easily create value permutations that match the given filters:
        >>> e = Experiments()
        >>> e.params("a % 2 == 0",
        ...          a=range(4),
        ...          b=["foo", "bar"])
        >>> e
        Experiments([{'a': 0, 'b': 'foo'},
                     {'a': 0, 'b': 'bar'},
                     {'a': 2, 'b': 'foo'},
                     {'a': 2, 'b': 'bar'}])

        New variables can be appended to the experiment set:

        >>> e.params(c=3)
        >>> e
        Experiments([{'a': 0, 'b': 'foo', 'c': 3},
                     {'a': 0, 'b': 'bar', 'c': 3},
                     {'a': 2, 'b': 'foo', 'c': 3},
                     {'a': 2, 'b': 'bar', 'c': 3}])

        Including ones with multiple values:

        >>> e.params(d=[1, 2])
        >>> e
        Experiments([{'a': 0, 'b': 'foo', 'c': 3, 'd': 1},
                     {'a': 0, 'b': 'foo', 'c': 3, 'd': 2},
                     {'a': 0, 'b': 'bar', 'c': 3, 'd': 1},
                     {'a': 0, 'b': 'bar', 'c': 3, 'd': 2},
                     {'a': 2, 'b': 'foo', 'c': 3, 'd': 1},
                     {'a': 2, 'b': 'foo', 'c': 3, 'd': 2},
                     {'a': 2, 'b': 'bar', 'c': 3, 'd': 1},
                     {'a': 2, 'b': 'bar', 'c': 3, 'd': 2}])

        New values override old ones, even if that means eliminating some experiments:

        >>> e.params(b="baz")
        >>> e
        Experiments([{'a': 0, 'b': 'baz', 'c': 3, 'd': 1},
                     {'a': 0, 'b': 'baz', 'c': 3, 'd': 2},
                     {'a': 2, 'b': 'baz', 'c': 3, 'd': 1},
                     {'a': 2, 'b': 'baz', 'c': 3, 'd': 2}])

        """
        new_experiments = _do_recombine(self._experiments, [],
                                        variables, filters,
                                        False)
        self._experiments = new_experiments[0]
        self._translate |= new_experiments[1]


    def params_append(self, *filters, **variables):
        """Same as `params`, but appends the new permutations.

        Examples
        --------
        >>> e = Experiments()
        >>> e.params(a=range(2))
        >>> e.params_append(b=range(2))
        >>> e
        Experiments([{'a': 0},
                     {'a': 1},
                     {'b': 0},
                     {'b': 1}])

        """
        new_experiments = _do_recombine(self._experiments, [],
                                        variables, filters,
                                        True)
        self._experiments = new_experiments[0]
        self._translate |= new_experiments[1]


    def pack(self, template_from, template_to, dereference=None):
        """Copy files, accepting templates for both source and destination paths.

        Parameters
        ----------
        template_from, template_to : str
            Source/destination file templates.
        dereference : bool, optional
            Whether to dereference symlinks in source files (defaults to
            ``self.dereference``).

        Notes
        -----
        The copy is performed only if the source is newer than the destination,
        or if the destination does not exist.

        There can be cases where multiple source files correspond to a single
        destination file (after translating the templates). Such cases are
        logged by a message.

        """
        _do_pack(self, template_from, template_to, dereference)

    def generate(self, template_from, template_to,
                 parallel=True, backend="pystache", backend_options={}):
        """Generate files from other templated files.

        Like `pack`, the paths to source and destination files are
        templates. Every source file is, in addition, considered a template that
        will be translated with each of the experiments.

        Parameters
        ----------
        template_from, template_to : str
            Templates for Source/destination file paths.
        parallel : optional
            Whether to generate files in parallel (default is `True`).
        backend : {'pystache', 'jinja2'}, optional
            Templating backend to process the contents of `template_from`.

        Notes
        -----
        Like `pack`, if multiple source files correspond to a single destination
        file (after translating the templates), the case is logged by a message
        and only the first generated file is kept.

        """
        _do_generate_user(self, template_from, template_to,
                          parallel=parallel, backend=backend,
                          backend_options=backend_options)

    def generate_jobs(self, system, template_to, export=[], depends=[],
                      submit_args=[], job_desc="jobs.jd",
                      parallel=True):
        """Generate job files for given job system.

        Works similar to `generate`, but takes a predefined source file template
        that is identified by `system`. It also creates a job descriptor file
        that can be later used by the `launcher` program.

        Parameters
        ----------
        system : str
            Job system name.
        template_to : str
            Template to path of destination job scripts.
        export : list of str, optional
            List of variable names to export into the job descriptor file.
        depends : list of str, optional
            File path templates for job dependencies.
        submit_args : list of str, optional
            Templates for additional arguments to the job submission command.
        job_desc : str, optional
            Name of the output job descriptor file.
        parallel : optional
            Whether to generate files in parallel (default is `True`).

        All job systems implicitly define the *LAUNCHER* variable, which has the
        path of the to the generated script to run that. All job systems also
        define *DONE* and *FAIL* as file paths to identify the state of each
        job.

        The variables selected by `export` will be later available when using
        `sciexp2.expdef.launcher` with this job descriptor. Any variable
        directly or indirectly used in `depends` will be implicitly added to
        `export`. Variable *LAUNCHER* is also implicitly added.

        The templates specified by `depends` will be translated for each job
        info file paths, and each file path will be considered a dependency of
        that job. The path specified by *LAUNCHER* is implicitly added as a
        dependency.

        The state for a given job is decided as follows:

        - Not run: Neither the *DONE* nor the *FAIL* files exist.
        - Failed: The *FAIL* file exists.
        - Outdated: The *DONE* file exists, but is older than any of its
          dependencies.
        - Done: The *DONE* file exists, and is newer than any of its
          dependencies.
        - Running: Some job systems can track when a job is currently executing.


        Notes
        -----

        None of the experiments can define the *LAUNCHER* variable. Some job
        systems also define their own set of reserved variables and default
        values to others (in case your experiments don't specify them); see the
        job system's documentation for more information.

        """
        _do_generate_jobs(self, system, template_to, export, depends,
                          submit_args, job_desc, parallel)


    def translate(self, template, with_exps=False, with_unique=True):
        """Translate the given templates with each experiment.

        Parameters
        ----------
        template : str
            Template to translate.
        with_exps : bool, optional
            Return the list of experiments used to get each translation.
        with_unique : bool, optional
            Only return unique translations.

        Returns
        -------
        A list of the template translations (``with_exps=False``), or a list of
        tuples with each translation and the corresponding experiments
        (``with_exps=True``).

        Examples
        --------
        Translations are unique by default:
        >>> e = Experiments()
        >>> e.params(a=range(2), b=range(2), c=range(2))
        >>> e.translate("{{a}}-{{b}}")
        ['0-0', '0-1', '1-0', '1-1']
        >>> e.translate("{{a}}-{{b}}", with_unique=False)
        ['0-0', '0-0', '0-1', '0-1', '1-0', '1-0', '1-1', '1-1']

        And can be easily extended with the experiments that led to each
        translation:
        >>> e.translate("{{a}}-{{b}}", with_exps=True) == [
        ...     ('0-0', [{'a': 0, 'b': 0, 'c': 0}, {'a': 0, 'b': 0, 'c': 1}]),
        ...     ('0-1', [{'a': 0, 'b': 1, 'c': 0}, {'a': 0, 'b': 1, 'c': 1}]),
        ...     ('1-0', [{'a': 1, 'b': 0, 'c': 0}, {'a': 1, 'b': 0, 'c': 1}]),
        ...     ('1-1', [{'a': 1, 'b': 1, 'c': 0}, {'a': 1, 'b': 1, 'c': 1}])]
        True
        >>> e.translate("{{a}}-{{b}}", with_exps=True, with_unique=False) == [
        ...     ('0-0', [{'a': 0, 'b': 0, 'c': 0}]),
        ...     ('0-0', [{'a': 0, 'b': 0, 'c': 1}]),
        ...     ('0-1', [{'a': 0, 'b': 1, 'c': 0}]),
        ...     ('0-1', [{'a': 0, 'b': 1, 'c': 1}]),
        ...     ('1-0', [{'a': 1, 'b': 0, 'c': 0}]),
        ...     ('1-0', [{'a': 1, 'b': 0, 'c': 1}]),
        ...     ('1-1', [{'a': 1, 'b': 1, 'c': 0}]),
        ...     ('1-1', [{'a': 1, 'b': 1, 'c': 1}])]
        True

        """
        return _do_translate(self._experiments, [], self._translate,
                             [template], with_exps, with_unique)


######################################################################
# Views

class ExperimentsView (pp.Pretty):
    """Proxy to a subset of elements in a `Experiments` instance.

    Notes
    -----
    You can use a view with Python's ``with`` statement to improve code
    readability:

    >>> e = Experiments()
    >>> e.params(a=range(2), b=range(2))
    >>> with e.view("a != b") as v, v.view_inverse() as i:
    ...     v.params(c=1)
    ...     i.params(c=2)
    >>> e
    Experiments([{'a': 0, 'b': 0, 'c': 2},
                 {'a': 0, 'b': 1, 'c': 1},
                 {'a': 1, 'b': 0, 'c': 1},
                 {'a': 1, 'b': 1, 'c': 2}])

    """

    def __init__(self, experiments, filter_base, filter_top,
                 **kwargs):
        assert len(kwargs) == 0
        self._base = experiments
        self._filters = [filter_base, filter_top]
        for filter_ in self._filters:
            filter_.validate(set(self._base._experiments.variables()))

    def _get_experiments(self):
        filter_ = self._as_filter()
        return self._base._experiments.select(filter_, allow_unknown=True)

    def _repr_pretty_(self, p, cycle):
        with self.pformat(p, cycle):
            have_prev = False
            if len(self) > 0:
                p.pretty(list(map(lambda elem: _sorted_dict(elem), self._get_experiments())))
                have_prev = True
            if self.out != Experiments.out:
                if have_prev:
                    p.text(",")
                    p.breakable()
                p.text("out=%r" % self.out)
                have_prev = True
            if self.dereference != Experiments.dereference:
                if have_prev:
                    p.text(",")
                    p.breakable()
                p.text("dereference=%r" % self.dereference)

    def __iter__(self):
        return self._get_experiments()

    def __len__(self):
        return len(list(self._get_experiments()))

    def __getitem__(self, index):
        return list(self._get_experiments())[index]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _as_filter(self):
        return and_filters(*self._filters)

    @property
    def out(self):
        return self._base.out

    @property
    def dereference(self):
        return self._base.dereference

    def view(self, *filters):
        """Create a new view from this one.

        See also
        --------
        Experiments.view

        """
        return ExperimentsView(self._base,
                               self._as_filter(),
                               and_filters(*filters))

    def view_inverse(self):
        """Get the inverse view of this one.

        If using nested views, this will invert the filter of this one, not all
        filters for parent views.

        See also
        --------
        Experiments.view

        """
        return self._base.view(and_filters(self._filters[0],
                                           "not (%s)" % self._filters[1]))

    def execute(self, *args, **kwargs):
        """Same as `Experiments.execute`"""
        return _do_execute(self, *args, **kwargs)

    def params(self, *filters, **variables):
        """Same as `Experiments.params`"""
        new_experiments = _do_recombine(self._base._experiments, self._filters,
                                        variables, filters,
                                        False)
        self._base._experiments = new_experiments[0]
        self._base._translate |= new_experiments[1]

    def params_append(self, *filters, **variables):
        """Same as `Experiments.params_append`"""
        new_experiments = _do_recombine(self._base._experiments, [],
                                        variables, filters,
                                        True)
        self._base._experiments = new_experiments[0]
        self._base._translate |= new_experiments[1]

    def pack(self, template_from, template_to, dereference=None):
        """Same as `Experiments.pack`"""
        _do_pack(self, template_from, template_to, dereference=None)

    def generate(self, template_from, template_to,
                 parallel=True, backend="pystache"):
        """Same as `Experiments.generate`"""
        _do_generate_user(self, template_from, template_to,
                          parallel=parallel, backend=backend)

    def generate_jobs(self, system, template_to, export=[], depends=[],
                      submit_args=[], job_desc="jobs.jd", parallel=True):
        """Same as `Experiments.generate_jobs`"""
        _do_generate_jobs(self, system, template_to, export, depends,
                          submit_args, job_desc, parallel)

    def translate(self, template, with_exps=False, with_unique=True):
        """Same as `Experiments.translate`"""
        return _do_translate(self._base._experiments, self._filters, self._translate,
                             [template], with_exps, with_unique)


    def __getattr__(self, name):
        if name in ["_base", "_filters"]:
            object.__getattribute__(self, name)
        else:
            attr = getattr(self._base, name)
            if callable(attr):
                if attr.__name__ in VIEW_SUPPORTED:
                    attr = getattr(self._base,
                                   VIEW_SUPPORTED[attr.__name__])

                def func(*args, **kwargs):
                    return attr(self._as_filter(), *args, **kwargs)
                return func
            else:
                return attr

    def __setattr__(self, name, value):
        if name in ["_base", "_filters"]:
            object.__setattr__(self, name, value)
        else:
            attr = getattr(self._base, name)
            assert not callable(attr)
            setattr(self._base, name, value)


######################################################################
# Function wrappers

_THREADLOCAL = threading.local()

class _WithExp(pp.Pretty):

    def __init__(self, func):
        self._func = func

    @staticmethod
    def set_experiment(experiment):
        setattr(_THREADLOCAL, "_WithExp__experiment", experiment)

    @staticmethod
    def get_experiment():
        return getattr(_THREADLOCAL, "_WithExp__experiment", None)

    def __call__(self, *args, **kwargs):
        exp = self.get_experiment()
        return self._func(exp, *args, **kwargs)

    def _repr_pretty_(self, p, cycle):
        p.text("with_exp(")
        p.pretty(self._func)
        p.text(")")

    def __eq__(self, other):
        return isinstance(other, _WithExp) and self._func == other._func

    def __hash__(self):
        return hash((_WithExp, self._func))


def with_exp(func):
    """Wrap function to get experiment as first argument during translation.

    Examples
    --------
    >>> e = Experiments()
    >>> e.params(a=range(2), b=range(2),
    ...          c=with_exp(lambda exp: exp['a']+exp['b']))
    >>> e.translate("{{c}}")
    ['0', '1', '2']

    """
    return _WithExp(func)

class _WithExpTpl(pp.Pretty):

    _EXPERIMENT = None

    def __init__(self, func, template):
        self._func = func
        self._template = template
        self._translator = text.Translator(self._template)

    @staticmethod
    def set_experiment(experiment):
        setattr(_THREADLOCAL, "_WithExpTpl__experiment", experiment)

    @staticmethod
    def get_experiment():
        return getattr(_THREADLOCAL, "_WithExpTpl__experiment", None)

    def __call__(self, *args, **kwargs):
        exp = self.get_experiment()
        translated = self._translator.translate(exp)
        return self._func(exp, translated, *args, **kwargs)

    def _repr_pretty_(self, p, cycle):
        p.text("with_exp_tpl(")
        p.pretty(self._func)
        p.text(", ")
        p.pretty(self._template)
        p.text(")")

    def __eq__(self, other):
        return (isinstance(other, _WithExpTpl) and
                self._func == other._func and
                self._template == other._template)

    def __hash__(self):
        return hash((_WithExp, self._func, self._template))


def with_exp_tpl(func, template):
    """Similar to `with_exp`, but passes translated template as second argument.

    This is a convenience shortcut for using `text.translate` in `with_exp`.

    Examples
    --------
    In its basic form, we can combine translated templates with other experiment
    values:

    >>> e = Experiments()
    >>> def fun(exp, tpl):
    ...     return tpl + " == " + str(exp['a']+exp['b'])
    >>> e.params(a=range(2), b=range(2),
    ...          f=with_exp_tpl(fun, "{{a}}+{{b}}"))
    >>> e.translate("{{f}}")
    ['0+0 == 0', '0+1 == 1', '1+0 == 1', '1+1 == 2']

    But this comes in handy when we want to pull the contents of per-experiment
    files into new experiment values. Let's start by creating some files:

    >>> import tempfile
    >>> tmp_dir = tempfile.TemporaryDirectory()
    >>> with open(os.path.join(tmp_dir.name, "file-0"), "w") as f:
    ...     f.write("000")
    3
    >>> with open(os.path.join(tmp_dir.name, "file-1"), "w") as f:
    ...     f.write("111")
    3

    And now we can use them to populate experiment values:

    >>> def get_file(exp, path):
    ...    return open(path, "r").read()
    >>> v = e.view("b == 0")
    >>> v.params(f=with_exp_tpl(get_file, os.path.join(tmp_dir.name, "file-1")))
    >>> v.translate("{{f}}")
    ['111']
    >>> v.params(f=with_exp_tpl(get_file, os.path.join(tmp_dir.name, "file-{{a}}")))
    >>> v.translate("{{f}}")
    ['000', '111']

    """
    return _WithExpTpl(func, template)


class _FromFunction(object):
    def __init__(self, func, keys):
        self._func = func
        self._keys = keys
        self._results = None

    def param(self, key_name):
        if key_name not in self._keys:
            raise ValueError("unknown key name: %s" % key_name)
        if self._results is not None:
            raise Exception("cannot get parameter after getting function results")
        return _FromFunctionKey(self, key_name)

    def _get_results(self, exp):
        results = self._func(exp)
        if not isinstance(results, collections.abc.Sized):
            results = list(results)
        return results


class _FromFunctionKey(object):
    def __init__(self, from_function, key_name):
        self._from_func = from_function
        self._key_name = key_name


def from_function(fun, keys):
    """Parameter value to add given parameter permutations to every experiment.

    For every experiment, it will permute it with the values returned by
    `fun`. Note that `fun` is expected to return entries with multiple variable
    names (specified by `keys`), so you must call ``param`` on the result of
    `from_function` to select the specific variable name.

    Parameters
    ----------
    fun : callable
        Function to call on every experiment, receives the experiment at hand
        and must return a list of dict.
    keys : list of str
        Variable names in the elements returned by `fun`.

    Examples
    --------
    The result can use any of the values available on each experiment; in this
    case ``b`` is two and three times the value of ``a`` (note how `from_func`
    and other values can be mixed):

    >>> def func(exp):
    ...     return [{'b': exp["a"]*2}, {'b': exp["a"]*3}]
    >>> e = Experiments()
    >>> e.params(a=range(2), b=from_function(func, ["b"]).param("b"))
    >>> e
    Experiments([{'a': 0, 'b': 0}, {'a': 1, 'b': 2}, {'a': 1, 'b': 3}])

    See also
    --------
    Experiments.params

    """
    return _FromFunction(fun, keys)


def from_find_files(template, **kwargs):
    """Helper to use `sciexp2.common.utils.find_files` with `from_function`.

    Will provide all variable names that are tags in the template. If argument
    `path` is provided, will also provide that variable name (with the full path
    to the found file).

    Parameters
    ----------
    template : str
        Template of file paths to find.
    kwargs
        Arguments to `sciexp2.common.utils.find_files`.

    Examples
    --------
    After creating some example files:

    >>> import tempfile
    >>> tmp = tempfile.TemporaryDirectory()
    >>> _ = open(os.path.join(tmp.name, "0.txt"), "w")
    >>> _ = open(os.path.join(tmp.name, "1.txt"), "w")

    Now we can use the variables on the file template (``a``) and its full path
    (``PATH``) as new variables on the experiments (``var`` and ``path``):

    >>> e = Experiments()
    >>> f = from_find_files(os.path.join(tmp.name, "{{a}}.txt"), path="PATH")
    >>> e.params(var=f.param("a"), path=f.param("PATH"))
    >>> e                               # doctest:+ELLIPSIS
    Experiments([{'path': '/tmp/.../0.txt', 'var': 0},
                 {'path': '/tmp/.../1.txt', 'var': 1}])

    """
    template_vars = text.get_variables(template)
    keys = template_vars

    path = kwargs.get("path", None)
    if path is not None:
        if not isinstance(path, six.string_types):
            raise TypeError("path argument must be a string")
        keys.append(path)

    results = list(utils.find_files(template, **kwargs))

    def fun(experiment):
        experiment = dict((key, val) for key, val in experiment.items()
                          if key in template_vars)
        if len(experiment) > 0:
            filter_ = Filter(experiment)
        else:
            filter_ = Filter()
        for result in results:
            if filter_.match(result):
                yield result

    return from_function(fun, keys)


__all__ = [
    "Experiments", "ExperimentsView",
    "with_exp", "with_exp_tpl",
    "from_function", "from_find_files",
]
