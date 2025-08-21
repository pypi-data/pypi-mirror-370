#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Common interface to manage jobs created with expdef.

Each job is described with an `~sciexp2.common.instance.Instance`, as generated
by `~sciexp2.expdef.experiments.Experiments.launcher`.

You can integrate job management into your application by instantiating the
`Launcher` class.

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2023, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import hashlib
import os
import stat
import struct
import time
from six.moves import cPickle as pickle
import subprocess

from sciexp2.common.filter import *
from sciexp2.common import instance
from sciexp2.common import progress
from sciexp2.common import text
from sciexp2.common import utils
import sciexp2.expdef.system



class Launcher:
    """Common interface to manage jobs.

    The `types` argument to all methods identifies a set of job states to
    narrow the selection of jobs.

    The `filters` argument to all methods narrows the selection of jobs to
    those matching the given filters.

    """

    def __init__(self, base_path, system, group, depends, submit_args):
        """
        Parameters
        ----------
        base_path : str
            Path to the base directory created by
            `~sciexp2.expdef.experiments.Experiments.launcher`.
        system : str or System subclass
            Execution system.
        group : `~sciexp2.common.instance.InstanceGroup`
            Job descriptors.
        depends : sequence of str
            Variable names to which jobs depend.
        submit_args : sequence of str
            Extra arguments to the job-submitting program.

        See also
        --------
        sciexp2.expdef.system.get

        """
        if not os.path.isdir(base_path):
            raise IOError("Not a directory: " + base_path)

        if isinstance(system, str):
            name = system
            system = sciexp2.expdef.system.get(system)
            if system is None:
                raise ValueError("Not a launcher system name: " + name)
        if not issubclass(system, sciexp2.expdef.system.System):
            raise TypeError("Not a System subclass: " +
                            system.__class__.__name__)

        if not isinstance(group, instance.InstanceGroup):
            raise TypeError("Not an InstanceGroup")

        self._system = system(base_path, group, depends, submit_args)

    def parse_filters(self, *filters):
        value_filters = []
        filters_ = []
        for f in filters:
            try:
                f = Filter(f)
            except SyntaxError:
                path_abs = os.path.abspath(f)
                path = self._system.get_relative_path(
                    path_abs, self._system._base_abs)
                found = None
                for var in self.variables():
                    values = self._system._launchers[var]
                    if f in values:
                        found = "%s == %r" % (var, f)
                        break
                    if path in values:
                        found = "%s == %r" % (var, path)
                        break
                    if path_abs in values:
                        found = "%s == %r" % (var, path_abs)
                        break
                if found is None:
                    raise
                value_filters.append(found)
            else:
                filters_.append(f)
        res = and_filters(*filters_)
        if len(value_filters) > 0:
            res = and_filters(res, or_filters(*value_filters))
        res.validate(self.variables())
        return res

    def variables(self):
        """Return a list with the available variables."""
        return list(self._system._launchers.variables())

    def values(self, *filters):
        """Return a list with the available variables."""
        filter_ = and_filters(*filters)
        return list(self._system._launchers.select(filter_))

    def summary(self, types, *filters):
        """Print a summary of the state of selected jobs."""
        if len(types) == 0:
            types = list(sciexp2.expdef.system.Job.STATES)

        parts = [(sciexp2.expdef.system.Job.STATE_LONG[t],
                  len(list(self._system.build([t], *filters))))
                 for t in types]
        max_name = max(len(t) for t, _ in parts)
        max_count = max(len(str(n)) for _, n in parts)
        fmt = "%%-%ds: %%%dd" % (max_name, max_count)
        for t, n in parts:
            print(fmt % (t, n))

    def state(self, types, *filters, **kwargs):
        """Print the states for the selected jobs."""
        expression = kwargs.pop("expression", None)
        if len(kwargs) > 0:
            raise ValueError("Unknown arguments: " + " ".join(kwargs.keys()))

        for job in self._system.build(types, *filters):
            state, name = job.state()
            if expression is not None:
                name = text.translate(expression, job)
            print("(%s) %s" % (sciexp2.expdef.system.Job.STATE_SHORT[state], name))

    def submit(self, types, *filters, **kwargs):
        """Submit selected jobs to execution.

        Calls `kill` before submitting a job if it's already running.

        """
        submit_args = kwargs.pop("submit_args", [])
        keep_going = kwargs.pop("keep_going", False)
        if len(kwargs) > 0:
            raise ValueError("Unknown arguments: " + " ".join(kwargs.keys()))
        jobs = list(self._system.build(types, *filters))
        exit_code = 0
        with progress.progressable_simple(
                jobs, None, msg="Submitting jobs...") as pjobs:
            for job in pjobs:
                if job["_STATE"] == sciexp2.expdef.system.Job.RUNNING:
                    job.kill()
                job_path = self._system.get_relative_path(job["LAUNCHER"])
                progress.info("Submitting %s", job_path)
                try:
                    job.submit(*submit_args)
                except subprocess.CalledProcessError as e:
                    exit_code = e.returncode
                    msg = "ERROR: Exited with code %d" % exit_code
                    if progress.level() < progress.LVL_INFO:
                        msg += " (%s)" % self._system.get_relative_path(job["LAUNCHER"])
                    progress.log(progress.LVL_NONE, msg)
                    if not keep_going:
                        break
        return exit_code

    def kill(self, types, *filters, **kwargs):
        """Kill the execution of selected jobs."""
        kill_args = kwargs.pop("kill_args", [])
        if len(kwargs) > 0:
            raise ValueError("Unknown arguments: " + " ".join(kwargs.keys()))
        for job in self._system.build(types, *filters):
            if job["_STATE"] == sciexp2.expdef.system.Job.RUNNING:
                job.kill(*kill_args)

    def files(self, types, *filters, **kwargs):
        """List files matching an expression."""
        expression = kwargs.pop("expression")
        not_expanded = kwargs.pop("not_expanded", False)
        if len(kwargs) > 0:
            raise ValueError("Unknown arguments: " + " ".join(kwargs.keys()))

        expr_path = expression
        if not os.path.isabs(expr_path):
            expr_path = os.path.join(self._system._base_abs, expr_path)

        expr_files = list(f["__FILE"]
                          for f in utils.find_files(expr_path,
                                                    path="__FILE"))

        job_files = set()
        for job in self._system.build(types, *filters):
            path = text.translate(expression, job)
            abs_path = path
            if not os.path.isabs(abs_path):
                abs_path = os.path.join(self._system._base_abs, abs_path)
            if not os.path.exists(abs_path):
                continue
            job_files.add(abs_path)

        if not_expanded:
            res = set(expr_files) - job_files
        else:
            res = set(expr_files) & job_files
        for i in sorted(res, key=expr_files.index):
            print(i)


