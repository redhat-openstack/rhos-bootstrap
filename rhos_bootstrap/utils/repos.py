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
import requests

from rhos_bootstrap.utils.rhsm import SubscriptionManager
from rhos_bootstrap.constants import DEFAULT_MIRROR_MAP
from rhos_bootstrap.constants import CENTOS_RELEASE_MAP
from rhos_bootstrap.constants import CENTOS_REPO_MAP
from rhos_bootstrap.constants import CENTOS_SIG_LIST
from rhos_bootstrap.constants import YUM_REPO_BASE_DIR
from rhos_bootstrap.exceptions import DistroNotSupported, RepositoryNotSupported


class RhsmRepo:  # pylint: disable=too-few-public-methods
    """Base repo object for rhsm"""

    def __init__(self, name: str):
        self._name = name
        self._rhsm = SubscriptionManager.instance()

    @property
    def name(self):
        return self._name

    def save(self):
        self._rhsm.repos(enable=[self._name])


class BaseYumRepo:  # pylint: disable=too-many-instance-attributes
    """Base repo object for yum"""

    def __init__(
        self,
        name: str,
        description: str,
        baseurl: str,
        enabled: bool,
        gpgcheck: bool,
        mirrorlist: str = None,
        metalink: str = None,
        gpgkey: str = None,
    ) -> None:
        self._name = name
        self._description = description
        self._baseurl = baseurl
        self.enabled = enabled
        self.gpgcheck = gpgcheck
        self._mirrorlist = mirrorlist
        self._metalink = metalink
        self._gpgkey = gpgkey

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def baseurl(self):
        return self._baseurl

    @property
    def enabled(self):
        return self._enabled == 1

    @enabled.setter
    def enabled(self, enabled_setting: bool):
        if enabled_setting:
            self._enabled = 1
        else:
            self._enabled = 0

    @property
    def gpgcheck(self):
        return self._gpgcheck == 1

    @gpgcheck.setter
    def gpgcheck(self, gpgcheck_setting):
        if gpgcheck_setting:
            self._gpgcheck = 1
        else:
            self._gpgcheck = 0

    @property
    def mirrorlist(self):
        return self._mirrorlist

    @property
    def metalink(self):
        return self._metalink

    @property
    def gpgkey(self):
        return self._gpgkey

    def __str__(self) -> str:
        repo = [
            f"[{self.name}]",
            f"name={self.description}",
        ]
        if self.baseurl:
            repo.append(f"baseurl={self.baseurl}")
        if self.mirrorlist:
            repo.append(f"mirrorlist={self.mirrorlist}")
        if self.metalink:
            repo.append(f"metalink={self.metalink}")
        repo.append(f"enabled={self._enabled}")
        repo.append(f"gpgcheck={self._gpgcheck}")
        if self.gpgkey:
            repo.append(f"gpgkey={self.gpgkey}")
        repo.append("")
        return "\n".join(repo)

    def save(self, repo_dir: str = YUM_REPO_BASE_DIR):
        repo_path = os.path.join(repo_dir, f"{self.name}.repo")
        if not os.path.isdir(repo_dir):
            raise FileNotFoundError(f"{repo_dir} does not exist")
        if not os.access(repo_dir, os.W_OK):
            raise PermissionError(f"{repo_dir} is not writable")
        if os.path.isfile(repo_path) and not os.access(repo_path, os.W_OK):
            raise PermissionError(f"{repo_path} is not writable")
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(str(self))


class TripleoCephRepo(BaseYumRepo):
    """Upstream Ceph Repo"""

    def __init__(
        self, centos_release: str, ceph_release: str, mirror: str = None
    ) -> None:
        if centos_release not in CENTOS_RELEASE_MAP:
            raise DistroNotSupported(centos_release)
        if mirror is None:
            mirror = DEFAULT_MIRROR_MAP[centos_release]
        centos_short_release = CENTOS_RELEASE_MAP[centos_release]
        if centos_short_release == "8-stream":
            path_base = "centos/"
        else:
            # 9-stream storage is in the SIGs path
            path_base = "SIGs/"
        super().__init__(
            f"tripleo-centos-ceph-{ceph_release}",
            f"tripleo-centos-ceph-{ceph_release}",
            (
                f"{mirror}/{path_base}{centos_short_release}/"
                f"storage/$basearch/ceph-{ceph_release}/"
            ),
            True,
            False,
        )


class TripleoCentosRepo(BaseYumRepo):
    """Upstream CentOS Repo"""

    def __init__(self, centos_release: str, repo: str, mirror: str = None) -> None:
        if repo not in CENTOS_REPO_MAP:
            raise RepositoryNotSupported(repo)
        if mirror is None:
            mirror = DEFAULT_MIRROR_MAP[centos_release]
        centos_short_release = CENTOS_RELEASE_MAP[centos_release]
        if centos_short_release == "8-stream":
            # 8-stream has repos in centos base
            path_base = "centos/"
        else:
            path_base = ""
            # 9-stream+ has some repos in SIGs
            if repo in CENTOS_SIG_LIST:
                path_base = "SIGs/"
        super().__init__(
            f"tripleo-centos-{repo}",
            f"tripleo-centos-{repo}",
            (
                f"{mirror}/{path_base}{centos_short_release}/"
                f"{CENTOS_REPO_MAP[repo]}/$basearch/os/"
            ),
            True,
            False,
        )


class TripleoDeloreanRepos:
    """Upstream RDO Repo"""

    def __init__(
        self,
        distro: str,
        version: str,
        repo: str,
        mirror: str = DEFAULT_MIRROR_MAP["rdo"],
    ) -> None:
        self._base_uri = f"{mirror}/{distro}-{version}"
        if repo == "deps":
            uri = f"{self._base_uri}/delorean-deps.repo"
        else:
            uri = f"{self._base_uri}/{repo}/delorean.repo"
        self._name = f"tripleo-delorean-{repo}"
        self._repo_data = self._get_repo(uri)

    @property
    def name(self) -> str:
        return self._name

    @property
    def repo_data(self) -> str:
        return self._repo_data

    def _get_repo(self, uri) -> str:
        r = requests.get(uri)
        r.raise_for_status()
        # NOTE(mwhahaha): May want to inject mirror here
        return r.text

    def __str__(self) -> str:
        return self.repo_data

    def save(self, repo_dir: str = YUM_REPO_BASE_DIR):
        repo_path = os.path.join(repo_dir, f"{self.name}.repo")
        if not os.path.isdir(repo_dir):
            raise FileNotFoundError(f"{repo_dir} does not exist")
        if not os.access(repo_dir, os.W_OK):
            raise PermissionError(f"{repo_dir} is not writable")
        if os.path.isfile(repo_path) and not os.access(repo_path, os.W_OK):
            raise PermissionError(f"{repo_path} is not writable")
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(str(self))
