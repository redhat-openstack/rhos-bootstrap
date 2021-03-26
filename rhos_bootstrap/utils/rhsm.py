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

import shutil
import subprocess


class SubscriptionManager:
    """Subscription manager interactions"""

    def __init__(self):
        self._exe = shutil.which("subscription-manager")
        if not self._exe:
            raise Exception("subscrition-manager not available in PATH")

    @property
    def exe(self):
        return self._exe

    def run(self, args: list):
        cmd = [self.exe] + args
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        rc = proc.returncode

        if rc != 0:
            raise Exception(err)
        return rc, out, err
