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

from bs4 import BeautifulSoup

from otc_sphinx_directives.tests import base


def get_ref_content(wrapper_type=None):
    ref_content = ''

    if wrapper_type:
        ref_content = f'<{wrapper_type} class="ecs" id="7891011">'
    else:
        ref_content += '<div class="ecs" id="123456">'

    ref_content += (
        '<div class="admonition note">'
        '<p class="admonition-title">Note</p>'
        '<p>My note.</p>'
        '</div>'
    )
    if wrapper_type:
        ref_content += f'</{wrapper_type}>'
    else:
        ref_content += '</div>'

    return ref_content


class TestDirectiveWrapperHTML(base.TestCase):
    """Test basic rendering.

    This can be used to test that basic rendering works for these
    examples, so if someone breaks something we know.
    """

    @base.with_app(buildername='html', srcdir=base.template_dir('directive_wrapper'))
    def setUp(self, app):
        super(TestDirectiveWrapperHTML, self).setUp()
        self.app = app
        self.app.build()
        self.html = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.content = str(self.soup)

    def test_directive_wrapper(self):
        """Directive Wrapper test without type"""
        content = str(self.soup.find(id='123456'))
        ref_content = get_ref_content()
        self.assertEqual(
            ''.join(ref_content),
            content.replace('\n', '')
        )

    def test_directive_wrapper_with_type(self):
        """Directive Wrapper test with type"""
        content = str(self.soup.find(id='7891011'))
        ref_content = get_ref_content(wrapper_type='section')
        self.assertEqual(
            ''.join(ref_content),
            content.replace('\n', '')
        )
