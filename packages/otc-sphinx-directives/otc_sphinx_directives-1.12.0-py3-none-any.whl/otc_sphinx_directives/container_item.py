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
# The directive container_item can get 3 options.
#
# Options:
#  - title: takes the Name of the linked item
#  - image: takes the link to the picture in the static folder
#  - external: if set, the link opens in a new tab
#
# Usage:
# .. container:: row row-cols-1 row-cols-md-3 g-4
#
#    .. container_item::
#       :title: Ansible
#       :image: _static/images/ansible.svg
#       :external:
#
#       - Ansible Collection|https://docs.otc-service.com/ansible-collection-cloud


from docutils import nodes

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.util import logging

import otc_metadata.services

LOG = logging.getLogger(__name__)


class container_item(nodes.General, nodes.Element):
    pass


METADATA = otc_metadata.services.Services()


class ContainerItem(Directive):
    node_class = container_item
    option_spec = {
        'title': directives.unchanged,
        'image': directives.unchanged,
        'external': directives.unchanged
    }

    has_content = True

    def run(self):
        doctree_node = container_item()
        doctree_node['title'] = self.options['title']
        if 'image' in self.options:
            doctree_node['image'] = self.options['image']
        # Check, if 'external' is available in self.options and set the value for the node
        doctree_node['external'] = 'external' in self.options
        services = []
        for ent in self.content:
            _srv = ent.strip('- ')
            data_parts = _srv.split("|")
            title = data_parts[0]
            href = data_parts[1] if len(data_parts) > 1 else '#'
            services.append(
                dict(
                    title=title,
                    href=href
                )
            )
        doctree_node['services'] = services
        return [doctree_node]


def container_item_html(self, node):
    tmpl = """
        <div class="col">
          <div class="card">
            %(img)s
            <div class="card-body">
              <h5 class="card-title">%(title)s</h5>
            </div>
            %(data)s
          </div>
        </div>
        """

    if node['external']:
        node['data'] = (
            "<ul class='list-group list-group-flush'>"
            + "".join([('<li class="list-group-item"><a href="%(href)s" target="_blank" rel="noopener noreferrer">'
                        '<div class="col-md-10">%(title)s</div>'
                        '</a></li>'
                        % x)
                      for x in node['services']])
            + "</ul>")
    else:
        node['data'] = (
            "<ul class='list-group list-group-flush'>"
            + "".join([('<li class="list-group-item"><a href="%(href)s">'
                        '<div class="col-md-10">%(title)s</div>'
                        '</a></li>'
                        % x)
                      for x in node['services']])
            + "</ul>")
    node['img'] = ''
    if 'image' in node and node['image']:
        node['img'] = (
            f'<img src="{node["image"]}" '
            'class="card-img-top mx-auto">'
        )
    self.body.append(tmpl % node)
    raise nodes.SkipNode
