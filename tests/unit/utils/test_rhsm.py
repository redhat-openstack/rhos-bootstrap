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
from rhos_bootstrap.utils import rhsm
from rhos_bootstrap import exceptions
from unittest import mock


class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        # ensure we get a fresh instance for each test
        rhsm.SubscriptionManager._instance = None
        rhsm.SubscriptionManager._exe = None
        self.obj = rhsm.SubscriptionManager.instance()

    def test_instance(self):
        self.assertRaises(RuntimeError, rhsm.SubscriptionManager)
        self.assertIsInstance(self.obj, rhsm.SubscriptionManager)

        with mock.patch("shutil.which") as which_mock:
            which_mock.return_value = "/bin/subscription-manager"
            self.assertEqual(self.obj.exe, "/bin/subscription-manager")

        with mock.patch("shutil.which") as which_mock:
            self.obj._exe = None
            which_mock.return_value = None
            try:
                _ = self.obj.exe
            except Exception as e:
                self.assertEqual(str(e), "subscription-manager not available in PATH")

    @mock.patch("subprocess.Popen")
    def test_run(self, popen_mock):
        proc_mock = mock.MagicMock()
        comm_mock = mock.MagicMock()
        proc_mock.communicate = comm_mock
        popen_mock.return_value.__enter__.return_value = proc_mock

        self.obj._exe = "foo"

        comm_mock.return_value = ("foo", "bar")
        proc_mock.returncode = 0

        self.assertEqual(self.obj.run(["foo"]), (0, "foo", "bar"))

        comm_mock.return_value = ("foo", "bar")
        proc_mock.returncode = 1
        self.assertRaises(exceptions.SubscriptionManagerFailure, self.obj.run, ["foo"])

    def test_status(self):
        run_mock = mock.MagicMock()
        self.obj.run = run_mock

        run_mock.return_value = (0, "", "")
        self.assertEqual(self.obj.status(), (0, "", ""))
        run_mock.assert_called_with(["status"])

        run_mock.side_effect = exceptions.SubscriptionManagerFailure("foo")
        self.assertRaises(exceptions.SubscriptionManagerConfigError, self.obj.status)

    def test_release(self):
        run_mock = mock.MagicMock()
        self.obj.run = run_mock

        run_mock.return_value = (0, "Release: 8.2", "")
        self.assertEqual(self.obj.release(), (0, "Release: 8.2", ""))
        run_mock.assert_called_with(["release"])

        run_mock.side_effect = exceptions.SubscriptionManagerFailure("foo")
        self.assertRaises(exceptions.SubscriptionManagerConfigError, self.obj.release)

    def test_repos(self):
        run_mock = mock.MagicMock()
        self.obj.run = run_mock

        run_mock.return_value = (0, "", "")
        self.assertEqual(self.obj.repos(enable=["foo", "bar"]), (0, "", ""))
        run_mock.assert_called_with(["repos", "--enable=foo,bar"])

        run_mock.return_value = (0, "", "")
        self.assertEqual(self.obj.repos(disable=["foo", "bar"]), (0, "", ""))
        run_mock.assert_called_with(["repos", "--disable=foo,bar"])

        run_mock.side_effect = exceptions.SubscriptionManagerFailure("foo")
        self.assertRaises(exceptions.SubscriptionManagerFailure, self.obj.repos)
