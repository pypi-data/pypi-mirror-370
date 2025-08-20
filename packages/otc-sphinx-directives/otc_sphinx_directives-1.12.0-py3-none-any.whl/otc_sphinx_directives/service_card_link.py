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

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.util import logging


LOG = logging.getLogger(__name__)


class service_card_link(nodes.General, nodes.Element):
    pass


class ServiceCardLink(Directive):
    node_class = service_card_link

    option_spec = {
        'title': directives.unchanged_required,
        'url': directives.unchanged_required,
        'description': directives.unchanged,
    }

    has_content = False

    def run(self):
        node = self.node_class()
        node['title'] = self.options['title']
        node['url'] = self.options['url']
        node['description'] = self.options.get('description')
        return [node]


def service_card_link_html(self, node):
    # This method renders containers per each service of the category with all
    # links as individual list items

    data = f'''
    <div class="card item-sbv item-sbv-flex">
        <a href="{node['url']}" target="_blank">
            <div class="card-body">
                <h4 style="display: inline-flex; width: 100%; justify-content: space-between;">{node['title']} <scale-icon-navigation-external-link accessibility-title="external-link"/></h4>
                <p>
    '''

    if node['description']:
        data += f'''
            {node['description']}
        '''

    data += '''
                </p>
            </div>
        </a>
    </div>
    '''

    self.body.append(data)
    raise nodes.SkipNode


def service_card_link_latex(self, node):
    # do nothing
    raise nodes.SkipNode
