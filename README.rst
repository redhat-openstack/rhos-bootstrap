rhos-bootstrap
==============

|CI Status|

.. |CI Status| image:: https://github.com/mwhahaha/rhos-bootstrap/actions/workflows/py-tox.yml/badge.svg
   :target: https://github.com/mwhahaha/rhos-bootstrap/actions

A bootstrap tool used to handle repository, dnf module configuration, and
tripleoclient installation in preparation for a Red Hat OpenStack installation.

Usage
~~~~~

::

    usage: rhos-bootstrap [-h] [--skip-validation] [--skip-repos]
                          [--skip-ceph-install] [--skip-modules]
                          [--update-packages] [--skip-client-install] [--debug]
                          version

    Perform basic bootstrap related functions when installing, updating, or
    upgrading OpenStack on Red Hat based systems. This tool can manage RPM
    repository and dnf module configurations. This tool can also be used to
    install tripleoclient and perform repository validations for the target
    version

    positional arguments:
      version               The target OpenStack version to configure this system
                            to use when fetching packages.

    optional arguments:
      -h, --help            show this help message and exit
      --skip-validation     Skip version validation
      --skip-repos          Skip repository configuration related actions
      --skip-ceph-install   Skip ceph related configuration actions
      --skip-modules        Skip module configuration related actions
      --update-packages     Perform a system update after configuring the system
                            repositories and modules configuration.
      --skip-client-install
                            Skip tripleoclient installation
      --debug               Enable debug logging
