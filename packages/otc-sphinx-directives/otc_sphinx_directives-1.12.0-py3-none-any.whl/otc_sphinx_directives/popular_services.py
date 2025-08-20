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

from otc_metadata.analytics.data import AnalyticsData
import otc_metadata.services

LOG = logging.getLogger(__name__)
METADATA = otc_metadata.services.Services()


class popular_services(nodes.General, nodes.Element):
    pass


class PopularServices(Directive):
    node_class = popular_services

    option_spec = {
        'cloud_environment': directives.unchanged,
    }

    has_content = False

    def run(self):
        node = self.node_class()
        cloud_env = self.options.get('cloud_environment', 'eu_de')
        node['cloud_environment'] = cloud_env
        return [node]


def popular_services_html(self, node):
    # This method renders containers per each service of the category with all
    # links as individual list items

    data = ''
    analytics_data = AnalyticsData().analytics_data_by_cloud_environment(cloud_environment=node['cloud_environment'])
    cloud_env_services = METADATA.all_services_by_cloud_environment_as_dict(cloud_environment=node['cloud_environment'], environments=['public'])
    popular_services = []

    for svc in analytics_data:
        if svc in cloud_env_services:
            popular_services.append(cloud_env_services[svc])

    for svc in popular_services:
        data += f'''
            <div class="card item-pop-svc item-pop-svc-flex">
                <a href="/{svc['service_uri']}/">
                    <div class="card-body">
                        <div class="header">
                            <picture>
                                <source class="icon-svg" srcset="_static/images/services/dark/{svc['service_type']}.svg" media="(prefers-color-scheme: dark)">
                                <img class="icon-svg" src="_static/images/services/light/{svc['service_type']}.svg">
                            </picture>
                            <h4>{svc['service_title']}</h4>
                        </div>
        '''
        if 'description' in svc:
            data += f'''
                        <p>{svc['description']}</p>
            '''

        data += '''
                    </div>
                </a>
            </div>
        '''

    self.body.append(data)
    raise nodes.SkipNode


def popular_services_latex(self, node):
    # do nothing
    raise nodes.SkipNode
