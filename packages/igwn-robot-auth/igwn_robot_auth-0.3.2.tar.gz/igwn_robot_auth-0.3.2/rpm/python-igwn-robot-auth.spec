%define srcname igwn-robot-auth
%global distname %{lua:name = string.gsub(rpm.expand("%{srcname}"), "[.-]", "_"); print(name)}
%define version 0.3.2
%define release 1

# -- metadata ---------------

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   Auth credential management for IGWN robots

Source0:   %pypi_source %distname
License:   GPLv3+
Url:       https://git.ligo.org/computing/software/igwn-robot-auth

Packager:  Duncan Macleod <duncan.macleod@ligo.org>
Vendor:    Duncan Macleod <duncan.macleod@ligo.org>

BuildArch: noarch
Prefix:    %{_prefix}

# -- build requirements -----

# build
BuildRequires: python3-devel
BuildRequires: python3dist(pip)
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(wheel)

# man pages
BuildRequires: python3dist(argparse-manpage)
BuildRequires: python3dist(igwn-auth-utils) >= 1.3.0

# tests
BuildRequires: python3dist(htcondor)
BuildRequires: python3dist(pytest)

# -- packages ------------------------

# src.rpm
%description
This project provides utilities for managing IGWN authorisation credentials
associated with Robot identities (shared accounts, automated processes, etc).

%package -n python3-%{srcname}
Summary: Python %{python3_version} library for IGWN Robot Auth
# make igwn-auth-utils optional requirements explicit for us, Python extras
# metadata doesn't seem to work with current igwn-auth-utils release on EL9
Requires: python3dist(gssapi)
Requires: python3dist(htgettoken)
%description -n python3-%{srcname}
Utilities for managing authentication and authorisation for
IGWN unattended (robot) processes.
This package provides the Python 3 library.
%files -n python3-%{srcname}
%doc README.md
%license LICENSE
%{python3_sitelib}/*

%package -n igwn-robot-auth
Summary: Command line utilities for IGWN Robot Auth
Requires: python3-%{srcname} = %{version}-%{release}
%description -n igwn-robot-auth
Utilities for managing authentication and authorisation for
IGWN unattended (robot) processes.
This package provides the command-line tools.
%files -n igwn-robot-auth
%doc README.md
%license LICENSE
%{_bindir}/*
%{_mandir}/man1/*.1*

# -- build ---------------------------

%prep
%autosetup -n %{distname}-%{version}

# if running Python 3.6, apply the patch bundled with the source
%if 0%{?rhel} && 0%{?rhel} < 9
%__patch -p1 -i rpm/0001-Reverse-engineer-support-for-Python-3.6.patch
%endif

# for RHEL < 10 hack together setup.{cfg,py} for old setuptools
%if 0%{?rhel} && 0%{?rhel} < 10
cat > setup.cfg << SETUP_CFG
[metadata]
name = %{srcname}
version = %{version}
author-email = %{packager}
description = %{summary}
license = %{license}
license_files = LICENSE
url = %{url}
[options]
packages = find:
python_requires = >=%{python3_version}
install_requires =
  htcondor
  igwn-auth-utils >=1.3.0
[options.entry_points]
console_scripts =
  igwn-robot-get = igwn_robot_auth.tools.get:main
[build_manpages]
manpages =
  man/igwn-robot-get.1:function=create_parser:module=igwn_robot_auth.tools.get
SETUP_CFG
%endif
%if %{undefined pyproject_wheel}
cat > setup.py << SETUP_PY
from setuptools import setup
setup()
SETUP_PY
%endif

%build
%if %{defined pyproject_wheel}
%pyproject_wheel
%else
%py3_build_wheel
%endif
# generate manuals
%python3 -c "from setuptools import setup; setup()" \
  --command-packages=build_manpages \
  build_manpages \
;

%install
%if %{defined pyproject_install}
%pyproject_install
%else
%py3_install_wheel *.whl
%endif
%__mkdir -p -v %{buildroot}%{_mandir}/man1
%__install -m 644 -p -v man/*.1* %{buildroot}%{_mandir}/man1/

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
export PATH="%{buildroot}%{_bindir}:${PATH}"
igwn-robot-get --help
%pytest --verbose -ra --pyargs igwn_robot_auth.tests

# -- changelog -----------------------

%changelog
* Sun Aug 17 2025 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.2-1
- Update to 0.3.2

* Sat Aug 16 2025 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.1-1
- Update to 0.3.1

* Sat Aug 16 2025 Duncan Macleod <duncan.macleod@ligo.org> - 0.3.0-1
- Update to 0.3.0
- Add Requires on gssapi and htgettoken

* Wed Apr 30 2025 Duncan Macleod <duncan.macleod@ligo.org> - 0.2.0-1
- Update to 0.2.0

* Wed Apr 02 2025 Duncan Macleod <duncan.macleod@ligo.org> - 0.1.0-1
- First release
