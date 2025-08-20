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

from otc_sphinx_directives.directive_wrapper import directive_wrapper, directive_wrapper_latex, DirectiveWrapper
from otc_sphinx_directives.service_card import service_card, service_card_html, service_card_latex, ServiceCard
from otc_sphinx_directives.service_card_link import service_card_link, service_card_link_html, service_card_link_latex, ServiceCardLink
from otc_sphinx_directives.container_item import container_item, container_item_html, ContainerItem
from otc_sphinx_directives.service_navigator import service_navigator, service_navigator_html, ServiceNavigator
from otc_sphinx_directives.service_group import service_group, service_group_html, ServiceGroup
from otc_sphinx_directives.document_navigator import document_navigator, document_navigator_html, DocumentNavigator
from otc_sphinx_directives.navigator import navigator, navigator_html, Navigator
from otc_sphinx_directives.card_item import card_item, card_item_html, CardItem
from otc_sphinx_directives.docs_link import docs_link, docs_link_html, DocsLink
from otc_sphinx_directives.popular_services import (
    popular_services,
    popular_services_html,
    popular_services_latex,
    PopularServices
)


def setup(app):
    app.add_node(
        directive_wrapper,
        html=(directive_wrapper.visit_div, directive_wrapper.depart_div),
        latex=(directive_wrapper_latex, None))
    app.add_directive("directive_wrapper", DirectiveWrapper)
    app.add_node(
        service_card,
        html=(service_card_html, None),
        latex=(service_card_latex, None))
    app.add_directive("service_card", ServiceCard)
    app.add_node(container_item,
                 html=(container_item_html, None))
    app.add_node(card_item,
                 html=(card_item_html, None))
    app.add_node(navigator,
                 html=(navigator_html, None))
    app.add_node(service_navigator,
                 html=(service_navigator_html, None))
    app.add_node(document_navigator,
                 html=(document_navigator_html, None))
    app.add_node(service_group,
                 html=(service_group_html, None))
    app.add_node(docs_link,
                 html=(docs_link_html, None))
    app.add_node(
        service_card_link,
        html=(service_card_link_html, None),
        latex=(service_card_link_latex, None))
    app.add_node(
        popular_services,
        html=(popular_services_html, None),
        latex=(popular_services_latex, None)
    )
    app.add_directive("service_card_link", ServiceCardLink)
    app.add_directive("container_item", ContainerItem)
    app.add_directive("card_item", CardItem)
    app.add_directive("navigator", Navigator)
    app.add_directive("service_navigator", ServiceNavigator)
    app.add_directive("document_navigator", DocumentNavigator)
    app.add_directive("service_group", ServiceGroup)
    app.add_directive("docs_link", DocsLink)
    app.add_directive("popular_services", PopularServices)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
