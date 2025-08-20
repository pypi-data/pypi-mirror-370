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

# Description:
# The directive card_item can get 3 options.
#
# Options:
#  - title: takes the Name of the linked item
#  - image: takes the link to the picture in the static folder
#  - external: if set, the link opens in a new tab
#
# Usage:
# .. directive_wrapper::
#    :class: card-item-wrapper
#
#    .. card_item::
#       :title: Ansible
#       :image: ../_static/images/ansible.svg
#       :description: Ansible is a suite of software tools that enables infrastructure as code. It is open-source and the suite includes software provisioning, configuration management, and application deployment functionality.
#
#       - OTC Ansible Collection|https://docs.otc-service.com/ansible-collection-cloud
#       - Release Notes|https://docs.otc-service.com/ansible-collection-cloud


from docutils import nodes

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.util import logging

LOG = logging.getLogger(__name__)


class card_item(nodes.General, nodes.Element):
    pass


class CardItem(Directive):
    node_class = card_item
    option_spec = {
        'title': directives.unchanged_required,
        'image': directives.unchanged_required,
        'external': directives.unchanged,
        'description': directives.unchanged_required,
    }

    has_content = True

    def run(self):
        node = card_item()
        node['title'] = self.options['title']
        node['image'] = self.options['image']
        node['description'] = self.options['description']
        # Check, if 'external' is available in self.options and set the value for the node
        node['external'] = 'external' in self.options
        links = []
        for ent in self.content:
            _srv = ent.strip('- ')
            data_parts = _srv.split("|")
            title = data_parts[0]
            href = data_parts[1] if len(data_parts) > 1 else '#'
            links.append(
                dict(
                    title=title,
                    href=href
                )
            )
        node['links'] = links
        return [node]


def card_item_html(self, node):

    data = f'''
    <div class="card-item">
        <div>
            <picture>
                <source alt="{node['title']}" srcSet="/_static/images/dark/{node['image']}" media="(prefers-color-scheme: dark)" />
                <img class="card-item-img" alt="{node['title']}" src="/_static/images/light/{node['image']}">
            </picture>
            <div class="card-item-content">
                <h4 style="margin: 0px 0 1rem 0; font: var(--telekom-text-style-heading-4);">{node['title']}</h4>
                <div style="padding-bottom: 1rem;">
                    {node['description']}
                </div>
    '''
    for link in node['links']:
        data += f'''
                <a href="{link['href']}" class="link">{link['title']}</a>
        '''

    data += '''
            </div>
        </div>
    </div>
    '''
    self.body.append(data)
    raise nodes.SkipNode
