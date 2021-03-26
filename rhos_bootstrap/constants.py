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

# NOTE(mwhahaha): So if we pip install this, we need to also
# honor pulling some other files from a venv. This logic will create a
# constant for a venv share path.
SHARE_BASE_PATH = os.path.join(sys.prefix, "share")
if sys.prefix != "/usr" and not os.path.isdir(SHARE_BASE_PATH):
    SHARE_BASE_PATH = os.path.join("/usr", "share")

RHOS_VERSIONS_DIR = os.path.join(SHARE_BASE_PATH, "rhos-bootstrap")

YUM_REPO_BASE_DIR = "/etc/yum.repos.d"

DEFAULT_MIRROR_MAP = {
    "fedora": "https://mirrors.fedoraproject.org",
    "centos": "http://mirror.centos.org",
    "ubi": "http://mirror.centos.org",
    "rhel": "https://trunk.rdoproject.org",
    "rdo": "https://trunk.rdoproject.org",
}

CENTOS_RELEASE_MAP = {"centos8": "8", "centos8-stream": "8-stream"}

CENTOS_REPO_MAP = {
    "baseos": "BaseOS",
    "appstream": "AppStream",
    "highavailability": "HighAvailability",
    "nfv": "nfv",
    "powertools": "PowerTools",
    "rt": "RT",
    "virt": "virt",
}
