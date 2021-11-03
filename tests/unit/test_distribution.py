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

import yaml
import unittest
import sys
from rhos_bootstrap import exceptions
from unittest import mock

sys.modules["dnf"] = mock.MagicMock()
sys.modules["dnf.cli.cli"] = mock.MagicMock()
sys.modules["dnf.exceptions"] = mock.MagicMock()
sys.modules["dnf.logging"] = mock.MagicMock()
sys.modules["libdnf"] = mock.MagicMock()
from rhos_bootstrap import distribution

DUMMY_CENTOS_DATA = """
---
distros:
  centos:
    mirror:
      - http://mirror.centos.org
    versions:
      - 8-stream

versions:
  master: &master_branch
    distros: &distros_centos8
      - centos8-stream
    repos:
      centos8-stream:
        - highavailability
        - powertools
      ceph:
        - octopus
      delorean:
        - current-tripleo
        - deps
    modules:
      container-tools: rhel8
      virt: rhel
      python36: 3.6
  wallaby: *master_branch
"""

DUMMY_RHEL_DATA = """
---
distros:
  redhat:
    versions:
      - 8.2

versions:
  "16.1":
    distros:
      - rhel8.2
    repos:
      rhel8.2:
        - rhel-8-for-x86_64-baseos-eus-rpms
        - rhel-8-for-x86_64-appstream-eus-rpms
        - rhel-8-for-x86_64-highavailability-eus-rpms
      ansible:
        - ansible-2.9-for-rhel-8-x86_64-rpms
      virt:
        - advanced-virt-for-rhel-8-x86_64-rpms
      ceph:
        - rhceph-4-tools-for-rhel-8-x86_64-rpms
      openstack:
        - openstack-16.1-for-rhel-8-x86_64-rpms
      satellite:
        - satellite-tools-6.5-for-rhel-8-x86_64-rpms
      openvswitch:
        - fast-datapath-for-rhel-8-x86_64-rpms
    modules:
      container-tools: 2.0
      virt: rhel
      python36: 3.6
"""


