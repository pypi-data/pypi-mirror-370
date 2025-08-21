# -*- mode: python -*-

description = """
Base template for clusters using 'Grid Engine' (qsub).
"""

template = "gridengine"
system = "gridengine"

submit_args = ["-v", "LAUNCHER_BASE={{LAUNCHER_BASE}}", "-wd", "{{LAUNCHER_BASE}}"]

defaults = dict(
    JOB_STDIN="/dev/null",
    JOB_STDOUT="/dev/null",
    JOB_STDERR="/dev/null",
    QSUB_MAIL="ea",
    QSUB_OPTS="",
    STDOUT="out/{{LAUNCHER}}.stdout",
    STDERR="out/{{LAUNCHER}}.stderr",
    DONE="{{STDOUT}}",
    FAIL="{{STDERR}}",
    SYNCIN="",
    SYNCOUT="",
)
