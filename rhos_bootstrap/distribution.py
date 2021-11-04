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

from __future__ import print_function

import logging
import os
import subprocess
import yaml

from rhos_bootstrap import constants
from rhos_bootstrap import exceptions
from rhos_bootstrap.utils import repos
from rhos_bootstrap.utils import dnf
from rhos_bootstrap.utils import rhsm

LOG = logging.getLogger(__name__)


class DistributionInfo:
    """Distribution information"""

    def __init__(
        self,
        distro_id: str = None,
        distro_version_id: str = None,
        distro_name: str = None,
    ):
        """Distribution Information class"""
        _id, _version_id, _name = (None, None, None)
        if not distro_id or not distro_version_id or not distro_name:
            with subprocess.Popen(
                "source /etc/os-release && " 'echo -e -n "$ID\n$VERSION_ID\n$NAME"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                executable="/bin/bash",
                universal_newlines=True,
            ) as proc:
                output = proc.communicate()
                LOG.debug("os-release info: %s", output)
                _id, _version_id, _name = output[0].split("\n")

        self._distro_id = distro_id or _id
        self._distro_version_id = distro_version_id or _version_id
        self._distro_name = distro_name or _name
        self._is_stream = "stream" in self._distro_name.lower()
        self._load_data()

    def _load_data(self):
        for ver_path in constants.RHOS_VERSIONS_SEARCH_PATHS:
            data_path = os.path.join(ver_path, f"{self.distro_id}.yaml")
            if not os.path.exists(data_path):
                LOG.debug("%s does not exist", data_path)
                continue
            LOG.debug("Found distro data in %s", data_path)
            with open(data_path, "r", encoding="utf-8") as data:
                self._distro_data = yaml.safe_load(data.read())
                return
        LOG.error("Unable to find a %s.yaml", self.distro_id)
        raise exceptions.DistroNotSupported(self.distro_id)

    @property
    def distro_data(self):
        return self._distro_data

    @property
    def distro_id(self):
        return self._distro_id

    @property
    def distro_version_id(self):
        return self._distro_version_id

    @property
    def distro_major_version_id(self):
        return self._distro_version_id.split(".")[0]

    @property
    def distro_minor_version_id(self):
        if len(self._distro_version_id.split(".")) < 2:
            # CentOS Stream doesn't have a minor version
            return ""
        return self._distro_version_id.split(".")[1]

    @property
    def is_stream(self):
        return self._is_stream

    @property
    def distro_name(self):
        return self._distro_name

    @property
    def distros(self):
        return self._distro_data.get("distros", {})

    @property
    def versions(self):
        return self._distro_data.get("versions", {})

    @property
    def distro_normalized_id(self):
        ver = [
            self.distro_id,
            self.distro_major_version_id,
        ]
        if self.distro_minor_version_id:
            # handle period before minor version if exists
            ver.append("." + self.distro_minor_version_id)
        if self.is_stream:
            ver.append("-stream")
        return "".join(ver)

    def __str__(self):
        return self.distro_normalized_id

    def validate_distro(self, version) -> bool:
        if version not in self.versions:
            LOG.warning(
                "%s not in defined in release information",
                version,
            )
            return False
        # make sure distro is in the listed distributions
        distros = self.versions[version].get("distros", [])
        if self.distro_normalized_id not in distros:
            LOG.warning(
                "%s not in %s",
                self.distro_normalized_id,
                distros,
            )
            return False
        # make sure subscription manager is at least registered and base os locked
        if "rhel" in self.distro_id:
            submgr = rhsm.SubscriptionManager.instance()
            submgr.status()
            _, out, _ = submgr.release()
            ver = f"{self.distro_major_version_id}.{self.distro_minor_version_id}"
            # The output will be "Release not set" or "Release: X.Y"
            if "not set" in out or f": {ver}" not in out:
                LOG.warning(
                    "System not currently locked to the correct release. "
                    "Please run subscription-manager release --set=%s",
                    ver,
                )
                raise exceptions.SubscriptionManagerConfigError()
        return True

    def get_version(self, version) -> dict:
        if version not in self.versions:
            LOG.error("%s is not available in version list", version)
            raise exceptions.VersionNotSupported(version)
        return self.versions.get(version, {})

    def construct_repo(self, repo_type, version, name):
        # RHEL only supports rhsm
        if "rhel" in self.distro_id:
            return repos.RhsmRepo(name)
        if "centos" in repo_type:
            return repos.TripleoCentosRepo(repo_type, name)
        if "ceph" in repo_type:
            return repos.TripleoCephRepo(self.distro_normalized_id, name)
        if "delorean" in repo_type:
            dlrn_dist = f"{self.distro_id}{self.distro_major_version_id}"
            return repos.TripleoDeloreanRepos(dlrn_dist, version, name)
        raise exceptions.RepositoryNotSupported(repo_type)

    def get_repos(self, version, enable_ceph: bool = False) -> list:
        r = []
        dist = self.distro_normalized_id
        version_data = self.get_version(version)
        if dist not in version_data["repos"]:
            LOG.warning("%s missing from version repos", dist)

        # handle distro specific repos
        for name in version_data["repos"].get(dist, []):
            r.append(self.construct_repo(dist, version, name))

        # handle other software related repos
        for repo in constants.SUPPORTED_REPOS:
            for name in version_data["repos"].get(repo, []):
                if not enable_ceph and "ceph" in name:
                    continue
                r.append(self.construct_repo(repo, version, name))
        return r

    def get_modules(self, version) -> list:
        r = []
        module_data = self.get_version(version).get("modules", {})
        for item in module_data.items():
            r.append(dnf.DnfModule(*item))
        return r
