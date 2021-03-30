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


class DistroNotSupported(Exception):
    """Distribution is not supported"""

    def __init__(
        self,
        distro_id: str,
        message: str = "Distribution {} is not currently supported",
    ):
        super().__init__(message.format(distro_id))


class SubscriptionManagerConfigError(Exception):
    """Subscription manager not configured correctly"""

    def __init__(  # pylint: disable=useless-super-delegation
        self,
        message: str = "Red Hat Subscription Manager is not currently configured correctly",
    ):
        super().__init__(message)


class SubscriptionManagerFailure(Exception):
    """Subscription manager failed"""

    def __init__(
        self, cmd_line: str, message: str = "Failed running subscription-manager {}"
    ):
        super().__init__(message.format(cmd_line))


class VersionNotSupported(Exception):
    """Version is not supported"""

    def __init__(
        self, version: str, message: str = "Version {} is not currently supported"
    ):
        super().__init__(message.format(version))


class RepositoryNotSupported(Exception):
    """Unknown repository"""

    def __init__(self, repo: str, message: str = "Repository {} is unknown"):
        super().__init__(message.format(repo))