def _header():
    return b"#!/usr/bin/env launcher\n"


def _magic():
    version = b"launcher"
    return hashlib.md5(version).digest()


class LauncherLoadError(Exception):
    """Could not load given file."""

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Not a job descriptor file: %s" % self.path


def save(file_name, base_to_file, system, group, export, depends, submit_args):
    """Save an InstanceGroup as a job descriptor into a file.

    Parameters
    ----------
    file_name : str
        Path to destination file.
    base_to_file : str
        Relative path from some base directory to the directory containing
        `file_name`.
    system : `~sciexp2.expdef.system.System`
        Class of the execution system to use.
    group : `~sciexp2.common.instance.InstanceGroup`
        Job descriptors.
    export : set
        Variable names to export into the description file.
    depends : sequence of str
        Variable names to which jobs depend.
    submit_args : sequence of str
        Extra arguments to the job-submitting program.

    See also
    --------
    load, sciexp2.expdef.system.get

    """
    assert system is not None
    if not issubclass(system, sciexp2.expdef.system.System):
        system = sciexp2.expdef.system.get(system)

    if len(group) > 0:
        for assumed in system.assumes():
            if assumed not in group:
                raise ValueError("'%s' must be defined" % assumed)

    file_dir = os.path.dirname(file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with open(file_name, "wb") as file_obj:
        file_obj.write(_header())

        version = _magic()
        file_obj.write(struct.pack("I", len(version)))
        file_obj.write(version)

        pickle.dump((base_to_file, system.name, depends, submit_args),
                    file_obj, -1)
        group.dump(file_obj, export)
    fmode = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
    os.chmod(file_name, fmode)


def load(file_name):
    """Load a job description from a file.

    Parameters
    ----------
    file_name : str
        Path to source file.

    Returns
    -------
    sciexp2.expdef.system.System
        Instance of the execution system with the job descriptions.

    Raises
    ------
    LauncherLoadError
        The given file cannot be loaded as a `Launcher`.

    See also
    --------
    save
    """
    with open(file_name, "rb") as file_obj:
        header = file_obj.readline()
        if header != _header():
            raise LauncherLoadError(file_name)
        version_size = struct.unpack("I", file_obj.read(struct.calcsize("I")))
        version_size = version_size[0]
        version = file_obj.read(version_size)
        if version != _magic():
            raise LauncherLoadError(file_name)

        base_to_file, system_name, depends, submit_args = pickle.load(file_obj)
        group = instance.InstanceGroup.load(file_obj)

    jd_base = os.path.dirname(os.path.abspath(file_name))
    if base_to_file != "":
        base = jd_base[:-len(base_to_file)]
    else:
        base = jd_base
    base = os.path.relpath(base)
    return Launcher(base, system_name, group, depends, submit_args)
