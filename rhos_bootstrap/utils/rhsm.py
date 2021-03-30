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

import logging
import shutil
import subprocess

from rhos_bootstrap.exceptions import SubscriptionManagerConfigError, SubscriptionManagerFailure

LOG = logging.getLogger(__name__)


class SubscriptionManager:
    """Subscription manager interactions"""

    _instance = None
    _exe = None

    def __init__(self):
        raise RuntimeError("Use instance()")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @property
    def exe(self) -> str:
        if not self._exe:
            self._exe = shutil.which("subscription-manager")
            if not self._exe:
                raise Exception("subscrition-manager not available in PATH")
        return self._exe

    def run(self, args: list) -> (int, str, str):
        cmd = [self.exe] + args
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        rc = proc.returncode

        if rc != 0:
            LOG.debug(err)
            raise SubscriptionManagerFailure(" ".join(cmd))
        return rc, out, err

    def status(self):
        try:
            return self.run(["status"])
        except SubscriptionManagerFailure as e:
            raise SubscriptionManagerConfigError from e

    def release(self):
        try:
            return self.run(["release"])
        except SubscriptionManagerFailure as e:
            raise SubscriptionManagerConfigError from e

    def repos(self, enable: list = None, disable: list = None):
        cmd_line = ["repos"]
        if enable:
            cmd_line.append(f"--enable={','.join(enable)}")
        if disable:
            cmd_line.append(f"--disable={','.join(disable)}")
        return self.run(cmd_line)
