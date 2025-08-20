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


class docs_link(nodes.General, nodes.Element):
    pass


class DocsLink(Directive):
    node_class = docs_link

    has_content = True

    option_spec = {
        'description': directives.unchanged,
        'link': directives.unchanged
    }

    def run(self):
        node = self.node_class()
        for k in self.option_spec:
            if self.options.get(k):
                node[k] = self.options.get(k)

        confpy_config = self.state.document.settings.env.config
        node["environment"] = confpy_config.otcdocs_doc_environment
        node["search_environment"] = confpy_config.otcdocs_search_environment

        return [node]


def docs_link_html(self, node):
    # This method renders containers per each service of the category with all
    # links as individual list items

    data = ''
    if node["search_environment"] == "hc_de":
        if node["environment"] == "public":
            data = f'<a class="reference external" href="https://docs.otc.t-systems.com/{node["link"]}" target="_blank" rel="external noopener noreferrer">{node["description"]}</a>'
        elif node["environment"] == "internal":
            data = f'<a class="reference external" href="https://docs-int.otc-service.com/{node["link"]}" target="_blank" rel="external noopener noreferrer">{node["description"]}</a>'
        else:
            LOG.error('No otcdocs_doc_environment for link generation of docs_link in confpy specified!')

    elif node["search_environment"] == "hc_swiss":
        if node["environment"] == "public":
            data = f'<a class="reference external" href="https://docs.sc.otc.t-systems.com/{node["link"]}" target="_blank" rel="external noopener noreferrer">{node["description"]}</a>'
        elif node["environment"] == "internal":
            data = f'<a class="reference external" href="https://docs-swiss-int.otc-service.com/{node["link"]}" target="_blank" rel="external noopener noreferrer">{node["description"]}</a>'
        else:
            LOG.error('No otcdocs_doc_environment for link generation of docs_link in confpy specified!')

    else:
        LOG.error('None or not supported otcdocs_search_environment for link generation of docs_link in confpy specified!')

    self.body.append(data)
    raise nodes.SkipNode


def docs_link_latex(self, node):
    # do nothing
    raise nodes.SkipNode
