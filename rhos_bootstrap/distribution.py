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

LOG = logging.getLogger(__name__)


class DistributionInfo:
    """Distribution information"""

    def __init__(self,
                 distro_id: str = None,
                 distro_version_id: str = None,
                 distro_name: str = None):
        """Distribution Information class"""
        _id, _version_id, _name = (None, None, None)
        if not distro_id or not distro_version_id or not distro_name:
            output = subprocess.Popen(
                'source /etc/os-release && '
                'echo -e -n "$ID\n$VERSION_ID\n$NAME"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=open(os.devnull, 'w'),
                executable='/bin/bash',
                universal_newlines=True).communicate()
            _id, _version_id, _name = output[0].split('\n')

        self._distro_id = distro_id or _id
        self._distro_version_id = distro_version_id or _version_id
        self._distro_name = distro_name or _name
        self._is_stream = ('stream' in self._distro_name.lower())
        self._load_data()

    def _load_data(self):
        data_path = os.path.join(constants.RHOS_VERSIONS_DIR,
                                 "{}.yaml".format(self.distro_id))
        if not os.path.exists(data_path):
            LOG.error(f"{data_path} does not exist")
            raise exceptions.DistroNotSupported(self.distro_id)
        with open(data_path, 'r') as data:
            self._distro_data = yaml.safe_load(data.read())

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
        return self._distro_version_id.split('.')[0]

    @property
    def is_stream(self):
        return self._is_stream

    @property
    def distro_name(self):
        return self._distro_name

    @property
    def distros(self):
        return self._distro_data.get('distros', {})

    @property
    def versions(self):
        return self._distro_data.get('versions', {})

    @property
    def distro_normalized_id(self):
        distro = f'{self.distro_id}{self.distro_major_version_id}'
        if self.is_stream:
            distro = distro + '-stream'
        return distro

    def __str__(self):
        return self.distro_normalized_id

    def get_version(self, version) -> dict:
        if version not in self.versions:
            LOG.error(f"{version} is not available in version list")
            raise exceptions.VersionNotSupported(version)
        return self.versions.get(version, {})

    def get_repos(self, version) -> list:
        r = []
        dist = self.distro_normalized_id
        version_data = self.get_version(version)
        if dist not in version_data['repos']:
            LOG.warning(f'{dist} missing from version repos')
        if 'centos' in dist:
            for repo in version_data['repos'].get(dist, []):
                r.append(repos.TripleoCentosRepo(dist, repo))
        if 'ceph' in version_data['repos']:
            for repo in version_data['repos']['ceph']:
                r.append(repos.TripleoCephRepo(dist, repo))
        if 'delorean' in version_data['repos']:
            distro = f'{self.distro_id}{self.distro_major_version_id}'
            for repo in version_data['repos']['delorean']:
                r.append(repos.TripleoDeloreanRepos(distro, version, repo))
        return r

    def get_modules(self, version) -> list:
        r = []
        module_data = self.get_version(version).get('modules', {})
        for mod in module_data.keys():
            r.append(dnf.DnfModule(mod, module_data[mod]))
        return r
