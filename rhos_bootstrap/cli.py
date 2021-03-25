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
import logging
import os
import sys

from rhos_bootstrap import distribution
from rhos_bootstrap.utils.dnf import DnfModuleManager

LOG = logging.getLogger(__name__)


class BootstrapCli(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description='Perform basic bootrstrap related functions when '
                        'installing, updating, or upgrading OpenStack on '
                        'Red Hat based systems. This tool can manage '
                        'RPM repository and dnf module configurations. This '
                        'tool can also be used to install tripleoclient and '
                        'perform repository validations for the target '
                        'version')

    @property
    def parser(self):
        return self._parser

    def parse_args(self):
        self.parser.add_argument('version',
                                 help=('The target OpenStack version to '
                                       'configure this system to use when '
                                       'fetching packages.'))
        self.parser.add_argument('--enable-ceph-install',
                                 action='store_true',
                                 default=False,
                                 help=('Perform ceph related configuration '
                                       'actions'))
        self.parser.add_argument('--skip-repos',
                                 action='store_true',
                                 default=False,
                                 help=('Skip repository configuration related '
                                       'actions'))
        self.parser.add_argument('--skip-modules',
                                 action='store_true',
                                 default=False,
                                 help=('Skip module configuration related '
                                       'actions'))
        self.parser.add_argument('--skip-client-install',
                                 action='store_true',
                                 default=False,
                                 help='Skip tripleoclient installation')
        self.parser.add_argument('--skip-validation',
                                 action='store_true',
                                 help='Skip version validation')
        self.parser.add_argument('--update-and-reboot',
                                 action='store_true',
                                 help=('Perform a system update and issue a '
                                       'reboot after configuring the system '
                                       'repositories and modules '
                                       'configuration.'))
        self.parser.add_argument('--debug',
                                 action='store_true',
                                 default=False,
                                 help='Enable debug logging')
        args = self.parser.parse_args()
        return args


def main():
    cli = BootstrapCli()
    args = cli.parse_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=log_level)

    if os.getuid() != 0:
        LOG.error('You must be root to run this command')
        cli.parser.print_help()
        sys.exit(2)

    distro = distribution.DistributionInfo('centos', '8', 'CentOS Stream')
    if not args.skip_repos:
        # TODO(mwhahaha): handle skip ceph
        repos = distro.get_repos(args.version)
        LOG.info("Configuring repositories....")
        for repo in repos:
            LOG.debug(repo.name)
            LOG.info(f"Saving {repo.name}")
            repo.save()
    else:
        LOG.info('Skipping repository configuration...')

    if not args.skip_modules:
        modules = distro.get_modules(args.version)
        LOG.info("Configuring modules....")
        manager = DnfModuleManager()
        for mod in modules:
            LOG.info(f'Enabling {mod.name}:{mod.stream}')
            manager.enable(mod.name, mod.stream, mod.profile)
    else:
        LOG.info('Skipping module configuration...')


if __name__ == '__main__':
    main()
