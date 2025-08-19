Name:      tuxsuite
Version:   1.44.0
Release:   0%{?dist}
Summary:   TuxSuite, helps with Linux kernel development
License:   Expat
URL:       https://tuxsuite.com
Source0:   %{pypi_source}


BuildRequires: git
BuildRequires: make
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: python3-flit
BuildRequires: python3-pip
BuildRequires: python3-pytest
BuildRequires: python3-pytest-cov
BuildRequires: python3-pytest-mock
BuildRequires: python3-voluptuous
BuildRequires: python3-yaml
BuildRequires: wget
BuildRequires: b4
Requires: b4
Requires: python3 >= 3.6
Requires: python3-attrs
Requires: python3-requests
Requires: python3-voluptuous
Requires: python3-yaml

BuildArch: noarch

%global debug_package %{nil}

%description
TuxSuite, by Linaro, is a suite of tools and services to help with Linux
kernel development. The TuxSuite CLI is the supported interface to TuxBuild
and TuxTest. TuxBuild is an on demand API for building massive quantities of
Linux kernels in parallel. TuxTest is an on demand API for testing Linux
kernels reliably and quickly.

%prep
%setup -q

%build
export FLIT_NO_NETWORK=1
make run
# make man
# make bash_completion

# %check
# python3 -m pytest test/

%install
mkdir -p %{buildroot}/usr/share/tuxsuite/
cp -r run tuxsuite %{buildroot}/usr/share/tuxsuite/
mkdir -p %{buildroot}/usr/bin
ln -sf ../share/tuxsuite/run %{buildroot}/usr/bin/tuxsuite
# mkdir -p %{buildroot}%{_mandir}/man1
# install -m 644 tuxsuite.1 %{buildroot}%{_mandir}/man1/
# mkdir -p %{buildroot}/usr/share/bash-completion/completions/
# install -m 644 bash_completion/tuxsuite %{buildroot}/usr/share/bash-completion/completions/

%files
/usr/share/tuxsuite
%{_bindir}/tuxsuite
# %{_mandir}/man1/tuxsuite.1*
# /usr/share/bash-completion/completions/tuxsuite

%doc README.md
%license LICENSE

%changelog

* Mon Oct 04 2021 Senthil Kumaran <senthil.kumaran@linaro.org> - 0.35.0-1
- Initial version of the package
