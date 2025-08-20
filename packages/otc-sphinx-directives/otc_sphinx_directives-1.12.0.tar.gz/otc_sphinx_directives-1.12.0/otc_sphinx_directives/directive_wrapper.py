# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

LOG = logging.getLogger(__name__)


class directive_wrapper(nodes.General, nodes.Element):

    def __init__(self, text=None, **args):
        super(directive_wrapper, self).__init__()
        self['class'] = ''
        self['id'] = ''
        self['style'] = ''
        self['wrapper_type'] = 'div'

    @staticmethod
    def visit_div(self, node):
        options = ""
        if node['id']:
            options += f'id="{node["id"]}" '
        if node['class']:
            options += f'class="{node["class"]}" '
        if node['style']:
            options += f'style="{node["style"]}" '

        self.body.append(
            self.starttag(node, f'{node["wrapper_type"]} {options}'))

    @staticmethod
    def depart_div(self, node):
        self.body.append(f'</{node["wrapper_type"]}>\n')


class DirectiveWrapper(SphinxDirective):
    node_class = directive_wrapper
    option_spec = {
        'class': directives.unchanged,
        'id': directives.unchanged,
        'wrapper_type': directives.unchanged,
        'style': directives.unchanged
    }

    has_content = True

    def run(self):
        text = '\n'.join(self.content)
        node = directive_wrapper(text)
        node['class'] = self.options.get('class', '')
        node['id'] = self.options.get('id', '')
        node['wrapper_type'] = self.options.get('wrapper_type', 'div')
        node['style'] = self.options.get('style', '')
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def directive_wrapper_latex(self, node):
    # do nothing
    raise nodes.SkipNode
