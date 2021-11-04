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
from rhos_bootstrap import exceptions
from unittest import mock


class TestRhsmRepos(unittest.TestCase):
    def setUp(self):
        super().setUp()
        submgr_mock = mock.patch(
            "rhos_bootstrap.utils.rhsm.SubscriptionManager.instance"
        )
        self.submgr_mock = submgr_mock.start()
        self.addCleanup(submgr_mock.stop)

    def test_base(self):
        obj = repos.RhsmRepo("foo")
        self.assertEqual(obj.name, "foo")
        self.submgr_mock.assert_called_once()

    def test_save(self):
        inst_mock = mock.MagicMock()
        repos_mock = mock.MagicMock()
        inst_mock.repos = repos_mock
        self.submgr_mock.return_value = inst_mock
        obj = repos.RhsmRepo("foo")
        obj.save()
        repos_mock.assert_called_once_with(enable=["foo"])


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

    @mock.patch("os.access")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_save(self, isdir_mock, isfile_mock, access_mock):
        obj = repos.BaseYumRepo("foo", "bar", "url", True, False)

        isdir_mock.return_value = True
        isfile_mock.retun_value = False
        access_mock.return_value = True
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            obj.save()
            calls = [
                mock.call("/etc/yum.repos.d/foo.repo", "w", encoding="utf-8"),
                mock.call().__enter__(),
                mock.call().write(str(obj)),
                mock.call().__exit__(None, None, None),
            ]
            self.assertEqual(file_mock.mock_calls, calls)

        isdir_mock.return_value = False
        isfile_mock.retun_value = False
        access_mock.return_value = True
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(FileNotFoundError, obj.save)

        isdir_mock.return_value = True
        isfile_mock.retun_value = False
        access_mock.return_value = False
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(PermissionError, obj.save)

        isdir_mock.return_value = True
        isfile_mock.retun_value = True
        access_mock.side_effect = [True, False]
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(PermissionError, obj.save)

    def test_ceph(self):
        obj = repos.TripleoCephRepo("centos8-stream", "pacific")
        self.assertEqual(obj.name, "tripleo-centos-ceph-pacific")

        self.assertRaises(
            exceptions.DistroNotSupported, repos.TripleoCephRepo, "foo", "bar"
        )

    def test_centos(self):
        obj = repos.TripleoCentosRepo("centos8-stream", "highavailability")
        self.assertEqual(obj.name, "tripleo-centos-highavailability")

        self.assertRaises(
            exceptions.RepositoryNotSupported, repos.TripleoCentosRepo, "foo", "bar"
        )


class TestDeloreanRepos(unittest.TestCase):
    def setUp(self):
        requests_mock = mock.patch("requests.get")
        response_mock = mock.MagicMock()
        self.requests_mock = requests_mock.start()
        self.response_mock = response_mock
        self.requests_mock.return_value = self.response_mock
        self.addCleanup(requests_mock.stop)

    def test_base(self):
        self.response_mock.text = "data"
        obj = repos.TripleoDeloreanRepos("centos8", "master", "current-tripleo")

        self.assertEquals(obj.name, "tripleo-delorean-current-tripleo")
        self.assertEquals(obj.repo_data, "data")
        self.assertEquals(str(obj), "data")
        self.requests_mock.assert_called_with(
            "https://trunk.rdoproject.org/centos8-master/current-tripleo/delorean.repo"
        )

        obj = repos.TripleoDeloreanRepos("centos8", "master", "deps")
        self.assertEquals(obj.repo_data, "data")
        self.assertEquals(str(obj), "data")
        self.requests_mock.assert_called_with(
            "https://trunk.rdoproject.org/centos8-master/delorean-deps.repo"
        )

    @mock.patch("os.access")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_save(self, isdir_mock, isfile_mock, access_mock):
        self.response_mock.text = "data"
        obj = repos.TripleoDeloreanRepos("centos8", "master", "current-tripleo")

        isdir_mock.return_value = True
        isfile_mock.retun_value = False
        access_mock.return_value = True
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            obj.save()
            calls = [
                mock.call(
                    "/etc/yum.repos.d/tripleo-delorean-current-tripleo.repo",
                    "w",
                    encoding="utf-8",
                ),
                mock.call().__enter__(),
                mock.call().write(str(obj)),
                mock.call().__exit__(None, None, None),
            ]
            self.assertEqual(file_mock.mock_calls, calls)

        isdir_mock.return_value = False
        isfile_mock.retun_value = False
        access_mock.return_value = True
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(FileNotFoundError, obj.save)

        isdir_mock.return_value = True
        isfile_mock.retun_value = False
        access_mock.return_value = False
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(PermissionError, obj.save)

        isdir_mock.return_value = True
        isfile_mock.retun_value = True
        access_mock.side_effect = [True, False]
        with mock.patch("builtins.open", mock.mock_open()) as file_mock:
            self.assertRaises(PermissionError, obj.save)
