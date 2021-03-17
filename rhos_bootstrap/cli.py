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
import argparse
import pprint

from rhos_bootstrap import distribution


class BootstrapCli(object):
    def __init__(self):
        pass

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='Perform basic bootrstrap related functions when '
                        'installing, updating, or upgrading OpenStack on '
                        'Red Hat based systems. This tool can manage '
                        'RPM repository and dnf module configurations. This '
                        'tool can also be used to install tripleoclient and '
                        'perform repository validations for the target '
                        'version')

        parser.add_argument('version',
                            help='The target OpenStack version to configure '
                                 'this system to use when fetching packages.')
        parser.add_argument('--enable-ceph-install',
                            action='store_true',
                            default=False,
                            help='Perform ceph related configuration actions')
        parser.add_argument('--skip-repos',
                            action='store_true',
                            default=False,
                            help='Skip repository configuration related '
                                 'actions')
        parser.add_argument('--skip-modules',
                            action='store_true',
                            default=False,
                            help='Skip module configuration related actions')
        parser.add_argument('--skip-client-install',
                            action='store_true',
                            default=False,
                            help='Skip tripleoclient installation')
        parser.add_argument('--skip-validation',
                            action='store_true',
                            help='Skip version validation')
        parser.add_argument('--update-and-reboot',
                            action='store_true',
                            help='Perform a system update and issue a reboot '
                                 'after configuring the system repositories '
                                 'and modules configuration.')
        args = parser.parse_args()
        return args


def main():
    cli = BootstrapCli()
    args = cli.parse_args()
    distro = distribution.DistributionInfo('centos', '8', 'CentOS Stream')
    print(distro)
    pprint.pprint(distro.get_version(args.version))
    repos = distro.get_repos(args.version)
    pprint.pprint(repos)
    for repo in repos:
        print(repo)


if __name__ == '__main__':
    main()
