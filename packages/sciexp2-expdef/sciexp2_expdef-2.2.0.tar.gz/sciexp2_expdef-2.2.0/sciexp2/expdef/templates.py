#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Common functionality for launcher templates.

Two files can be provided for each template:

- **template-name.tpl**

  The template itself.

  This is the file that will be produced (through :term:`translation`).

- **template-name.dsc**

  The template descriptor.

  Contains a predefined set of attributes (see `Template`).

  The use of the ``parent`` attribute is encouraged to write template
  refinements, so that instead of writing new ``.dsc`` and ``.tpl`` files you
  can simply write a single ``.dsc`` and declare its ``parent``. Then, any
  attribute in the ``.dsc`` file (other than the set of predefined attributes)
  will be used to refine the variables of the parent template.

The templates are searched for in the paths listed in :data:`SEARCH_PATH`,
where you can add new directories if necessary.

.. autodata:: sciexp2.expdef.templates.SEARCH_PATH

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2009-2023, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import glob
import os
import six
import pydoc

from sciexp2.common import text
import sciexp2.expdef.system


#: Paths to search for available templates.
#:
#: The order of the list establishes which template will be used in case it
#: exists in more than one directory.
#:
#: Includes the current directory and the `templates` directory shipped with
#: SciExp².
SEARCH_PATH = [
    os.curdir,
    os.sep.join([os.path.dirname(__file__), "templates"]),
    ]


def _get_path(name):
    """Get the path to descriptor or template file with given name."""
    for path in SEARCH_PATH:
        file_path = os.sep.join([path, name])
        if os.path.isfile(file_path):
            return file_path
    return None


_DOC = pydoc.TextDoc()


def _bold(text):
    return _DOC.bold(text)


def _indent(text):
    return _DOC.indent(text)


class _FakeDict (dict):
    def __getitem__(self, key):
        if key not in self:
            dict.__setitem__(self, key, "")
        return dict.__getitem__(self, key)


class TemplateError (Exception):
    """Error retrieving template file."""
    def __init__(self, message):
        Exception.__init__(self, message)


