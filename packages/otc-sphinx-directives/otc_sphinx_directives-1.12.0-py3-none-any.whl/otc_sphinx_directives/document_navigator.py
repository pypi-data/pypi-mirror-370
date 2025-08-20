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

import otc_metadata.services

LOG = logging.getLogger(__name__)

METADATA = otc_metadata.services.Services()


class document_navigator(nodes.General, nodes.Element):
    pass


class DocumentNavigator(Directive):
    node_class = document_navigator
    option_spec = {
        'class': directives.unchanged,
        'document_type': directives.unchanged,
        'environment': directives.unchanged_required
    }

    has_content = False

    def run(self):
        node = self.node_class()
        node['document_type'] = self.options['document_type']
        node['environment'] = self.options.get('environment', 'public')
        node['class'] = self.options.get('class', 'navigator-container')
        return [node]


def document_navigator_html(self, node):
    # This method renders containers of service groups with links to the
    # document of the specified type
    data = f'<div class="{node["class"]} container-docsportal">'

    for cat in METADATA.service_categories:
        category = cat["name"]
        category_title = cat["title"]
        data += (
            f'<div class="card item-docsportal">'
            f'<div class="card-body">'
            f'<h5 class="card-title">{category_title}</h5></div>'
            f'<ul class="list-group list-group-flush">'
        )
        for k, v in METADATA.services_with_docs_by_category(
                category=category, environment=node['environment']).items():
            title = v["service_title"]
            for doc in v.get("docs", []):
                if "link" not in doc:
                    continue
                if "type" not in doc or doc["type"] != node["document_type"]:
                    continue
                title = doc["service_title"]
                link = doc.get("link")
                img = v["service_type"]
                data += (
                    f'<li class="list-group-item"><a href="{link}">'
                    f'<div class="row">'
                    f'<div class="col-2">'
                    f'<picture>'
                    f'<source class="icon-svg" srcSet="_static/images/services/dark/{img}.svg" media="(prefers-color-scheme: dark)" />'
                    f'<img class="icon-svg" src="_static/images/services/light/{img}.svg">'
                    f'</picture>'
                    f'</div>'
                    f'<div class="col-10">{title}</div>'
                    f'</div></a></li>'
                )

        data += '</ul></div>'

    data += '</div>'

    self.body.append(data)
    raise nodes.SkipNode
