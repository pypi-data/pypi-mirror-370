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


class service_group(nodes.General, nodes.Element):
    pass


METADATA = otc_metadata.services.Services()


class ServiceGroup(Directive):
    node_class = service_group
    option_spec = {
        'class': directives.unchanged,
        'service_category': directives.unchanged_required,
        'environment': directives.unchanged_required,
        'cloud_environment': directives.unchanged_required,
    }

    has_content = False

    def run(self):
        node = self.node_class()
        node['service_category'] = self.options.get('service_category')
        node['environment'] = self.options.get('environment', 'public')
        node['class'] = self.options.get('class', 'navigator-container')
        node['cloud_environment'] = self.options.get('cloud_environment', 'eu_de')
        return [node]


def service_group_html(self, node):
    # This method renders containers per each service of the category with all
    # links as individual list items
    data = '<div class="container-docsportal">'
    services_with_docs_by_category = METADATA.services_with_docs_by_category(
        node['service_category'],
        environment='public',
        cloud_environment=node['cloud_environment']).items()

    if node['environment'] == 'internal':
        internal_services_with_docs_by_category = METADATA.services_with_docs_by_category(
            node['service_category'],
            environment='internal',
            cloud_environment=node['cloud_environment']).items()
        for pk, service in services_with_docs_by_category:
            for ik, internal_service in internal_services_with_docs_by_category:
                if pk == ik:
                    if "docs" in service and "docs" in internal_service:
                        service["docs"] += internal_service["docs"]

    for k, v in services_with_docs_by_category:
        if not v.get("docs"):
            continue
        title = v["service_title"]
        data += (
            f'<div class="card item-docsportal">'
            f'<div class="card-body"><h5 class="card-title">'
            f'{title}</h5></div>'
            f'<ul class="list-group list-group-flush">'
        )
        for doc in v.get("docs", []):
            if "link" not in doc:
                continue
            title = doc["title"]
            link = doc.get("link")
            data += (
                f'<li class="list-group-item"><a href="{link}">'
                f'<div class="row">'
                f'<div class="col-md-10 col-sm-10 col-xs-10">{title}</div>'
                f'</div></a></li>'
            )
        # Row end
        data += '</ul></div>'
    data += '</div>'

    self.body.append(data)
    raise nodes.SkipNode
