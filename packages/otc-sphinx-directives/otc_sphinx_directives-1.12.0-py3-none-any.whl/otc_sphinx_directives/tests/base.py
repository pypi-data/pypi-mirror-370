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

import os
import tempfile
import testtools

from sphinx.testing.path import path
from sphinx.testing.util import SphinxTestApp


def template_dir(name=""):
    return os.path.join(os.path.dirname(__file__), 'templates', name)


_TRUE_VALUES = ('True', 'true', '1', 'yes')


class with_app:
    def __init__(self, **kwargs):
        if 'srcdir' in kwargs:
            self.srcdir = path(kwargs['srcdir'])
        self.sphinx_app_args = kwargs

    def __call__(self, f):
        def newf(*args, **kwargs):
            with tempfile.TemporaryDirectory() as tmpdirname:
                tmpdir = path(tmpdirname)
                tmproot = tmpdir / self.srcdir.basename()
                self.srcdir.copytree(tmproot)
                self.sphinx_app_args['srcdir'] = tmproot
                self.builddir = tmproot.joinpath('_build')

                app = SphinxTestApp(freshenv=True, **self.sphinx_app_args)

                f(*args, app, **kwargs)

                app.cleanup()
        return newf


class TestCase(testtools.TestCase):

    """Test case base class for all unit tests."""

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(TestCase, self).setUp()
