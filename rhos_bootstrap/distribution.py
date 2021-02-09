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

import os
import subprocess
import yaml

from rhos_bootstrap import constants


class DistributionInfo:
    """Distribution information"""

    def __init__(self, distro_id=None, distro_version_id=None,
                 distro_name=None):
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

        self.distro_id = distro_id or _id
        self.distro_version_id = distro_version_id or _version_id
        self.distro_name = distro_name or _name
        self._load_data()

    def _load_data(self):
        data_path = os.path.join(constants.RHOS_VERSIONS_DIR,
                                 "{}.yaml".format(self.distro_id))
        if not os.path.exists(data_path):
            raise Exception('Unable to load distribution information from '
                            '{}'.format(data_path))
        with open(data_path, 'r') as data:
            self.distro_data = yaml.safe_load(data.read())

    def get_distros(self):
        return self.distro_data.get('distros', {})

    def get_versions(self):
        return self.distro_data.get('versions', {})

    def get_version(self, version):
        if version not in self.get_versions():
            raise Exception('Version {} not defined in distribution '
                            'data'.format(version))
        return self.get_versions().get(version, {})
