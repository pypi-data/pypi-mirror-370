# -*- mode: python -*-

description = """
Base template for shell scripts (bash).
"""
template = "shell"
system = "shell"

defaults = dict(
    DONE="{{STDOUT}}",
    FAIL="{{STDERR}}",
    STDOUT="out/{{LAUNCHER}}.stdout",
    STDERR="out/{{LAUNCHER}}.stderr",
)
