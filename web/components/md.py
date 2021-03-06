"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import (
    Typed, ForwardTyped, Enum, Int, Bool, List, Dict, observe
)

from enaml.core.declarative import d_
from .raw import Raw, ProxyRawNode


class ProxyMarkdown(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Markdown)

    def set_safe_mode(self, mode):
        raise NotImplementedError

    def set_output_format(self, output_format):
        raise NotImplementedError

    def set_tab_length(self, length):
        raise NotImplementedError

    def set_extensions(self, extensions):
        raise NotImplementedError

    def set_extensions_config(self, config):
        raise NotImplementedError


class Markdown(Raw):
    """ A block for rendering Markdown source. """

    #: Extensions to use when rendering
    extensions = d_(List(default=[
        "markdown.extensions.codehilite",
        "markdown.extensions.fenced_code",
        "markdown.extensions.tables",
    ])).tag(attr=False)

    #: Configuration for them
    extension_configs = d_(Dict(default={
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
    })).tag(attr=False)

    #: Disallow raw HTMl
    safe_mode = d_(Bool()).tag(attr=False)

    #: Output format
    output_format = d_(Enum("xhtml", "html5")).tag(attr=False)

    #: Tab size
    tab_length = d_(Int(4)).tag(attr=False)

    #: Reference to the proxy
    proxy = Typed(ProxyMarkdown)

    @observe('extensions', 'extension_configs', 'safe_mode', 'output_format',
             'tab_length')
    def _update_proxy(self, change):
        """ The superclass implementation is sufficient. """
        super(Markdown, self)._update_proxy(change)
