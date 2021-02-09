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

import dnf
import libdnf
import logging
import yaml

LOG = logging.getLogger(__name__)

STATE_DEFAULT = libdnf.module.ModulePackageContainer.ModuleState_DEFAULT
STATE_ENABLED = libdnf.module.ModulePackageContainer.ModuleState_ENABLED
STATE_DISABLED = libdnf.module.ModulePackageContainer.ModuleState_DISABLED
STATE_UNKNOWN = libdnf.module.ModulePackageContainer.ModuleState_UNKNOWN


class DnfModules(object):
    def __init__(self):
        self.dnf_base = dnf.Base()
        self.dnf_base.read_all_repos()
        self.dnf_base.fill_sack()
        self.module_base = dnf.module.module_base.ModuleBase(self.dnf_base)
        self.all_modules = []
        self.enabled_modules = {}
        self.default_modules = {}
        self.disabled_modules = {}
        self.unknown_modules = {}
        self._update_modules()

    def _build_module_string(self, name, stream=None, profile=None):
        val = name
        if stream:
            val = '%s:%s' % (val, stream)
        if profile:
            val = '%s/%s' % (val, profile)
        LOG.debug('module string: %s' % val)
        return val

    def _update_modules(self):
        self.dnf_base.reset(sack=True)
        self.dnf_base.fill_sack()
        mods = self.get_all_modules()
        self.all_modules = mods
        self.enabled_modules = {}
        self.default_modules = {}
        self.disabled_modules = {}
        self.unknown_modules = {}
        for mod in mods:
            name = mod['name']
            state = mod['state']
            if state == STATE_ENABLED:
                self.enabled_modules[name] = mod
            elif state == STATE_DEFAULT:
                self.default_modules[name] = mod
            elif state == STATE_DISABLED:
                self.disabled_modules[name] = mod
            elif state == STATE_UNKNOWN:
                self.unknown_modules[name] = mod

    def _commit(self):
        LOG.debug('committing changes')
        try:
            self.dnf_base.do_transaction()
        except RuntimeError:
            LOG.error('Runtime error, please run as root')
            raise
        self._update_modules()

    def get_all_modules(self):
        # returns a list of libdnf.module.ModulePackage. See docs
        # https://dnf.readthedocs.io/en/latest/api_module.html
        all_modules = []
        modules = self.dnf_base._moduleContainer.getModulePackages()
        for mod in modules:
            # get the modulemd represntation of a module
            modmd = yaml.safe_load(mod.getYaml())
            data = modmd['data']
            name = data['name']
            # can be string or float
            stream = str(data['stream'])
            active_stream = self.dnf_base._moduleContainer.\
                getEnabledStream(name)
            state = self.dnf_base._moduleContainer.getModuleState(name)
            # check to see if the stream is active, if not it's 'disabled'
            if (state == STATE_ENABLED and stream not in active_stream):
                state = STATE_DISABLED
            profiles = data['profiles'] if 'profiles' in data else {}
            all_modules.append({
                'name': name,
                'stream': stream,
                'profiles': profiles,
                'state': state
            })
        return all_modules

    def disable(self, name, stream=None, profile=None):
        if name not in self.enabled_modules:
            LOG.debug('missing from enabled_modules')
            return

        if (name in self.disabled_modules and stream
                and stream in self.disabled_modules[name]['stream']):
            LOG.debug('Already in disabled_modules')
            return

        if stream and stream not in self.enabled_modules[name]['stream']:
            LOG.debug('stream not enabled_modules')
            return

        if profile and profile not in self.enabled_modules[name]['profiles']:
            LOG.debug('profile not in enabled_modules')
            return

        LOG.debug('calling disable')
        self.module_base.disable([self._build_module_string(name, stream,
                                                            profile)])
        self._commit()

    def enable(self, name, stream=None, profile=None):
        if name in self.enabled_modules:
            if stream and stream in self.enabled_modules[name]['stream']:
                # already enabled, noop
                LOG.debug('already enabled')
                return
            self.disable(name, self.enabled_modules[name]['stream'])

        LOG.debug('calling enable')
        self.module_base.enable([self._build_module_string(name, stream,
                                                           profile)])
        self._commit()

    def reset(self, name, stream=None, profile=None):
        LOG.debug('calling reset')
        self.module_base.reset([self._build_module_string(name, stream,
                                                          profile)])
        self._commit()

    def install(self, name, stream=None, profile=None):
        if name in self.enabled_modules:
            if stream and stream in self.enabled_modules[name]['stream']:
                # already enabled, noop
                LOG.debug('already installed')
                return
            self.reset(name, self.enabled_modules[name]['stream'])

        LOG.debug('calling install')
        self.module_base.install([self._build_module_string(name, stream,
                                                            profile)], True)
        self._commit()
