#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Launch and monitor local shell jobs."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2024, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import os
import subprocess
import sys

import sciexp2.expdef.system
import sciexp2.common.instance
from sciexp2.common import progress
from sciexp2.common.utils import execute_with_sigint


class System (sciexp2.expdef.system.System):
    """Manage local shell jobs."""

    STATE_CMD = "ps xwww"

    ASSUMES = []
    DEFINES = []

    def compute_state(self):
        # build instance group of job states
        self._jobs = sciexp2.common.instance.InstanceGroup()
        for instance in self._launchers:
            job = Job(self,
                      sciexp2.expdef.system.Job.compute_state(self, instance),
                      instance)
            self._jobs.add(job)


class Job (sciexp2.expdef.system.Job):
    """A local shell script job."""

    def state(self):
        state = self["_STATE"]
        if state == sciexp2.expdef.system.Job.DONE:
            name = self._system.get_relative_path(self["DONE"])
        elif state == sciexp2.expdef.system.Job.FAILED:
            name = self._system.get_relative_path(self["FAIL"])
        elif state in [sciexp2.expdef.system.Job.NOTRUN, sciexp2.expdef.system.Job.OUTDATED]:
            name = self._system.get_relative_path(self["LAUNCHER"])
        else:
            raise ValueError("Unknown job state: %r" % state)
        return state, name

    def submit(self, *args):
        launcher = os.sep.join([self._system._base, self["LAUNCHER"]])
        assert os.path.isfile(launcher)

        cmd = ["bash"] + self._submit_args(args) + [launcher]
        progress.verbose(" %s", " ".join(cmd))
        kwargs = dict(stdout=sciexp2.expdef.system._DEVNULL,
                      stderr=sciexp2.expdef.system._DEVNULL)
        if progress.level() > progress.LVL_PROGRESS:
            kwargs["stderr"] = progress.get_writer(sys.stderr)
        if progress.level() >= progress.LVL_VERBOSE:
            kwargs["stdout"] = progress.get_writer(sys.stdout)

        res = execute_with_sigint(cmd, **kwargs)
        if res != 0:
            raise subprocess.CalledProcessError(res, cmd)

    def kill(self, *args):
        raise Exception("Cannot kill local shell script jobs")
