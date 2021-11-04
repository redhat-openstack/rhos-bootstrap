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
from rhos_bootstrap import exceptions as ex


class TestExceptions(unittest.TestCase):
    def test_distro_not_supported(self):
        obj = ex.DistroNotSupported("foo")
        self.assertEqual(str(obj), "Distribution foo is not currently supported")

    def test_version_not_supported(self):
        obj = ex.VersionNotSupported("foo")
        self.assertEqual(str(obj), "Version foo is not currently supported")

    def test_repo_not_supported(self):
        obj = ex.RepositoryNotSupported("foo")
        self.assertEqual(str(obj), "Repository foo is unknown")

    def test_subscription_manager_config_error(self):
        obj = ex.SubscriptionManagerConfigError()
        self.assertEqual(
            str(obj),
            "Red Hat Subscription Manager is not currently configured correctly",
        )

    def test_subscription_manager_failure(self):
        obj = ex.SubscriptionManagerFailure("foo")
        self.assertEqual(str(obj), "Failed running subscription-manager foo")
