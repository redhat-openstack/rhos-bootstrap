%global debug_package %{nil}
%{?!released_version: %global released_version 0.0.1}

# ---------------
# rhos-bootstrap
# ---------------

Name:           rhos-bootstrap
Summary:        Red Hat OpenStack bootstrap utility
Version:        %{released_version}
Release:        1%{?dist}

License:        ASL 2.0

URL:            https://github.com/redhat-openstack/rhos-bootstrap
Source:         https://github.com/redhat-openstack/rhos-bootstrap/archive/%{version}.tar.gz#/rhos-bootstrap-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3-pyyaml
Requires:       python3-requests

BuildRequires:  python3-pbr >= 2.0.0
BuildRequires:  python3-pyyaml
Requires:       python3-requests

%{?python_provide:%python_provide python3-%{name}}

%description
Red Hat OpenStack bootstrap utility

# ---------------
# Setup
# ---------------

%prep
%autosetup -n rhos-bootstrap-%{version} -S git
rm -rf *.egg-info

# ---------------
# Build
# ---------------

%build
%{py3_build}

# ---------------
#  Install
# ---------------

%install
%{py3_install}

# ---------------
#  Misc
# ---------------

%check
# TODO(mwhahaha): run tests

%post

%preun

# ---------------
# Files
# ---------------

%files
%license LICENSE
%doc README.rst AUTHORS ChangeLog
%{python3_sitelib}/rhos_bootstrap*
%{_bindir}/%{name}
%{_datadir}/%{name}

# ---------------

%changelog
* Tue Aug 10 2021 Alex Schultz <aschultz@redhat.com> - 0.0.1-1
- Initial Release
