SciExp²-ExpDef
==============

SciExp²-ExpDef (aka *Scientific Experiment Exploration - Experiment Definition*)
provides a framework for defining experiments, creating all the files needed for
them and, finally, executing the experiments.

SciExp²-ExpDef puts a special emphasis in simplifying experiment design space
exploration, using a declarative interface for defining permutations of the
different parameters of your experiments, and templated files for the scripts
and configuration files for your experiments. SciExp²-ExpDef supports various
execution platforms like regular local scripts and cluster jobs. It takes care
of tracking their correct execution, and allows selecting which experiments to
run (e.g., those with specific parameter values, or those that were not
successfully run yet).

You can find the documentation in:

  https://sciexp2-expdef.readthedocs.io


Copyright
=========

Copyright 2008-2023 Lluís Vilanova <llvilanovag@gmail.com>

Sciexp²-ExpDef is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Sciexp²-ExpDef is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
