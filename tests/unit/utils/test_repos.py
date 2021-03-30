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
from rhos_bootstrap.utils import repos


class RhsmRepos(unittest.TestCase):
    def test_base(self):
        obj = repos.RhsmRepo("foo")
        self.assertEqual(obj.name, "foo")


class TestYumRepos(unittest.TestCase):
    def test_base(self):
        obj = repos.BaseYumRepo("foo", "bar", "url", True, False)
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj.description, "bar")
        self.assertEqual(obj.baseurl, "url")
        self.assertTrue(obj.enabled)
        self.assertEqual(obj._enabled, 1)
        self.assertFalse(obj.gpgcheck)
        self.assertFalse(obj._gpgcheck, 0)
        self.assertEqual(obj.mirrorlist, None)
        self.assertEqual(obj.metalink, None)
        self.assertEqual(obj.gpgkey, None)

        obj.enabled = False
        self.assertFalse(obj.enabled)
        self.assertEqual(obj._enabled, 0)

        obj.gpgcheck = True
        self.assertTrue(obj.gpgcheck)
        self.assertEqual(obj._gpgcheck, 1)

    def test_base_to_string(self):
        obj = repos.BaseYumRepo(
            "foo", "bar", "url", True, False, "mirror", "meta", "gpg"
        )
        expected = "\n".join(
            [
                "[foo]",
                "name=bar",
                "baseurl=url",
                "mirrorlist=mirror",
                "metalink=meta",
                "enabled=1",
                "gpgcheck=0",
                "gpgkey=gpg",
                "",
            ]
        )
        self.assertEqual(str(obj), expected)

    def test_ceph(self):
        obj = repos.TripleoCephRepo("centos8-stream", "pacific")
        self.assertEqual(obj.name, "tripleo-centos-ceph-pacific")

    def test_centos(self):
        obj = repos.TripleoCentosRepo("centos8-stream", "highavailability")
        self.assertEqual(obj.name, "tripleo-centos-highavailability")
