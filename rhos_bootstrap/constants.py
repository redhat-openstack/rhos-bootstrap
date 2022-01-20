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

import os
import sys

RHOS_VERSIONS_SEARCH_PATHS = [
    # pkg
    os.path.join("/usr", "share", "rhos-bootstrap"),
    # sudo pip install
    os.path.join("/usr", "local", "share", "rhos-bootstrap"),
    # pip install
    os.path.join(sys.prefix, "share", "rhos-bootstrap"),
    # setup.py build
    os.path.join(sys.prefix, "share", "rhos_bootstrap"),
]

YUM_REPO_BASE_DIR = "/etc/yum.repos.d"

DEFAULT_MIRROR_MAP = {
    "fedora": "https://mirrors.fedoraproject.org",
    "centos": "http://mirror.centos.org",
    "centos8-stream": "http://mirror.centos.org",
    "centos9-stream": "http://mirror.stream.centos.org",
    "ubi": "http://mirror.centos.org",
    "rhel": "https://trunk.rdoproject.org",
    "rdo": "https://trunk.rdoproject.org",
}

CENTOS_RELEASE_MAP = {"centos8-stream": "8-stream", "centos9-stream": "9-stream"}

CENTOS_REPO_MAP = {
    "baseos": "BaseOS",
    "appstream": "AppStream",
    "highavailability": "HighAvailability",
    "nfv": "nfv",
    "powertools": "PowerTools",
    "rt": "RT",
    "virt": "virt",
    "crb": "CRB",
}

# SIG related repo list which is used in path for 9-stream+
CENTOS_SIG_LIST = [
    "extras",
    "hyperscale",
    "infra",
    "kmods",
    "messaging",
    "nfv",
    "storage",
]

SUPPORTED_REPOS = [
    "ansible",
    "ceph",
    "delorean",
    "openstack",
    "openvswitch",
    "satellite",
    "virt",
]
