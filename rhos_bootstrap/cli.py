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
import logging.config
import os
import sys

from . import distribution
from .exceptions import DistroNotSupported
from .utils.dnf import DnfManager
from .utils.rhsm import SubscriptionManager

LOG = logging.getLogger(__name__)
LOG_FORMAT = "[%(asctime)s] [%(levelname)s]: %(message)s"
LOG_FILE = "/var/log/rhos-bootstrap.log"


class BootstrapCli:
    """Bootstrap cli action"""

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description="Perform basic bootstrap related functions when "
            "installing, updating, or upgrading OpenStack on "
            "Red Hat based systems. This tool can manage "
            "RPM repository and dnf module configurations. This "
            "tool can also be used to install tripleoclient and "
            "perform repository validations for the target "
            "version"
        )

    @property
    def parser(self):
        return self._parser

    def parse_args(self):
        self.parser.add_argument(
            "version",
            help=(
                "The target OpenStack version to "
                "configure this system to use when "
                "fetching packages."
            ),
        )
        self.parser.add_argument(
            "--skip-validation", action="store_true", help="Skip version validation"
        )
        self.parser.add_argument(
            "--skip-repos",
            action="store_true",
            default=False,
            help=("Skip repository configuration related " "actions"),
        )
        self.parser.add_argument(
            "--skip-ceph-install",
            action="store_true",
            default=False,
            help=("Skip ceph related configuration " "actions"),
        )
        self.parser.add_argument(
            "--skip-modules",
            action="store_true",
            default=False,
            help=("Skip module configuration related " "actions"),
        )
        self.parser.add_argument(
            "--update-packages",
            action="store_true",
            default=False,
            help=(
                "Perform a system update after configuring the system "
                "repositories and modules configuration."
            ),
        )
        self.parser.add_argument(
            "--skip-client-install",
            action="store_true",
            default=False,
            help="Skip tripleoclient installation",
        )
        self.parser.add_argument(
            "--debug", action="store_true", default=False, help="Enable debug logging"
        )
        self.parser.add_argument(
            "--skip-log-file",
            action="store_false",
            default=True,
            help=f"Disable logging to {LOG_FILE}",
        )

        args = self.parser.parse_args()
        return args

    def configure_logger(self, log_file=True, debug=False):
        log_level = logging.INFO
        if debug:
            log_level = logging.DEBUG
        conf = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": LOG_FORMAT}},
            "handlers": {
                "default": {
                    "level": log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
                "log_file": {
                    "level": log_level,
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "standard",
                    "filename": LOG_FILE,
                    "maxBytes": 10485760,
                    "backupCount": 7,
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": log_level,
                    "proagate": True,
                }
            },
        }
        if log_file:
            conf["loggers"][""]["handlers"] = ["default", "log_file"]
        logging.config.dictConfig(conf)


def main():  # pylint: disable=too-many-branches,too-many-statements
    cli = BootstrapCli()
    args = cli.parse_args()
    cli.configure_logger(log_file=args.skip_log_file, debug=args.debug)

    if os.getuid() != 0:
        LOG.error("You must be root to run this command")
        cli.parser.print_help()
        sys.exit(2)

    LOG.info("=" * 40)
    LOG.info("=== OpenStack Version: %s", args.version)
    distro = distribution.DistributionInfo()
    LOG.info("=== Distribution: %s", distro.distro_normalized_id)
    LOG.info("=" * 40)
    if not args.skip_validation:
        LOG.info("=== Validating version for distro...")
        if not distro.validate_distro(args.version):
            raise DistroNotSupported(distro.distro_normalized_id)
        LOG.info("OK! %s on %s", args.version, distro.distro_normalized_id)
    else:
        LOG.info("=== Skipping validation of version for distro...")

    if not args.skip_repos:
        repos = distro.get_repos(args.version, enable_ceph=not args.skip_ceph_install)
        LOG.info("=== Configuring repositories...")

        if "rhel" in distro.distro_id:
            LOG.info("Disabling all existing configured repositories...")
            rhsm = SubscriptionManager.instance()
            rhsm.repos(disable=["*"])

        for repo in repos:
            LOG.info("Configuring %s", repo.name)
            repo.save()
    else:
        LOG.info("=== Skipping repository configuration...")

    if not (
        args.skip_modules and not args.update_packages and args.skip_client_install
    ):
        LOG.info("=== Configuring dnf...")
        # we don't need a manager if we're not calling it
        manager = DnfManager.instance()
    else:
        LOG.info("=== Skipping dnf configuration...")

    if not args.skip_modules:
        modules = distro.get_modules(args.version)
        LOG.info("=== Configuring modules...")
        for mod in modules:
            LOG.info("Enabling %s:%s", mod.name, mod.stream)
            manager.enable_module(mod.name, mod.stream, mod.profile)
    else:
        LOG.info("=== Skipping module configuration...")

    if args.update_packages:
        LOG.info("=== Performing update...")
        manager.update_package("*")
        LOG.info("NOTE: A manual reboot may be required")

    if not args.skip_client_install:
        LOG.info("=== Installing tripleoclient...")
        manager.install_update_package("python3-tripleoclient")
    else:
        LOG.info("=== Skipping tripleoclient installation...")
    LOG.info("=== Done!")


if __name__ == "__main__":
    main()