class Template:
    """A launcher template.

    The non-string attributes must be specified in the template descriptor file
    as the string identifying the object name.

    Attributes
    ----------
    name : str
        Template name (taken from the file name of descriptor file).
    description : str
        Template description.
    system : `sciexp2.expdef.system.System`, optional
        Name of the execution system this template if for. Can be inherited
        from `parent`.
    template : str, optional
        The template file this descriptor uses. For file ``name.tpl`` you must
        use ``name``. Can be inherited from `parent`.
    parent : `sciexp2.templates.Template`, optional
        Parent template to inherit from.
    submit_args : list of str, optional
        Extra arguments passed to the job submission program.
    overrides : dict, optional
        Dictionary mapping variable names in the parent template to their
        corresponding values for this template.
    defaults : dict, optional
        Dictionary mapping variable names in the template to their
        corresponding values, in case the user provides none.

    Notes
    -----
    Template descriptor files can use the following variables to refer to the
    corresponding attributes set in their parent template:

    - `parent_submit_args`
    - `parent_overrides`
    - `parent_defaults`

    Argument `submit_args` can contain variable *LAUNCHER_BASE*, which contains
    the absolute path to the base output directory
    (`expdef.experiments.Experiments.out`).

    """

    _LOADING = []

    def __init__(self, name):
        """Create a new template object from its descriptor file."""

        if name in Template._LOADING:
            raise TemplateError("Circular template dependency: %s"
                                % " -> ".join(Template._LOADING + [name]))
        self.name = name

        # load descriptor file
        dsc_path = _get_path(self.name + ".dsc")
        if dsc_path is None:
            raise TemplateError("Cannot find template descriptor file '%s'" %
                                (self.name + ".dsc"))
        dsc = open(dsc_path, "r").read()
        # load to know who's the parent
        globals_ = dict(
            parent_submit_args=[],
            parent_overrides=_FakeDict(),
            parent_defaults=_FakeDict(),
        )
        namespace = {}
        six.exec_(dsc, globals_, namespace)

        self._init_parent(namespace, dsc_path)

        # reload with parent-specific information
        if self.parent is None:
            globals_ = dict(
                parent_submit_args=[],
                parent_overrides={},
                parent_default={},
            )
        else:
            globals_ = dict(
                parent_submit_args=list(self.parent.submit_args),
                parent_overrides=dict(self.parent.overrides),
                parent_default=dict(self.parent.defaults),
            )
        namespace = {}
        six.exec_(dsc, globals_, namespace)

        namespace.pop("parent", None)
        self._init_description(namespace, dsc_path)
        self._init_system(namespace, dsc_path)
        self._init_template(namespace, dsc_path)
        self._init_submit_args(namespace)
        self._init_overrides(namespace)
        self._init_defaults(namespace)

        # do not accept any other variable in the descriptor
        if len(namespace) > 0:
            raise TemplateError("Unknown variables in template %s: %s" %
                                (dsc_path, ", ".join(namespace)))

    def _init_parent(self, namespace, dsc_path):
        parent_name = namespace.pop("parent", None)
        if parent_name is not None:
            Template._LOADING.append(self.name)
            try:
                self.parent = get(parent_name)
            except TemplateError as e:
                raise TemplateError("When loading parent of %s: %s" %
                                    (dsc_path, e.message))
            Template._LOADING.remove(self.name)
        else:
            self.parent = None

    def _init_description(self, namespace, dsc_path):
        self.description = namespace.pop("description", None)
        if self.description is None:
            raise TemplateError("Template descriptor without 'description': "
                                "%s" % dsc_path)

    def _init_system(self, namespace, dsc_path):
        self.system = None
        if self.parent is not None:
            self.system = self.parent.system

        system_name = namespace.pop("system", None)
        if system_name:
            try:
                self.system = sciexp2.expdef.system.get(system_name)
            except sciexp2.expdef.system.SystemError as e:
                raise TemplateError("Error loading 'system' for template "
                                    "%s: %s" % (dsc_path, e.message))
        elif self.system is None:
            raise TemplateError("Template descriptor without 'system': "
                                "%s" % dsc_path)

    def _init_template(self, namespace, dsc_path):
        self.template = None
        if self.parent is not None:
            self.template = self.parent.template
            self.template_path = self.parent.template_path

        template_name = namespace.pop("template", None)
        if template_name:
            self.template = template_name
            self.template_path = _get_path(self.template + ".tpl")
            if self.template_path is None:
                raise TemplateError("Template descriptor with incorrect "
                                    "'template' %r: %s" %
                                    (self.template, dsc_path))
        elif self.template is None:
            raise TemplateError("Template descriptor without 'template': "
                                "%s" % dsc_path)

    def _init_submit_args(self, namespace):
        parent_submit_args = self.parent.submit_args if self.parent else []
        self.submit_args = namespace.pop("submit_args", parent_submit_args)

    def _init_overrides(self, namespace):
        parent_overrides = self.parent.overrides if self.parent else {}
        self_overrides = namespace.pop("overrides", {})
        self.overrides = dict(self_overrides)
        for key, val in parent_overrides.items():
            new_val = text.translate(val, self_overrides)
            if new_val != val or key not in self_overrides:
                self.overrides[key] = new_val

    def _init_defaults(self, namespace):
        if self.parent:
            self.defaults = dict(self.parent.defaults)
        else:
            self.defaults = {}
        self.defaults.update(namespace.pop("defaults", {}))

    def get_short_description(self, get_long=False):
        """Get short description."""
        res = [_bold(self.name)]
        contents = []
        contents += [self.description.strip()]
        has_parent = self.parent is not None
        if has_parent:
            contents += [_bold("Parent  : ") + self.parent.name]
        if get_long or not has_parent:
            contents += [_bold("System  : ") + self.system.name]
            contents += [_bold("Template: ") + self.template]
        res.append(_indent("\n".join(contents)))
        return "\n".join(res)

    def get_description(self):
        """Get a full description."""
        res = [self.get_short_description(True)]
        contents = []

        if len(self.submit_args) > 0:
            contents += [_bold("Submit arguments:")]
            contents += [_indent(" ".join(self.submit_args))]
        if len(self.defaults) > 0:
            contents += [_bold("Default values:")]
            defaults = ["%-15s :: \"%s\"" % (var, val)
                        for var, val in sorted(six.iteritems(self.defaults))]
            contents += [_indent("\n".join(defaults))]

        with open(self.template_path) as contents_file:
            mandatory_vars = set(text.get_variables(contents_file.read()))
            mandatory_vars |= set([
                v
                for val in six.itervalues(self.overrides)
                for v in text.get_variables(val)])
            mandatory_vars -= self.system.assumes()
            mandatory_vars -= self.system.defines()
            mandatory_vars -= set(self.defaults)
            if len(mandatory_vars) > 0:
                contents += [_bold("Mandatory variables:")]
                mandatory = sorted([str(var) for var in mandatory_vars])
                contents += [_indent("\n".join(mandatory))]

        with open(self.template_path) as contents_file:
            contents += [_bold("Contents:")]
            fcontents = "".join(contents_file.readlines())
            overrides = dict(self.overrides)
            for var in text.get_variables(fcontents):
                if var not in overrides:
                    overrides[var] = "{{%s}}" % var
            fcontents = text.translate(fcontents, overrides, recursive=False)
            contents += [_indent(fcontents)]

        res += [_indent("\n".join(contents))]
        return "\n".join(res)


_TEMPLATES = {}


def get(name):
    """Get a Template object by name."""
    if name in _TEMPLATES:
        res = _TEMPLATES[name]
    else:
        res = Template(name)
        _TEMPLATES[name] = res
    return res


def _get_all_templates():
    """Search for all possible template file descriptors."""
    for path in SEARCH_PATH:
        for file_path in glob.iglob(path + os.sep + "*.dsc"):
            name = os.path.basename(file_path)[:-4]
            get(name)


def get_description():
    """Get a short description of all available templates."""
    _get_all_templates()
    return "\n\n".join([tpl.get_short_description()
                        for tpl in six.itervalues(_TEMPLATES)])