class TestDistributionInfo(unittest.TestCase):
    @mock.patch("os.path.exists")
    def test_data(self, exists_mock):
        exists_mock.return_value = True
        dummy_data = yaml.safe_load(DUMMY_CENTOS_DATA)
        with mock.patch(
            "builtins.open", mock.mock_open(read_data=DUMMY_CENTOS_DATA)
        ) as open_mock:
            obj = distribution.DistributionInfo("centos", "8", "CentOS Stream")
            open_mock.assert_called_with(
                "/usr/share/rhos-bootstrap/centos.yaml", "r", encoding="utf-8"
            )
            self.assertEqual(obj.distro_data, dummy_data)
            self.assertEqual(obj.distro_id, "centos")
            self.assertEqual(obj.distro_version_id, "8")
            self.assertEqual(obj.distro_major_version_id, "8")
            self.assertTrue(obj.is_stream)
            self.assertEqual(obj.distro_minor_version_id, "")
            self.assertEqual(obj.distro_name, "CentOS Stream")
            self.assertEqual(obj.distros, dummy_data["distros"])
            self.assertEqual(obj.versions, dummy_data["versions"])
            self.assertEqual(obj.distro_normalized_id, "centos8-stream")
            self.assertEqual(str(obj), "centos8-stream")

        with mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data"):
            obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
            self.assertEqual(obj.distro_id, "rhel")
            self.assertEqual(obj.distro_version_id, "8.2")
            self.assertEqual(obj.distro_major_version_id, "8")
            self.assertFalse(obj.is_stream)
            self.assertEqual(obj.distro_minor_version_id, "2")
            self.assertEqual(obj.distro_normalized_id, "rhel8.2")

            with mock.patch("subprocess.Popen") as popen_mock:
                proc_mock = mock.MagicMock()
                comm_mock = mock.MagicMock()
                comm_mock.return_value = ["rhel\n8.2\nRed Hat Enterprise Linux"]
                proc_mock.__enter__.return_value.communicate = comm_mock
                popen_mock.return_value = proc_mock
                obj = distribution.DistributionInfo()
                self.assertEqual(obj.distro_id, "rhel")
                self.assertEqual(obj.distro_version_id, "8.2")
                self.assertEqual(obj.distro_major_version_id, "8")
                self.assertFalse(obj.is_stream)
                self.assertEqual(obj.distro_minor_version_id, "2")

        exists_mock.return_value = False
        self.assertRaises(
            exceptions.DistroNotSupported,
            distribution.DistributionInfo,
            "foo",
            "bar",
            "baz",
        )

    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_validate_distro(self, load_mock):
        obj = distribution.DistributionInfo("centos", "8", "CentOS Stream")
        obj._distro_data = yaml.safe_load(DUMMY_CENTOS_DATA)

        self.assertFalse(obj.validate_distro("doesnotexist"))
        self.assertTrue(obj.validate_distro("master"))

        obj._distro_version_id = "9"
        self.assertFalse(obj.validate_distro("master"))

    @mock.patch("rhos_bootstrap.utils.rhsm.SubscriptionManager.instance")
    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_validate_distro_rhel(self, load_mock, submgr_mock):
        inst_mock = mock.MagicMock()
        status_mock = mock.MagicMock()
        release_mock = mock.MagicMock()
        inst_mock.status = status_mock
        inst_mock.release = release_mock
        submgr_mock.return_value = inst_mock

        obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
        obj._distro_data = yaml.safe_load(DUMMY_RHEL_DATA)

        self.assertFalse(obj.validate_distro("doesnotexist"))

        release_mock.return_value = (0, "Release: 8.2", "")
        self.assertTrue(obj.validate_distro("16.1"))

        release_mock.return_value = (0, "Release: 8.3", "")
        self.assertRaises(
            exceptions.SubscriptionManagerConfigError, obj.validate_distro, "16.1"
        )

    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_version(self, lock_mock):
        dummy_data = yaml.safe_load(DUMMY_RHEL_DATA)
        obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
        obj._distro_data = dummy_data
        self.assertRaises(exceptions.VersionNotSupported, obj.get_version, "999")
        self.assertEqual(obj.get_version("16.1"), dummy_data["versions"]["16.1"])

    @mock.patch("rhos_bootstrap.utils.repos.TripleoDeloreanRepos")
    @mock.patch("rhos_bootstrap.utils.repos.TripleoCephRepo")
    @mock.patch("rhos_bootstrap.utils.repos.TripleoCentosRepo")
    @mock.patch("rhos_bootstrap.utils.repos.RhsmRepo")
    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_contruct_repos(
        self, load_mock, rhsm_mock, centos_mock, ceph_mock, dlrn_mock
    ):
        dummy_data = yaml.safe_load(DUMMY_RHEL_DATA)
        obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
        obj._distro_data = dummy_data

        obj.construct_repo("rhel8.2", "16.1", "rhel-repo")
        rhsm_mock.assert_called_once_with("rhel-repo")

        obj.construct_repo("ceph", "16.1", "ceph-repo")
        rhsm_mock.assert_called_with("ceph-repo")

        dummy_data = yaml.safe_load(DUMMY_CENTOS_DATA)
        obj = distribution.DistributionInfo("centos", "8", "CentOS Stream")
        obj._distro_data = dummy_data

        obj.construct_repo("centos8-stream", "master", "centos-repo")
        centos_mock.assert_called_once_with("centos8-stream", "centos-repo")

        obj.construct_repo("ceph", "master", "ceph-repo")
        ceph_mock.assert_called_once_with("centos8-stream", "ceph-repo")

        obj.construct_repo("delorean", "master", "dlrn-repo")
        dlrn_mock.assert_called_once_with("centos8", "master", "dlrn-repo")

        self.assertRaises(
            exceptions.RepositoryNotSupported, obj.construct_repo, "nope", "foo", "bar"
        )

    @mock.patch("rhos_bootstrap.distribution.DistributionInfo.construct_repo")
    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_repos(self, load_mock, const_repo):
        dummy_data = yaml.safe_load(DUMMY_RHEL_DATA)
        obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
        obj._distro_data = dummy_data

        res = obj.get_repos("16.1")
        self.assertEqual(len(res), 8)

        dummy_data = yaml.safe_load(DUMMY_CENTOS_DATA)
        obj = distribution.DistributionInfo("centos", "8", "CentOS Stream")
        obj._distro_data = dummy_data

        res = obj.get_repos("master")
        self.assertEqual(len(res), 5)

        dummy_data = yaml.safe_load(DUMMY_CENTOS_DATA)
        obj = distribution.DistributionInfo("centos", "8.2", "CentOS Stream")
        obj._distro_data = dummy_data

        res = obj.get_repos("master")
        self.assertEqual(len(res), 3)

    @mock.patch("rhos_bootstrap.utils.dnf.DnfModule")
    @mock.patch("rhos_bootstrap.distribution.DistributionInfo._load_data")
    def test_modules(self, load_mock, mod_mock):
        dummy_data = yaml.safe_load(DUMMY_RHEL_DATA)
        obj = distribution.DistributionInfo("rhel", "8.2", "Red Hat")
        obj._distro_data = dummy_data
        self.assertEqual(
            len(obj.get_modules("16.1")), len(dummy_data["versions"]["16.1"]["modules"])
        )
        mod_calls = [
            mock.call(*i) for i in dummy_data["versions"]["16.1"]["modules"].items()
        ]
        self.assertEqual(mod_mock.mock_calls, mod_calls)
