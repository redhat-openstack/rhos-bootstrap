# Copyright 2020 Red Hat, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import sys
from unittest import mock

sys.modules["dnf"] = mock.MagicMock()
sys.modules["dnf.cli.cli"] = mock.MagicMock()
sys.modules["dnf.cli.progress"] = mock.MagicMock()
sys.modules["dnf.exceptions"] = mock.MagicMock()
sys.modules["dnf.logging"] = mock.MagicMock()
sys.modules["dnf.transaction"] = mock.MagicMock()
sys.modules["dnf.yum.rpmtrans"] = mock.MagicMock()
sys.modules["libdnf"] = mock.MagicMock()
from rhos_bootstrap.utils import dnf


class TestDnfManager(unittest.TestCase):
    @mock.patch("rhos_bootstrap.utils.dnf.DnfManager.setup")
    def test_instance(self, setup_mock):
        obj = dnf.DnfManager.instance()
        self.assertIsInstance(obj, dnf.DnfManager)

        self.assertRaises(RuntimeError, dnf.DnfManager)


class TestDnfModule(unittest.TestCase):
    def test_obj(self):
        obj = dnf.DnfModule("foo", "bar")
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj.stream, "bar")
        self.assertEqual(obj.profile, None)

        obj = dnf.DnfModule("foo", 2.0, "s")
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj.stream, "2.0")
        self.assertEqual(obj.profile, "s")
