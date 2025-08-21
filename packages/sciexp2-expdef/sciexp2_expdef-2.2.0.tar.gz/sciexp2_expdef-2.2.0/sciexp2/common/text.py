#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Text translation and extraction functions.

The translation and extraction functions are based on text templates that follow
a subset of the mustache syntax: https://mustache.github.io.

The accepted subset of mustache tags is:

* Variables: ``{{name}}``
* Sections: ``{{#name}}...{{/name}}``
* Inverted sections: ``{{^name}}...{{/name}}``

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019-2023, 2025, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import ast
from collections import OrderedDict
try:
    from collections.abc import Mapping
except:
    pass
import jinja2
import os
import pystache
import re
from .utils import OrderedSet
import six
import sys


class ParseError(Exception):
    pass


class VariableError(Exception):
    pass


class ExtractError(Exception):
    pass


def _get_parsed_elems(parsed):
    return parsed._parse_tree


def _pystache_parse(text, allow_nested=True, allow_inverted=True):
    try:
        pystache.render(text, {})
    except pystache.parser.ParsingError as e:
        _, _, exc_traceback = sys.exc_info()
        new_e = ParseError(str(e))
        six.reraise(new_e.__class__, new_e, exc_traceback)

    parsed = pystache.parse(text)

    elems = _get_parsed_elems(parsed)
    if len(elems) == 0 and len(text) > 0:
        raise ParseError("section start tag mismatch")

    def traverse(elems, nested):
        seen_node = False
        for elem in elems:
            if not isinstance(elem, six.string_types):
                seen_node = True

            if isinstance(elem, six.string_types):
                pass
            elif isinstance(elem, (pystache.parser._EscapeNode,
                                   pystache.parser._ChangeNode)):
                pass
            elif isinstance(elem, pystache.parser._SectionNode):
                nested = traverse(_get_parsed_elems(elem.parsed), True)
                if nested and not allow_nested:
                    raise ParseError(
                        "nested tags not allowed in section %r" % elem.key)
            elif isinstance(elem, pystache.parser._InvertedNode):
                if not allow_inverted:
                    raise ParseError("inverted sections not allowed: %s" % elem.key)
                nested = traverse(_get_parsed_elems(elem.parsed_section), True)
                if nested and not allow_nested:
                    raise ParseError(
                        "nested tags not allowed in inverted section %r" % elem.key)
            elif isinstance(elem, pystache.parser._PartialNode):
                raise ParseError(
                    "partial tags not allowed")
            else:
                raise ParseError("tag not allowed %r" % elem.__class__)

        return seen_node

    traverse(elems, False)

    return parsed


def get_variables(text, nested=False):
    """Get the variables referenced in the given text.

    Parameters
    ----------
    text : str
       Text to get variables from.
    nested : optional
       Whether to allow nested variables. Can have values "all" for all the
       variables, or "inner" for just the inner variables.

    Examples
    --------
    >>> get_variables("{{a}}")
    ['a']
    >>> get_variables("{{#a}} {{b}} {{/a}}", nested="inner")
    ['b']
    >>> get_variables("{{#a}} {{b}} {{/a}}", nested="all")
    ['a', 'b']

    """
    if nested not in [False, "all", "inner"]:
        raise ValueError("invalid nested value:", nested)

    parsed = _pystache_parse(text, allow_nested=bool(nested))
    if not nested:                    # equivalent due to exception raised above
        nested = "all"

    def traverse(elems, variables):
        added_variables = False

        for elem in elems:
            if isinstance(elem, pystache.parser._SectionNode):
                traversed_variables = traverse(_get_parsed_elems(elem.parsed),
                                               variables)
                if nested == "all":
                    variables.add(elem.key)
                    added_variables = True
                elif nested == "inner" and not traversed_variables:
                    variables.add(elem.key)
                    added_variables = True

            elif isinstance(elem, pystache.parser._InvertedNode):
                traversed_variables = traverse(_get_parsed_elems(elem.parsed_section),
                                               variables)
                if nested == "all":
                    variables.add(elem.key)
                    added_variables = True
                elif nested == "inner" and not traversed_variables:
                    variables.add(elem.key)
                    added_variables = True

            elif isinstance(elem, (pystache.parser._EscapeNode, pystache.parser._PartialNode)):
                variables.add(elem.key)
                added_variables = True

            else:
                assert isinstance(elem, six.string_types), elem

        return added_variables

    elems = _get_parsed_elems(parsed)
    variables = set()
    traverse(elems, variables)

    return sorted(variables)


class TemplatePath:
    """Wrapper to identify a path to a template file."""
    def __init__(self, path):
        self.value = path


class TemplateContents:
    """Wrapper"""
    def __init__(self, contents):
        self.value = contents


class Translator(object):
    """Translate a template text with given variables."""

    DEFAULT_BACKEND = "pystache"

    def __init__(self, template, backend=None, backend_options={}):
        """
        Parameters
        ----------
        template : str or TemplateContents or TemplatePath
            Template contents (when using `TemplateContents`) or path to a file
            containing them (when using `TemplatePath`). Passing a `str` is a
            shorthand for `TemplateContents(template)`.
        backend : {'pystache', 'jinja2'}, optional
            Name of the templating backend to process the contents of `template`.
        backend_options : dict, optional
            Options for the translation backend.

        Notes
        -----
        The "pystache" backend recognizes no options.

        The "jinja2" backend recognizes the following options:
        - `loader_search_path` : list of str, default [os.getcwd(), "/"]
            Paths to search for template and any files it includes. Uses the
            jinja2.FileSystemLoader() to find files.

        """
        if isinstance(template, str):
            template = TemplateContents(template)
        assert isinstance(template, tuple([TemplatePath, TemplateContents]))
        if backend is None:
            backend = Translator.DEFAULT_BACKEND
        backend_options = dict(backend_options)

        if backend == "pystache":
            if len(backend_options):
                raise RuntimeError("unknown backend option: " + list(backend_options.keys())[0])

            def identity(arg):
                return arg
            if isinstance(template, TemplatePath):
                template_txt = open(template.value).read()
            elif isinstance(template, TemplateContents):
                template_txt = template.value
            else:
                assert False
            parsed_template = _pystache_parse(template_txt, allow_nested=True)
            renderer = pystache.renderer.Renderer(search_dirs=[], file_extension=False,
                                                  partials=None, escape=identity,
                                                  missing_tags="strict")
            def render(env, recursive):
                template_new = template
                parsed_new = parsed_template
                while True:
                    template_old = template_new
                    parsed_old = parsed_new
                    try:
                        template_new = renderer.render(parsed_new, env)
                    except pystache.context.KeyNotFoundError as e:
                        _, _, exc_traceback = sys.exc_info()
                        new_e = VariableError("missing variable %s" % e.key)
                        six.reraise(new_e.__class__, new_e, exc_traceback)
                    except pystache.common.TemplateNotFoundError as e:
                        _, _, exc_traceback = sys.exc_info()
                        new_e = VariableError(str(e))
                        six.reraise(new_e.__class__, new_e, exc_traceback)

                    if not recursive:
                        break
                    elif template_old == template_new:
                        break

                    parsed_new = _pystache_parse(template_new, allow_nested=True)

                return template_new

            self._render = render

        elif backend == "jinja2":
            loader_search_path = backend_options.pop("loader_search_path",
                                                     [os.getcwd(), "/"])
            environment_filters = backend_options.pop("environment_filters", {})
            if len(backend_options):
                raise RuntimeError("unknown backend option: " + list(backend_options.keys())[0])

            def get_template(template):
                if isinstance(template, TemplatePath):
                    jinja_env = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(loader_search_path),
                        undefined=jinja2.StrictUndefined,
                    )
                    jinja_env.filters.update(environment_filters)
                    jinja_tpl = jinja_env.get_template(template.value)
                elif isinstance(template, TemplateContents):
                    jinja_env = jinja2.Environment(
                        loader=jinja2.DictLoader({"template": template.value}),
                        undefined=jinja2.StrictUndefined,
                    )
                    jinja_env.filters.update(environment_filters)
                    jinja_tpl = jinja_env.get_template("template")
                else:
                    assert False
                return jinja_tpl

            def render(env, recursive):
                template_new = template
                parsed_new = template
                jinja_tpl = get_template(template_new)

                while True:
                    template_old = template_new
                    parsed_old = parsed_new

                    try:
                        template_new = jinja_tpl.render(env)
                    except jinja2.exceptions.UndefinedError as e:
                        _, _, exc_traceback = sys.exc_info()
                        new_e = VariableError(e.message)
                        six.reraise(new_e.__class__, new_e, exc_traceback)

                    if not recursive:
                        break
                    elif template_old == template_new:
                        break

                    jinja_tpl = get_template(TemplateContents(template_new))

                return template_new

            self._render = render

        else:
            raise RuntimeError("invalid templating backend: " + str(backend))

    def translate(self, env, recursive=True):
        """Apply translation with given variables.

        Parameters
        ----------
        env : dict
            Mapping of variable names to their values.
        recursive : bool, optional
            Whether to apply translations recursively.

        Examples
        --------
        You can perform simple text translations:

        >>> t = Translator('Hello {{a}}')
        >>> t.translate({'a': 'you'})
        'Hello you'
        >>> t.translate({'a': [1, 2]})
        'Hello [1, 2]'

        And also recursive ones:

        >>> t.translate({'a': '{{b}}', 'b': 'them'})
        'Hello them'

        More complex cases like conditionals are also possible:

        >>> t = Translator('{{#a}}is true{{/a}}{{^a}}is false{{/a}}')
        >>> t.translate({'a': 1})
        'is true'
        >>> t.translate({'a': 0})
        'is false'

        Or even calls to functions (arguments are the unexpanded text on the template):

        >>> Translator('{{a}}').translate({'a': lambda: 'value'})
        'value'
        >>> Translator('{{#a}}{{b}}{{/a}}').translate(
        ...     {'a': lambda arg: 2*arg, 'b': 4})
        '44'
        >>> Translator('{{#a}}{{b}}{{/a}}').translate(
        ...     {'a': lambda arg: " ".join(list(arg))})
        '{ { b } }'


        And expansion of nested variables with multiple values is also possible:

        >>> Translator('{{#a}}A.B=={{b}} {{/a}}').translate({'a': [{'b': 1}, {'b': 2}]})
        'A.B==1 A.B==2 '

        """
        if not isinstance(env, Mapping):
            raise TypeError("not a mapping: %r" % env)

        return self._render(env, recursive)

    def translate_many(self, envs, recursive=True, ignore_variable_error=False,
                       with_envs=False):
        """Apply translation with given set of variables.

        Parameters
        ----------
        envs : sequence of dict
            Sequence of variable names to value mappings to apply the
            translation for.
        recursive : bool, optional
            Whether to apply translations recursively.
        ignore_variable_error : bool, optional
            Ignore translations for variable maps that have missing variables.
        with_envs : bool, optional
            Get the set of maps that led to each translation.

        Returns
        -------
        list of str
            Translations when ``with_envs`` is ``False``.
        list of (str, [env])
            Translations with their corresponding variable maps when
            ``with_envs`` is ``True``.

        Notes
        -----
        The result is guaranteed to maintain the order of the elements of
        `envs`.

        Examples
        --------
        You can very easily translate a sequence of variable maps:

        >>> t = Translator('Hello {{a}}')
        >>> t.translate_many([{'a': 'you'}, {'a': 'them'}])
        ['Hello you', 'Hello them']

        Multiple maps can also translate into the same text:

        >>> t.translate_many([{'a': 'you'}, {'a': 'them', 'b': 1}, {'a': 'them', 'b': 2}])
        ['Hello you', 'Hello them']

        But you can also get the maps that led to each translation:

        >>> t = Translator('Hello {{a}}')
        >>> translated = t.translate_many([{'a': 'you'}, {'a': 'them', 'b': 1},
        ...                                {'a': 'them', 'b': 2}], with_envs=True)
        >>> translated == [('Hello you', [{'a': 'you'}]),
        ...                ('Hello them', [{'a': 'them', 'b': 1},
        ...                                {'a': 'them', 'b': 2}])]
        True

        """
        if with_envs:
            result = OrderedDict()
            def add(key, val):
                if key not in result:
                    result[key] = []
                result[key].append(val)
        else:
            result_track = OrderedSet()
            result = []
            def add(key, val):
                if key not in result_track:
                    result_track.add(key)
                    result.append(key)

        for env in envs:
            try:
                text = self.translate(env)
            except VariableError:
                if not ignore_variable_error:
                    raise
            else:
                add(text, env)

        if with_envs:
            return list(result.items())
        else:
            return result


def translate(template, env, **kwargs):
    """Shorthand for ``Translator(template).translate(env, **kwargs)``."""
    backend = kwargs.pop("backend", None)
    backend_options = kwargs.pop("backend_options", {})
    translator = Translator(template=template, backend=backend,
                            backend_options=backend_options)
    return translator.translate(env=env, **kwargs)


def translate_many(template, envs, **kwargs):
    """Shorthand for ``Translator(template).translate_many(envs, **kwargs)``."""
    backend = kwargs.pop("backend", None)
    backend_options = kwargs.pop("backend_options", {})
    translator = Translator(template=template, backend=backend,
                            backend_options=backend_options)
    return translator.translate_many(envs=envs, **kwargs)


class Extractor(object):
    """Extract a dict with the variable values that match a given template.

    Variables and sections on the template are used to define regular
    expressions, following Python's `syntax
    <http://docs.python.org/library/re.html#regular-expression-syntax>`_.

    """

    def __init__(self, template):
        """
        Parameters
        ----------
        template : str
            Template text to extract from.

        """
        self._template = template
        parsed = _pystache_parse(template, allow_nested=False, allow_inverted=False)
        regex = ""
        variables = {}
        for elem in _get_parsed_elems(parsed):
            if isinstance(elem, six.string_types):
                regex += elem

            elif isinstance(elem, pystache.parser._SectionNode):
                if elem.key in variables:
                    raise ParseError(
                        "regex for variable %s has already been set: %s" % (
                            elem.key, variables[elem.key]))
                elem_regex = _get_parsed_elems(elem.parsed)
                if len(elem_regex) == 0:
                    raise ParseError(
                        "regex for variable %s cannot be empty" % elem.key)
                elem_regex = elem_regex[0]
                assert len(elem_regex) > 0, template
                variables[elem.key] = elem_regex
                regex += "(?P<%s>%s)" % (elem.key, elem_regex)

            elif isinstance(elem, pystache.parser._EscapeNode):
                if elem.key in variables:
                    regex += "(?P=%s)" % elem.key
                else:
                    elem_regex = ".+"
                    variables[elem.key] = elem_regex
                    regex += "(?P<%s>%s)" % (elem.key, elem_regex)

            else:
                # silently ignore
                pass

        self._cre = re.compile(regex)

    def extract(self, text):
        """Apply extraction to given text.

        Parameters
        ----------
        text : str
            Text to extract from.

        Examples
        --------
        You can perform simple text extractions, where variables correspond to
        the simple regex ``.+``:

        >>> e = Extractor('Hello {{a}}')
        >>> e.extract('Hello world')
        {'a': 'world'}
        >>> e.extract('Hello 123!')
        {'a': '123!'}

        More complex regexes can be specified using section tags:

        >>> Extractor('Hello {{#a}}[0-9]+{{/a}}.*').extract('Hello 123!')
        {'a': 123}

        And using the same variable on multiple tags ensures they all match the
        same contents:

        >>> extracted = Extractor('{{#a}}[0-9]+{{/a}}.*{{a}}{{b}}').extract('123-123456')
        >>> extracted == {'a': 123, 'b': 456}
        True

        """
        match = self._cre.match(text)
        if match is None:
            raise ExtractError(
                "could not extract variables from template %r (regex: %r)" % (
                    self._template, self._cre.pattern))
        def retype_maybe(val):
            try:
                return ast.literal_eval(val)
            except:
                pass
            return val
        return dict((key, retype_maybe(val))
                    for (key, val) in match.groupdict().items())


def extract(template, text):
    """Shorthand for ``Extractor(template).extract(text)``."""
    return Extractor(template).extract(text)


__all__ = [
    "ParseError", "VariableError", "ExtractError",
    "get_variables",
    "TemplatePath", "TemplateContents",
    "Translator", "translate", "translate_many",
    "Extractor", "extract",
]
