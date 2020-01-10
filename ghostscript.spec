#
# Important notes regarding the package:
# ======================================
# 1) This package has GUI versions (*-x11, *-gtk), but we are not shipping the
#    desktop files, because the GUI versions are used for displaying of files
#    invoked from command line. The displaying GUI does not contain any buttons
#    or other means for user interaction. It can't even open a different file
#    from the GUI version. Therefore it does not make sense to ship desktop
#    files...

# === GLOBAL MACROS ===========================================================

# According to Fedora Package Guidelines, it is advised that packages that can
# process untrusted input are build with position-independent code (PIC).
#
# Koji should override the compilation flags and add the -fPIC or -fPIE flags by
# default. This is here just in case this wouldn't happen for some reason.
# For more info: https://fedoraproject.org/wiki/Packaging:Guidelines#PIE
%global _hardened_build 1

# By redefining the '_docdir_fmt' macro we override the default location of
# documentation or license files. Instead of them being located in 'libgs'
# folder, they are now located in 'ghostscript'.
%global _docdir_fmt     %{name}

# NOTE: Artifex is using Github only as a mirror for providing the source
#       tarballs, and their release tags/branches do not use the dot in version
#       tag. This makes obtaining the current version harder, and might prevent
#       automatic builds of new releases...
%global version_short   %(echo "%{version}" | tr -d '.')

# =============================================================================

Name:             ghostscript
Summary:          Interpreter for PostScript language & PDF
Version:          9.25
Release:          2%{?dist}

License:          AGPLv3+

URL:              https://ghostscript.com/
Source0:          https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs%{version_short}/ghostscript-%{version}.tar.xz
Source1:          ghostscript-cups-9.07.tar.xz

# NOTE: We're not explicitly requiring 'dvips' utility needed for 'dvipdf'
#       script, because it would pull a lot of 'texlive-*' to user as a result.
#
#       If user needs to use 'dvipdf', then they will need to install the
Requires:         libgs%{?_isa} = %{version}-%{release}

# Auxiliary build requirements:
BuildRequires:    autoconf
BuildRequires:    automake
BuildRequires:    libtool
BuildRequires:    gcc
BuildRequires:    git

# Already packaged Resources -- needed to build package correctly:
BuildRequires:    adobe-mappings-cmap-devel
BuildRequires:    adobe-mappings-pdf-devel
BuildRequires:    urw-base35-fonts-devel

# Already packaged software -- needed for debundling of Ghostscript:
BuildRequires:    cups-devel
BuildRequires:    dbus-devel
BuildRequires:    fontconfig-devel
BuildRequires:    freetype-devel
BuildRequires:    lcms2-devel
BuildRequires:    libidn-devel
BuildRequires:    libjpeg-turbo-devel
BuildRequires:    libpng-devel
BuildRequires:    libpaper-devel
BuildRequires:    libtiff-devel
BuildRequires:    openjpeg2-devel
BuildRequires:    zlib-devel

# Enabling the GUI possibilities of Ghostscript:
BuildRequires:    gtk3-devel
BuildRequires:    libXt-devel

# =============================================================================

# NOTE: 'autosetup' macro (below) uses 'git' for applying the patches:
#       ->> All the patches should be provided in 'git format-patch' format.
#       ->> Auxiliary repository will be created during 'fedpkg prep', you
#           can see all the applied patches there via 'git log'.

# Upstream patches -- official upstream patches released by upstream since the
# ----------------    last rebase that are necessary for any reason:
#Patch000: example000.patch
Patch000: ghostscript-cve-2018-19409.patch
Patch001: ghostscript-cve-2018-18073.patch
Patch002: ghostscript-cve-2018-17961.patch
Patch003: ghostscript-cve-2018-18284.patch
Patch004: ghostscript-cve-2018-19134.patch
Patch005: ghostscript-cve-2018-19475.patch
Patch006: ghostscript-cve-2018-19476.patch
Patch007: ghostscript-cve-2018-19477.patch
Patch008: ghostscript-cve-2019-6116.patch
Patch009: ghostscript-cve-2019-6116-downstream.patch
Patch010: ghostscript-cve-2019-3839.patch
Patch011: ghostscript-cve-2019-3835.patch
Patch012: ghostscript-cve-2019-3838.patch
Patch013: ghostscript-fix-DSC-comment-parsing.patch
Patch014: ghostscript-pdf2dsc-regression.patch

# Downstream patches -- these should be always included when doing rebase:
# ------------------
Patch100: ghostscript-9.23-100-run-dvipdf-securely.patch
Patch101: ghostscript-9.25-101-reenable-cups-filters.patch


# Downstream patches for RHEL -- patches that we keep only in RHEL for various
# ---------------------------    reasons, but are not enabled in Fedora:
%if %{defined rhel} || %{defined centos}
#Patch200: example200.patch
%endif


# Patches to be removed -- deprecated functionality which shall be removed at
# ---------------------    some point in the future:


%description
This package provides useful conversion utilities based on Ghostscript software,
for converting PS, PDF and other document formats between each other.

Ghostscript is a suite of software providing an interpreter for Adobe Systems'
PostScript (PS) and Portable Document Format (PDF) page description languages.
Its primary purpose includes displaying (rasterization & rendering) and printing
of document pages, as well as conversions between different document formats.

# === SUBPACKAGES =============================================================

# Below requirements are resources, which are not detected by RPM automatically:
%package -n libgs
Summary:          Library providing Ghostcript's core functionality
Requires:         adobe-mappings-cmap
Requires:         adobe-mappings-cmap-deprecated
Requires:         adobe-mappings-pdf
Requires:         urw-base35-fonts

# NOTE: Keeping this here for RHEL-7 to avoid possilible regressions:
#
# Upstream is not versioning the SONAME correctly, thus the rpmbuild is unable
# to recognize we need a newer version of lcms2. This 'hackish' workaround
# will make ghostscript to require at least the version we are built with. (bug #1436273)
%global lcms2_version %(pkg-config --modversion lcms2 2>/dev/null || echo 0)
Requires:         lcms2 >= %{lcms2_version}

%description -n libgs
This library provides Ghostscript's core functionality, based on Ghostscript's
API, which is useful for many packages that are build on top of Ghostscript.

# ---------------

%package -n libgs-devel
Summary:          Development files for Ghostscript's library
Requires:         libgs%{?_isa} = %{version}-%{release}

# This virtual provides is useful in case people get confused what *-devel
# subpackage they should actually use (i.e. ghostscript-devel vss libgs-devel?).
# By having this virtual provide both of the options above will work...
Provides:         %{name}-devel         = %{version}-%{release}
Provides:         %{name}-devel%{?_isa} = %{version}-%{release}
Obsoletes:        %{name}-devel < 9.07-32

%description -n libgs-devel
This package contains development files that are useful for building packages
against Ghostscript's library, which provides Ghostscript's core functionality.

# ---------------

%package gtk
Summary:          Ghostscript's GTK-based document renderer
Requires:         libgs%{?_isa} = %{version}-%{release}

%description gtk
This package provides GTK-based utility 'gsx', which can be used for displaying
of various document files (including PS and PDF).

# ---------------

%package cups
Summary:          CUPS filter for interpreting PostScript and PDF
Requires:         %{name} = %{version}-%{release}
Requires:         libgs%{?_isa} = %{version}-%{release}
Requires:         cups

%description cups
CUPS filter and conversion rules for interpreting PostScript and PDF.

# ---------------

%package doc
Summary:          Documentation files for Ghostscript
Requires:         %{name} = %{version}-%{release}
BuildArch:        noarch

%description doc
This package provides detailed documentation files for Ghostscript software.

# === BUILD INSTRUCTIONS ======================================================

# Call the 'autosetup' macro to prepare the environment, but do not patch the
# source code yet -- we need to remove bundled software before the build first:
%prep
%autosetup -N -S git

# Libraries that we already have packaged in Fedora (see Build Requirements):
rm -rf cups/libs freetype jpeg lcms2* libpng openjpeg tiff windows zlib

# We need to extract additional sources for the ghostscript-cups supbackage.
# These sources are already patched - taken from RHEL-7.6 branch:
tar -xf %{SOURCE1}

# Add the remaining source code to the initial commit, patch the source code:
git add --all --force .
git commit --all --amend --no-edit > /dev/null
%autopatch -p1

# ---------------

%build
# NOTE: The ghostscript-9.25-101-fix-for-cups-filters.patch updates the
#       configure.ac, so we need to keep this here permanently...
autoreconf -fv

# --enable-dynamic
#     ... enables dynamically loaded drivers
#
# --disable-compile-inits
#     ... disables compiling of init files (PS code, fonts, etc.) into resulting
#         binaries, so they are loaded dynamically
#
# --without-versioned-path
#     ... tells configure to not use version string in the resulting paths after
#         'make_install' macro - this is safe, because only one version of
#         package can be installed at a given time on Fedora distribution,
#         so we won't end up with conflicting folders when doing rebase
#
# --with-fonthpath
#     ... searches for necessary fonts in these column-separated directories,
#         not just default ones
#
# --with-install-cups
#     ... needed to correctly install CUPS filters
#
# NOTE:   In RHEL we need to keep the /usr/share/ghostscript/conf.d/ folder
#         for China's GB18030 official certification:
%configure --enable-dynamic --disable-compile-inits --without-versioned-path \
           --with-fontpath="%{urw_base35_fontpath}:%{_datadir}/%{name}/conf.d/:%{_sysconfdir}/%{name}/" \
           --with-install-cups --with-ijs

# Build IJS
cd ijs
autoreconf -ifv
%configure --disable-static --enable-shared
make
cd ..

# NOTE: In RHEL-7, we need to ship ghostscript-cups (filters). In RHEL-8 the
#       filters are provided by cups-filters package.
%make_build
%make_build cups

%make_build so

# ---------------

%install
# Before we run 'soinstall' target, we need to run 'install' first. Without it,
# the CUPS filters would not get installed into buildroot...
make DESTDIR=%{buildroot} install

# Using the 'make_install' macro with 'soinstall' target would result in some
# files being installed unnecessary, so we are using traditional way:
make DESTDIR=%{buildroot} soinstall

cd ijs
make DESTDIR=%{buildroot} install
cd ..

# Don't ship libtool la files.
rm -f %{buildroot}%{_libdir}/libijs.la

# Don't ship ijs example client or server
rm -f %{buildroot}%{_bindir}/ijs_{client,server}_example

# NOTE: In RHEL-8, we have dropped the LPR scripts, since they should not be
#       needed anymore. However, for RHEL-7 we have to keep them.

# Rename the dynamic binary to be used by default as 'gs' binary.
mv -f %{buildroot}%{_bindir}/{gsc,gs}

# Remove useless files from doc/ directory and doc/ symlink:
rm -f %{buildroot}%{_docdir}/%{name}/{AUTHORS,COPYING,*.tex,*.hlp,*.txt}
rm -f %{buildroot}%{_datadir}/%{name}/doc

# ---------------

# Move html documentation into html/ subdir:
install -m 0755 -d %{buildroot}%{_docdir}/%{name}/html
mv -f %{buildroot}%{_docdir}/%{name}/{*.htm*,*.el,html}

# ---------------

# Create 'ghostscript' symlink for its binary:
ln -s %{_bindir}/gs %{buildroot}%{_bindir}/ghostscript

# Create a man page symlink for 'ghostscript':
ln -s %{_mandir}/man1/gs.1 %{buildroot}%{_mandir}/man1/ghostscript.1

# ---------------

# According to upstream, using fontconfig for fonts lookup is quite a slow
# process for Ghostscript startup, and they advise using the symlinks where
# possible. The fontconfig (Ghostscript's search path) should be used preferably
# as a fallback only.

# NOTE: We're bundling the Google Droid Sans Fallback font into libgs to avoid
#       adding Google Droid Fonts package into RHEL, just because of one font.

for font in $(basename --multiple %{buildroot}%{_datadir}/%{name}/Resource/Font/*); do
  ln -fs %{urw_base35_fontpath}/${font}.t1 %{buildroot}%{_datadir}/%{name}/Resource/Font/${font}
done

# Using the system-wide available CMap files from Adobe via Ghostscript's search
# path is not safe (nor was ever intended to be supported) way of doing so
# according to upstream. Their preferred solution is to just create symlink for
# each of the CMap files in Ghostscript's Resources/CMap folder.
for file in $(basename --multiple %{buildroot}%{_datadir}/%{name}/Resource/CMap/*); do
  find %{adobe_mappings_rootpath} -type f -name ${file} -exec ln -fs {} %{buildroot}%{_datadir}/%{name}/Resource/CMap/${file} \;
done


# NOTE: In RHEL-7/8 we have to keep this configuration folder to support
#       Chineese font certification (see above %%build section above):
install -m 0755 -d %{buildroot}%{_datadir}/%{name}/conf.d/

# NOTE: For RHEL-7 (but not for RHEL-8̈́) we also have to support this folder:
install -m 0755 -d %{buildroot}%{_sysconfdir}/%{name}/

# === INSTALLATION INSTRUCTIONS ===============================================

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

# === PACKAGING INSTRUCTIONS ==================================================

%files -n libgs
%license LICENSE doc/COPYING

%{_libdir}/libgs.so.*
%{_libdir}/libijs-*.so*
%{_datadir}/%{name}/

%dir %{_sysconfdir}/%{name}/

# ---------------

%files -n libgs-devel
%{_libdir}/libgs.so
%{_includedir}/%{name}/
%{_includedir}/ijs
%{_includedir}/ijs/*
%{_libdir}/pkgconfig/ijs.pc
%{_libdir}/libijs.so

# ---------------

%files
%{_bindir}/gs
%{_bindir}/gsnd
%{_bindir}/ghostscript

# Useful conversion scripts:
%{_bindir}/eps2*
%{_bindir}/dvipdf
%{_bindir}/pdf2*
%{_bindir}/ps2*

# Useful scripts for working with fonts:
%{_bindir}/pf2afm
%{_bindir}/pfbtopfa
%{_bindir}/printafm

# Useful scripts for printing:
%{_bindir}/gsbj
%{_bindir}/gsdj
%{_bindir}/gsdj500
%{_bindir}/gslj
%{_bindir}/gslp
%{_bindir}/pphs

# Scripts for setting up LPR:
%{_bindir}/lprsetup.sh
%{_bindir}/unix-lpr.sh

# X11 driver:
%{_libdir}/%{name}/

%{_mandir}/man1/*
%lang(de) %{_mandir}/de/man1/*

# ---------------

%files gtk
%{_bindir}/gsx

# ---------------

%files cups
%{_datadir}/cups/mime/*
%{_datadir}/cups/model/*
%{_cups_serverbin}/filter/*

# ---------------

%files doc
%doc %{_docdir}/%{name}/

# =============================================================================

%changelog
* Tue Apr 02 2019 Martin Osvald <mosvald@redhat.com> - 9.25-2
- obsoleted old ghostscript-devel to allow clean upgrade to libgs-devel

* Thu Feb 14 2019 Martin Osvald <mosvald@redhat.com> - 9.25-1
- Rebase to latest upstream version (bug #1636115)
- Resolves: #1673399 - CVE-2019-3839 ghostscript: missing attack vector
  protections for CVE-2019-6116
- Resolves: #1678172 - CVE-2019-3835 ghostscript: superexec operator
  is available (700585)
- Resolves: #1680026 - CVE-2019-3838 ghostscript: forceput in DefineResource
  is still accessible (700576)
- Resolves: #1670443 - ghostscript: Regression: double comment chars
  '%%' in gs_init.ps leading to missing metadata
- fix for pdf2dsc regression added to allow fix for CVE-2019-3839

* Wed Jan 16 2019 Martin Osvald <mosvald@redhat.com> - 9.07-32
- Remove as many non-standard operators as possible to make the codebase
  closer to upstream for later CVEs
- Resolves: #1621385 - CVE-2018-16511 ghostscript: missing type check in type
  checker (699659)
- Resolves: #1649722 - CVE-2018-16539 ghostscript: incorrect access checking
  in temp file handling to disclose contents of files (699658) 
- Resolves: #1621162 - CVE-2018-15908 ghostscript: .tempfile file permission
  issues (699657)
- Resolves: #1621384 - CVE-2018-15909 ghostscript: shading_param incomplete
  type checking (699660)
- Resolves: #1652902 - CVE-2018-16863 ghostscript: incomplete fix for
  CVE-2018-16509
- Resolves: #1654045 ghostscript update breaks xdvi (gs: Error: /undefined in flushpage)
- Resolves: #1651150 - CVE-2018-15911 ghostscript: uninitialized memory
  access in the aesdecode operator (699665)
- Resolves: #1650061 - CVE-2018-16802 ghostscript: Incorrect "restoration of
  privilege" checking when running out of stack during exception handling
- Resolves: #1652936 - CVE-2018-19409 ghostscript: Improperly implemented
  security check in zsetdevice function in psi/zdevice.c
- Resolves: #1654622 - CVE-2018-16541 ghostscript: incorrect free logic in
  pagedevice replacement (699664)
- Resolves: #1650211 - CVE-2018-17183 ghostscript: User-writable error
  exception table
- Resolves: #1645517 - CVE-2018-18073 ghostscript: saved execution stacks
  can leak operator arrays
- Resolves: #1648892 - CVE-2018-17961 ghostscript: saved execution stacks
  can leak operator arrays (incomplete fix for CVE-2018-17183)
- Resolves: #1643117 - CVE-2018-18284 ghostscript: 1Policy operator
  allows a sandbox protection bypass
- Resolves: #1655939 - CVE-2018-19134 ghostscript: Type confusion in
  setpattern (700141)
- Resolves: #1657694 - ghostscript: Regression: Warning: Dropping incorrect
  smooth shading object (Error: /rangecheck in --run--)
- Resolves: #1661210 pdf2ps reports an error when reading from stdin
- Resolves: #1657334 - CVE-2018-16540 ghostscript: use-after-free in
  copydevice handling (699661)
- Resolves: #1660570 - CVE-2018-19475 ghostscript: access bypass in
  psi/zdevice2.c (700153)
- Resolves: #1660829 - CVE-2018-19476 ghostscript: access bypass in
  psi/zicc.c
- Resolves: #1661279 - CVE-2018-19477 ghostscript: access bypass in
  psi/zfjbig2.c (700168)
- Resolves: #1667443 - CVE-2019-6116 ghostscript: subroutines within
  pseudo-operators must themselves be pseudo-operators
- Resolves: #1670443 - ghostscript: Regression: double comment chars
  '%%' in gs_init.ps leading to missing metadata

* Mon Sep 10 2018 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-31
- Added security fixes for:
  - CVE-2018-16509 (bug #1621158)
  - CVE-2018-15910 (bug #1621160)
  - CVE-2018-16542 (bug #1621382)

* Tue Apr 17 2018 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-30
- Fix MediaPosition, ManualFeed and MediaType with pxl devices (bug #1551782)

* Tue Jul 25 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-29
- Fix rare Segmentation fault when converting PDF to PNG (bug #1473337)
- Raise the default VMThreshold from 1Mb to 8Mb (bug #1479852)

* Thu May 11 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-28
- Security fix for CVE-2017-8291 updated to address SIGSEGV

* Wed May 03 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-27
- Added security fix for CVE-2017-8291 (bug #1446063)

* Tue Apr 11 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-26
- Updated requirements for lcms2 to avoid possible issues in the future

* Thu Apr 06 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-25
- Added security fix for CVE-2017-7207 (bug #1434353)
- Added explicit requirement for lcms2 version we are build with (bug #1436273)

* Tue Mar 21 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-24
- Fix infinite 'for' loop in gdevp14.c file (bug #1424752)

* Wed Feb 15 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-23
- Fix for regression caused by previous CVE fixes (bug #1411725)

* Tue Jan 10 2017 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-22
- Fix of SIGSEGV in cid_font_data_param when using ps2pdf (bug #1390847)

* Thu Nov  3 2016 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-21
- Added security fixes for:
  - CVE-2013-5653 (bug #1380327)
  - CVE-2016-7977 (bug #1380415)
  - CVE-2016-7978 (bug #1382300)
  - CVE-2016-7979 (bug #1382305)
  - CVE-2016-8602 (bug #1383940)

* Wed Jul 13 2016 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-20
- Fixed some complains of CovScan in ghostscript-hanging-in-convert.patch

* Thu Jun  2 2016 David Kaspar [Dee'Kej] <dkaspar@redhat.com> - 9.07-19
- Import LCMS2 2.6 rebase changes into ghostscript (bug #959351)
- Fix hanging of ghostscript when converting PDF -> PNG (bug #1302121)
- Do not SIGSEGV after icc_profile error, report error instead (bug #1243784)
- Fix the color printing on HP InkJet printers (bug #1225858)

* Wed Sep 24 2014 Tim Waugh <twaugh@redhat.com> 9.07-18
- Applied patch from upstream to fix memory handling issue that could
  lead to crashes (bug #1105519).

* Fri Sep  5 2014 Tim Waugh <twaugh@redhat.com> 9.07-17
- Fix insufficient integer digits in trio's rendering of "%g" (bug #1096158).

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 9.07-16
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 9.07-15
- Mass rebuild 2013-12-27

* Fri Dec 13 2013 Tim Waugh <twaugh@redhat.com> 9.07-14
- Filter costs for gstoraster tweaked again (bug #1032117).

* Wed Sep 25 2013 Tim Waugh <twaugh@redhat.com> 9.07-13
- Regenerate tarball (bug #1012902).

* Wed Aug 21 2013 Tim Waugh <twaugh@redhat.com> 9.07-12
- Tweak filter costs for gstoraster (part of bug #998977).

* Thu Jul 18 2013 Tim Waugh <twaugh@redhat.com> 9.07-11
- Remove bundled (and unused) lcms source.
- Fixed license tag (AGPLv3+).

* Wed Jul 17 2013 Tim Waugh <twaugh@redhat.com> 9.07-10
- Added in missing part of gs_sprintf backport: add in the header to
  stdio_.h. Without this there are problems with va_args on some
  platforms (bug #979681).

* Mon Jul  8 2013 Tim Waugh <twaugh@redhat.com> 9.07-9
- Upstream patch from bug #693921 to avoid zfapi crash (bug #969785).

* Mon Jul  1 2013 Tim Waugh <twaugh@redhat.com> 9.07-8
- Use correct colord device ID in gstoraster.

* Mon Jul  1 2013 Tim Waugh <twaugh@redhat.com> 9.07-7
- Use more caution when converting floats to strings (bug #980085).

* Tue Jun 18 2013 Tim Waugh <twaugh@redhat.com> 9.07-6
- Upstream patch from bug #690692 to handle strange fonts (bug #969660).

* Fri May 17 2013 Tim Waugh <twaugh@redhat.com> 9.07-5
- Remove pdfopt man pages which were mistakenly left in (bug #963882).

* Thu May 16 2013 Tim Waugh <twaugh@redhat.com> 9.07-4
- Upstream patch to fix pdfwrite segfault (bug #962120).

* Thu May  9 2013 Tim Waugh <twaugh@redhat.com> - 9.07-3
- Back-ported locale fix (bug #961149).

* Thu Apr 25 2013 Tim Waugh <twaugh@redhat.com>
- Unowned directories (bug #902525).

* Mon Apr  8 2013 Tim Waugh <twaugh@redhat.com> - 9.07-2
- Rebuilt.

* Fri Mar  8 2013 Tim Waugh <twaugh@redhat.com> - 9.07-1
- 9.07.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.06-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 18 2013 Adam Tkac <atkac redhat com> - 9.06-6
- rebuild due to "jpeg8-ABI" feature drop

* Fri Jan  4 2013 Tim Waugh <twaugh@redhat.com> - 9.06-5
- Updated build requirement from gtk2-devel to gtk3-devel so that gsx
  gets built using the correct loader (bug #884483).

* Fri Dec 21 2012 Adam Tkac <atkac redhat com> - 9.06-4
- rebuild against new libjpeg

* Thu Sep 27 2012 Tim Waugh <twaugh@redhat.com> - 9.06-3
- Remove cups/libs to avoid bundling, although it isn't built in any
  case.

* Tue Sep  4 2012 Tim Waugh <twaugh@redhat.com> - 9.06-2
- Fixed encoding of German ps2pdf man page (bug #853764).

* Wed Aug  8 2012 Tim Waugh <twaugh@redhat.com> - 9.06-1
- 9.06.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.05-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Tim Waugh <twaugh@redhat.com> - 9.05-4
- Ship pkg-config file for ijs (bug #840830).

* Mon Apr 30 2012 Tim Waugh <twaugh@redhat.com> - 9.05-3
- Removed more bundled packages (bug #816747).
- Fixed missing error check when setting ICC profile.

* Thu Apr 26 2012 Jon Ciesla <limburgher@gmail.com> - 9.05-2
- Fixed encodings and changelog version for merge review BZ 225795.

* Thu Feb  9 2012 Tim Waugh <twaugh@redhat.com> 9.05-1.1
- Avoid mixed tabs and spaces in spec file.

* Thu Feb  9 2012 Tim Waugh <twaugh@redhat.com> 9.05-1
- 9.05.

* Fri Jan  6 2012 Tim Waugh <twaugh@redhat.com> 9.04-9
- Use %%_cups_serverbin macro.

* Fri Jan  6 2012 Tim Waugh <twaugh@redhat.com> 9.04-8
- Rebuilt for GCC 4.7.

* Tue Nov  8 2011 Tim Waugh <twaugh@redhat.com> 9.04-7
- Applied fix for type 1 font copying code SEAC scanner (bug #728710).

* Mon Nov  7 2011 Tim Waugh <twaugh@redhat.com> 9.04-6
- Rebuilt for new libpng.

* Tue Nov  1 2011 Tim Waugh <twaugh@redhat.com> 9.04-5
- Applied upstream fix for skipping "cached" outline glyphs (bug #742349).

* Wed Aug 31 2011 Tim Waugh <twaugh@redhat.com> 9.04-4
- Fixed typo (EXTRAFLAGS -> EXTRACFLAGS).

* Mon Aug 22 2011 Tim Waugh <twaugh@redhat.com> 9.04-3
- Updated upstream fix for gdevcups RGBW handling (Ghostscript bug #691922).

* Tue Aug 16 2011 Tim Waugh <twaugh@redhat.com> 9.04-2
- Applied upstream fix for gdevcups handling of RGBW (Ghostscript
  bug #691922).

* Mon Aug  1 2011 Tim Waugh <twaugh@redhat.com> 9.04-1
- 9.04.

* Mon Aug  1 2011 Tim Waugh <twaugh@redhat.com> 9.02-5
- No longer need jbig2-image-refcount patch.
- Fixed error reporting in the gstoraster filter.

* Wed May 25 2011 Tim Waugh <twaugh@redhat.com> 9.02-4
- colord is optional (bug #706619).

* Tue Apr 12 2011 Tim Waugh <twaugh@redhat.com> 9.02-3
- Prevent segfault when running gstoraster outside CUPS.

* Thu Apr  7 2011 Tim Waugh <twaugh@redhat.com>
- Remove bundled expat directory.  Not used, but this makes it
  clearer.

* Wed Apr  6 2011 Tim Waugh <twaugh@redhat.com> 9.02-2
- pxl: match landscape page sizes (bug #692165).

* Mon Apr  4 2011 Tim Waugh <twaugh@redhat.com>
- Fixed source URL.

* Mon Apr  4 2011 Tim Waugh <twaugh@redhat.com> 9.02-1
- 9.02.

* Thu Mar 10 2011 Tim Waugh <twaugh@redhat.com> 9.01-3
- colord support: prefix printer name with "cups-" to get device ID.

* Thu Feb 10 2011 Richard Hughes <rhughes@redhat.com> 9.01-2
- Backport a patch from svn trunk to enable colord support.

* Thu Feb 10 2011 Tim Waugh <twaugh@redhat.com> 9.01-1
- 9.01.  No longer needed gdevcups-691733, glyph-stretch-691920,
  icc-fix, scan_token, or system-jasper patches.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.00-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb  2 2011 Tim Waugh <twaugh@redhat.com> 9.00-13
- Applied fix for upstream bug #691920.

* Fri Jan 28 2011 Tim Waugh <twaugh@redhat.com> 9.00-12
- Use poppler-data for CMaps (bug #630632).

* Mon Jan 17 2011 Tim Waugh <twaugh@redhat.com> 9.00-11
- Fixed macro in comment.
- Include full source URL.

* Fri Jan 14 2011 Tim Waugh <twaugh@redhat.com> 9.00-10
- Avoid symbol clash with scan_token (bug #590914).

* Mon Jan 10 2011 Tim Waugh <twaugh@redhat.com> 9.00-9
- Replaced width-and-height patch with the one actually used upstream.

* Fri Jan  7 2011 Tim Waugh <twaugh@redhat.com> 9.00-8
- Applied upstream ICC fix (bug #655449).
- gdevcups: use correct width and height values when allocating memory
  (upstream bug 691733).

* Fri Nov 26 2010 Tim Waugh <twaugh@redhat.com> 9.00-7
- Fixed more summaries ending with ".".

* Thu Oct 21 2010 Tim Waugh <twaugh@redhat.com> 9.00-6
- Own more directories (bug #645075).

* Thu Oct 14 2010 Tim Waugh <twaugh@redhat.com> 9.00-5
- gdevcups: don't use uninitialized variables in debugging output
  (Ghostscript bug #691683).

* Fri Oct  1 2010 Tim Waugh <twaugh@redhat.com> 9.00-4
- Reverted incorrect change introduced to fix bug #635786.

* Thu Sep 30 2010 Tim Waugh <twaugh@redhat.com> 9.00-3
- Don't use carriage return in ps2epsi output (bug #635786).
- Include more documentation (bug #634354).

* Wed Sep 29 2010 jkeating - 9.00-2
- Rebuilt for gcc bug 634757

* Thu Sep 23 2010 Tim Waugh <twaugh@redhat.com> 9.00-1
- Updated to 9.00.  No longer need -P-, CVE-2009-4270, CVE-2010-1628,
  SEARCH_HERE_FIRST, bbox-close, cups-realloc-color-depth,
  epstopdf-failure, fPIC, gdevcups-ripcache, iname-segfault, ldfalgs,
  pdf2dsc, pdftoraster-exit, tif-fail-close, tiff-default-strip-size,
  or tiff-fixes patches.

* Mon Sep 13 2010 Tim Waugh <twaugh@redhat.com> 8.71-16
- Pulled in gs_fonts.ps modification for .runlibfileifexists from
  OpenSUSE package (bug #610301).

* Fri Sep  3 2010 Tim Waugh <twaugh@redhat.com> 8.71-15
- Restored Fontmap.local patch, incorrectly dropped after
  ghostscript-8.15.4-3 (bug #610301).
- Applied patch to let gdevcups use automatic memory allocation.  Use
  RIPCache=auto in /etc/cups/cupsd.conf to enable.
- Applied patch to fix NULL dereference in bbox driver (bug #591624).
- Applied upstream patch to fix iname.c segfault (bug #465311).

* Thu Aug 26 2010 Tim Waugh <twaugh@redhat.com> 8.71-14
- Avoid epstopdf failure using upstream patch (bug #627390).
- More upstream fixes for bug #599564.

* Wed Aug 25 2010 Tim Waugh <twaugh@redhat.com> 8.71-13
- Fix implementation of -P- (bug #599564).
- Use -P- and -dSAFER in scripts (bug #599564).

* Wed Aug 25 2010 Tim Waugh <twaugh@redhat.com> 8.71-12
- Change SEARCH_HERE_FIRST default to make -P- default instead of -P
  (bug #599564).
- Removed redundant gs-executable patch (bug #502550).

* Thu Aug  5 2010 Tim Waugh <twaugh@redhat.com> 8.71-11
- Avoid another NULL pointer dereference in jbig2 code (bug #621569).

* Fri Jul 16 2010 Tim Waugh <twaugh@redhat.com> 8.71-10
- Applied patch to fix CVE-2010-1628 (memory corruption at PS stack
  overflow, bug #592492).

* Tue Mar 16 2010 Tim Waugh <twaugh@redhat.com> 8.71-9
- Backported some more TIFF fixes (bug #573970).
- Use upstream fix for TIFF default strip size (bug #571520).

* Mon Mar 15 2010 Tim Waugh <twaugh@redhat.com> 8.71-8
- Restore the TIFF default strip size of 0 (bug #571520).
- Don't segfault closing tiffg3 device if opening failed (bug #571520).
- Don't revert gdevcups y-axis change (bug #541604).
- Reallocate memory in gdevcups when color depth changes (bug #563313).

* Fri Mar  5 2010 Tim Waugh <twaugh@redhat.com> 8.71-7
- Don't own the %%{_datadir}/ghostscript or
  %%{_datadir}/ghostscript/conf.d directories as the filesystem
  package already does (bug #569442).

* Wed Mar  3 2010 Tim Waugh <twaugh@redhat.com> 8.71-6
- Fixed summary.
- Fixed macros in changelog.
- Avoid mixed spaces and tabs.
- Ship COPYING file.
- Added comments for all patches.
- More consistent macro use.

* Mon Feb 22 2010 Tim Waugh <twaugh@redhat.com> 8.71-5
- The doc subpackage is now noarch (bug #567179).

* Sat Feb 20 2010 Tim Waugh <twaugh@redhat.com> 8.71-4
- Actually revert the upstream gdevcups changes (bug #563313).
- Fixed pdf2dsc.ps (bug #565935).
- Use fixed patch for LDFLAGS to make sure libgs.so gets a soname
  (bug #565935).

* Fri Feb 19 2010 Tim Waugh <twaugh@redhat.com> 8.71-3
- Fixed LDFLAGS when building dynamically linked executables (bug #565935).

* Wed Feb 17 2010 Tim Waugh <twaugh@redhat.com> 8.71-2
- Use system libtiff.

* Wed Feb 17 2010 Tim Waugh <twaugh@redhat.com> 8.71-1
- 8.71 (bug #565935).

* Tue Feb 16 2010 Tim Waugh <twaugh@redhat.com> 8.70-7
- Reverted gdevcups duplex changes as they cause a regression
  (see bug #563313).

* Mon Jan 25 2010 Tim Waugh <twaugh@redhat.com> 8.70-6
- Fixed pdftoraster so that it waits for its sub-process to exit.
- Another gdevcups duplex fix from upstream revision 10631
  (bug #541604).

* Fri Jan 22 2010 Tim Waugh <twaugh@redhat.com> 8.70-5
- Don't build static library for ijs (bug #556051).

* Thu Jan 21 2010 Tim Waugh <twaugh@redhat.com> 8.70-4
- Fixed gdevcups duplex output (bug #541604) by backporting upstream
  revision 10625.

* Thu Dec 24 2009 Tim Waugh <twaugh@redhat.com> 8.70-3
- Don't ship libtool la files (bug #542674).
- Fix debugging output from gdevcups (CVE-2009-4270, bug #540760).
- Harden ghostscript's debugging output functions (bug #540760).

* Thu Oct 15 2009 Tim Waugh <twaugh@redhat.com> 8.70-2
- New cups sub-package for pstoraster/pdftoraster/pstopxl.

* Mon Aug  3 2009 Tim Waugh <twaugh@redhat.com> 8.70-1
- 8.70.
- License has changed to GPLv3+.  Packages containing programs that
  link to libgs/libijs are:
  - foomatic (GPLv2+)
  - libspectre (GPLv2+)
  - ImageMagick (ImageMagick, listed on Licensing wiki page under
    "Good Licenses" and marked as GPLv3 compat)
  - gutenprint (GPLv2+)

* Mon Aug  3 2009 Tim Waugh <twaugh@redhat.com> 8.64-12
- Moved examples to doc subpackage (bug #515167).
- Converted spec file to UTF-8.

* Thu Jul 30 2009 Tim Waugh <twaugh@redhat.com> 8.64-11
- Fixed CVE-2009-0583,0584 patch by using 255 as the maximum number of
  points, not 100, and by not treating a missing black point tag as an
  error (bug #487744).

* Thu Jul 30 2009 Rex Dieter <rdieter@fedoraproject.org> - 8.64-10
- License: GPLv2 and Redistributable, no modification permitted (bug #487510)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.64-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 10 2009 Tim Waugh <twaugh@redhat.com> 8.64-8
- Fix scripts so they don't get broken on install (bug #502550).

* Thu Jun  4 2009 Tim Waugh <twaugh@redhat.com> 8.64-7
- Applied patch to fix NULL dereference in JBIG2 decoder (bug #503995).

* Wed Apr 15 2009 Tim Waugh <twaugh@redhat.com> 8.64-6
- Applied patch to fix CVE-2009-0792 (bug #491853).
- Applied patch to fix CVE-2009-0196 (bug #493379).

* Fri Mar 20 2009 Tim Waugh <twaugh@redhat.com> 8.64-5
- Applied patch to fix CVE-2009-0583 (bug #487742) and CVE-2009-0584
  (bug #487744).

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.64-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Tim Waugh <twaugh@redhat.com> 8.64-3
- Fix bitcmyk driver (bug #486644).

* Wed Feb  4 2009 Tim Waugh <twaugh@redhat.com> 8.64-2
- 8.64 (bug #483958).
- Removed trade marks to avoid any potential confusion.

* Fri Oct 17 2008 Tim Waugh <twaugh@redhat.com>
- Removed last patch (unsuccessful).

* Fri Oct 17 2008 Tim Waugh <twaugh@redhat.com> 8.63-4
- Try out a work-around for bug #465311.

* Wed Oct 15 2008 Tim Waugh <twaugh@redhat.com> 8.63-3
- Don't ship fixmswrd.pl as it pulls in perl (bug #463948).

* Tue Oct 14 2008 Tim Waugh <twaugh@redhat.com> 8.63-2
- Split out a doc sub-package (bug #466507).

* Mon Aug  4 2008 Tim Waugh <twaugh@redhat.com> 8.63-1
- 8.63.  No longer need r8591 or incomplete-ccittfax patches.
- Compile without strict aliasing opts due to warnings across several
  files.
- Don't run autogen.sh for main package, just for ijs which doesn't
  ship with a configure script.

* Mon Jun 23 2008 Tim Waugh <twaugh@redhat.com> 8.62-4
- Applied patch to work around bug #229174.
- Applied patch from upstream to fix box_fill_path for shfill (bug #452348).

* Mon Mar 31 2008 Tim Waugh <twaugh@redhat.com> 8.62-3
- Fix pksmraw output (bug #308211).

* Tue Mar  4 2008 Tim Waugh <twaugh@redhat.com> 8.62-2
- No longer need CVE-2008-0411 patch.
- Don't ship URW fonts; we already have them.

* Tue Mar  4 2008 Tim Waugh <twaugh@redhat.com> 8.62-1
- 8.62.  No longer need IJS KRGB patch, or patch for gs bug 689577.

* Wed Feb 27 2008 Tim Waugh <twaugh@redhat.com> 8.61-10
- Applied patch to fix CVE-2008-0411 (bug #431536).

* Fri Feb 22 2008 Tim Waugh <twaugh@redhat.com> 8.61-9
- Build with jasper again (bug #433897).  Build requires jasper-devel, and
  a patch to remove jas_set_error_cb reference.

* Wed Feb 13 2008 Tim Waugh <twaugh@redhat.com> 8.61-8
- Rebuild for GCC 4.3.

* Mon Jan 28 2008 Tim Waugh <twaugh@redhat.com> 8.61-7
- Don't build with jasper support.
- Remove bundled libraries.

* Tue Dec 11 2007 Tim Waugh <twaugh@redhat.com> 8.61-6
- Applied upstream patch for bug #416321.

* Fri Nov 30 2007 Tim Waugh <twaugh@redhat.com> 8.61-5
- Fixed runlibfileifexists patch.

* Fri Nov 30 2007 Tim Waugh <twaugh@redhat.com> 8.61-4
- Revert previous change, but define .runlibfileifexists, not just
  runlibfileifexists.

* Wed Nov 28 2007 Tim Waugh <twaugh@redhat.com> 8.61-3
- No longer need runlibfileifexists.
- Use runlibfile in cidfmap.

* Wed Nov 28 2007 Tim Waugh <twaugh@redhat.com> 8.61-2
- Add /usr/share/fonts to fontpath (bug #402551).
- Restore cidfmap-switching bits, except for FAPIcidfmap which is no
  longer used.
- Add runlibfileifexists to gs_init.ps.
- Build with --disable-compile-inits (bug #402501).

* Fri Nov 23 2007 Tim Waugh <twaugh@redhat.com> 8.61-1
- 8.61.

* Tue Oct 23 2007 Tim Waugh <twaugh@redhat.com> 8.60-5
- Applied patch from upstream to fix CVE-2007-2721 (bug #346511).

* Tue Oct  9 2007 Tim Waugh <twaugh@redhat.com> 8.60-4
- Marked localized man pages as %%lang (bug #322321).

* Thu Sep 27 2007 Tim Waugh <twaugh@redhat.com> 8.60-3
- Back-ported mkstemp64 patch (bug #308211).

* Thu Aug 23 2007 Tim Waugh <twaugh@redhat.com> 8.60-2
- More specific license tag.

* Fri Aug  3 2007 Tim Waugh <twaugh@redhat.com> 8.60-1
- 8.60.

* Mon Jul 16 2007 Tim Waugh <twaugh@redhat.com> 8.60-0.r8112.2
- Own %%{_libdir}/ghostscript (bug #246026).

* Tue Jul 10 2007 Tim Waugh <twaugh@redhat.com> 8.60-0.r8112.1
- 8.60 snapshot from svn.  Patches dropped:
  - big-cmap-post
  - split-cidfnmap
  - exactly-enable-cidfnmap
  - Fontmap.local
  No longer needed:
  - gxcht-64bit-crash

* Tue Apr 17 2007 Tim Waugh <twaugh@redhat.com> 8.15.4-3
- Apply fonts in CIDFnmap even if the same fontnames are already registered
  (bug #163231).
- New file CIDFmap (bug #233966).
- Allow local overrides for FAPIcidfmap, cidfmap and Fontmap (bug #233966).

* Tue Apr  3 2007 Tim Waugh <twaugh@redhat.com> 8.15.4-2
- Fixed configuration file locations (bug #233966).

* Wed Mar 14 2007 Tim Waugh <twaugh@redhat.com> 8.15.4-1
- 8.15.4.

* Thu Jan 25 2007 Tim Waugh <twaugh@redhat.com> 8.15.3-7
- dvipdf script fixes (bug #88906).
- Moved libijs.so and libgs.so into devel package (bug #203623).

* Wed Jan 24 2007 Tim Waugh <twaugh@redhat.com> 8.15.3-6
- Configure with --with-drivers=ALL since the advertised default is not
  what gets used (bug #223819).

* Thu Jan 18 2007 Tim Waugh <twaugh@redhat.com> 8.15.3-5
- Backported gxcht 64bit crash fix from GPL trunk (bug #177763).

* Fri Jan 12 2007 Tim Waugh <twaugh@redhat.com> 8.15.3-4
- Own cjkv directory (bug #221380, bug #222375).

* Tue Dec  5 2006 Tim Waugh <twaugh@redhat.com> 8.15.3-3
- Added split-cidfnmap patch (bug #194592).

* Thu Nov 16 2006 Tim Waugh <twaugh@redhat.com> 8.15.3-2
- 8.15.3.  No longer need gtk2, ps2epsi, badc, pagesize,
  use-external-freetype, split-font-configuration or cjkv patches.
- Renumbered patches.

* Tue Oct  3 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-9
- Apply CJKV patch from svn164:165 plus the fix from svn173:174 (bug #194592,
  bug #203712, possibly bug #167596).

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 8.15.2-8.1
- rebuild

* Fri Jun 23 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-8
- Revert CJKV patch.

* Wed Jun 14 2006 Tomas Mraz <tmraz@redhat.com> - 8.15.2-7
- rebuilt with new gnutls

* Tue Jun 13 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-6
- Undo svn sync.
- Apply CJKV patch from svn164:165.

* Fri Jun  9 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-5
- Sync to svn165.

* Fri May 26 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-4
- Fix ijs-config not to have multilib conflicts (bug #192672)

* Tue May  2 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-3
- Remove adobe-cmaps and acro5-cmaps, since latest CMaps are already
  included (bug #190463).

* Tue Apr 25 2006 Tim Waugh <twaugh@redhat.com> 8.15.2-2
- 8.15.2.
- No longer need build, krgb, pdfwrite, str1570 patches.

* Mon Apr 24 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-10
- Fix emacs interaction (bug #189321, STR #1570).

* Mon Apr 10 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-9
- Add %%{_datadir}/fonts/japanese to font path (bug #188448).
- Spec file cleanups (bug #188066).

* Sat Apr  8 2006 Tim Waugh <twaugh@redhat.com>
- Build requires libtool (bug #188341).

* Thu Apr  6 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-8
- Fix pdfwrite (bug #187834).
- CUPS filters go in /usr/lib/cups/filter even on lib64 platforms.

* Thu Mar  2 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-7
- BuildRequires: gnutls-devel
- Updated KRGB patch for gdevijs.

* Tue Feb 28 2006 Karsten Hopp <karsten@redhat.de> 8.15.1-6
- BuildRequires: libXt-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 8.15.1-5.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 8.15.1-5.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 30 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-5
- Updated adobe-cmaps to 200406 (bug #173613).

* Fri Jan 27 2006 Tim Waugh <twaugh@redhat.com> 8.15.1-4
- Support reading a big cmap/post table from a TrueType font.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov  9 2005 Tomas Mraz <tmraz@redhat.com> 8.15.1-3
- Build does not explicitly require xorg-x11-devel.

* Wed Nov  9 2005 Tomas Mraz <tmraz@redhat.com> 8.15.1-2
- rebuilt with new openssl

* Mon Sep 26 2005 Tim Waugh <twaugh@redhat.com> 8.15.1-1
- Some directories should be "8.15" not "8.15.1" (bug #169198).

* Thu Sep 22 2005 Tim Waugh <twaugh@redhat.com> 8.15.1-0.1
- 8.15.1.
- No longer need overflow patch.

* Tue Aug 16 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc4.3
- Rebuilt for new cairo.

* Mon Aug 15 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc4.2
- Parametrize freetype, and disable it (bug #165962).

* Fri Aug 12 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc4.1
- 8.15rc4.
- Fixed lips4v driver (bug #165713).

* Tue Aug  9 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.7
- Install adobe/acro5 CMaps (bug #165428).

* Mon Jul 18 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.6
- Fixed split font configuration patch (bug #161187).

* Wed Jul 13 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.5
- Split font configuration (bug #161187).
- Reverted this change:
  - Build requires xorg-x11-devel, not XFree86-devel.

* Tue Jul 12 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.4
- Add Japanese fonts to FAPIcidfmap (bug #161187).
- Moved Resource directory.
- Added use-external-freetype patch (bug #161187).

* Mon Jul 11 2005 Tim Waugh <twaugh@redhat.com>
- Build requires libtiff-devel (bug #162826).

* Thu Jun  9 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.3
- Build requires xorg-x11-devel, not XFree86-devel.
- Include ierrors.h in the devel package.

* Wed Jun  8 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.2
- Drop 'Provides: libijs.so' because it is incorrect.
- Build igcref.c with -O0 to work around bug #150771.
- Renumber patches.

* Fri Jun  3 2005 Tim Waugh <twaugh@redhat.com> 8.15-0.rc3.1
- Switch to ESP Ghostscript.
- 8.15rc3.
- Lots of patches dropped.  Perhaps some will need to be re-added.

* Thu Mar 10 2005 Tim Waugh <twaugh@redhat.com> 7.07-40
- Build igcref.c with -O0 to work around bug #150771.

* Tue Mar  1 2005 Tim Waugh <twaugh@redhat.com> 7.07-39
- Rebuilt for new GCC.

* Mon Feb 21 2005 Tim Waugh <twaugh@redhat.com> 7.07-38
- Fixes inspired by GCC 4.

* Tue Jan 18 2005 Tim Waugh <twaugh@redhat.com>
- Correct permissions for %%{_datadir}/ghostscript/Resource (bug #145420).

* Fri Dec 10 2004 Tim Waugh <twaugh@redhat.com> 7.07-37
- Fixed missing return statement (bug #136757).

* Thu Dec  9 2004 Tim Waugh <twaugh@redhat.com> 7.07-36
- Remove VFlib2 bits (bug #120498).

* Fri Dec  3 2004 Tim Waugh <twaugh@redhat.com> 7.07-35
- Added /etc/ghostscript to search path and to file manifest (bug #98974).

* Sat Nov 20 2004 Miloslav Trmac <mitr@redhat.com> - 7.07-34
- Convert man pages to UTF-8

* Wed Oct 20 2004 Tim Waugh <twaugh@redhat.com> 7.07-33
- Fix for bug #136322 (temporary files).

* Tue Sep 28 2004 Tim Waugh <twaugh@redhat.com> 7.07-32
- Turn off fontconfig until it's fixed (bug #133353).

* Wed Aug 18 2004 Tim Waugh <twaugh@redhat.com> 7.07-31
- Only ship gsx in the gtk subpackage.

* Fri Aug  6 2004 Tim Waugh <twaugh@redhat.com>
- Run /sbin/ldconfig in %%post/%%postun.
- Stricter requirements for the main package in the subpackages.

* Tue Jul 20 2004 Tim Waugh <twaugh@redhat.com> 7.07-30
- Updated eplaser driver to add alc4000 (bug #128007).

* Fri Jun 25 2004 Tim Waugh <twaugh@redhat.com> 7.07-29
- Prevent pdf2ps generating "null setpagesize" (bug #126446).

* Thu Jun 24 2004 Tim Waugh <twaugh@redhat.com> 7.07-28
- Fix Omni patch assumption about /usr/lib which breaks for multilib
  architectures.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun  1 2004 Tim Waugh <twaugh@redhat.com> 7.07-26
- Removed another debug message from the fontconfig patch.

* Tue Mar  9 2004 Tim Waugh <twaugh@redhat.com> 7.07-25
- Added bjc250gs driver (bug #117860).

* Thu Mar  4 2004 Tim Waugh <twaugh@redhat.com> 7.07-24
- Fix compilation with GCC 3.4.

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 18 2004 Tim Waugh <twaugh@redhat.com> 7.07-23
- Build against gtk2/glib2 (bug #115619).  Patch from W. Michael Petullo.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com> 7.07-22
- rebuilt

* Thu Feb 12 2004 Tim Waugh <twaugh@redhat.com> 7.07-21
- Leave gdevpdfm.c seemingly-mistaken bitwise ops alone (bug #115396).

* Thu Feb  5 2004 Tim Waugh <twaugh@redhat.com> 7.07-20
- Fix compilation with GCC 3.4.

* Wed Jan 28 2004 Tim Waugh <twaugh@redhat.com> 7.07-19
- Attempt to fix gdevcups crash (bug #114256).
- Make gs dynamically link to libgs (bug #114276).
- Fix gdevesmv.c's misuse of const (bug #114250).

* Tue Jan 20 2004 Tim Waugh <twaugh@redhat.com> 7.07-18
- Turn on libgs again (bug #88175).

* Mon Jan 19 2004 Tim Waugh <twaugh@redhat.com> 7.07-17
- Removed stp driver.  Use the IJS version (ijsgimpprint) instead.
- No longer conflicts with foomatic for hpijs versioning.

* Mon Jan 12 2004 Tim Waugh <twaugh@redhat.com> 7.07-16
- Split hpijs out into separate source package.

* Thu Jan 8  2004 Tim Waugh <twaugh@redhat.com>
- Fix several mistakenly-used bitwise operations.

* Tue Jan 6  2004 Tim Waugh <twaugh@redhat.com> 7.07-15
- Build for Fedora Core 1 printer drivers update.
- Conflicts with foomatic before hpijs 1.5 data.
- Make fontconfig optional.

* Sat Dec 13 2003 Tim Waugh <twaugh@redhat.com> 7.07-14
- Disable unnecessary debug messages from fontconfig support.

* Fri Dec  5 2003 Tim Waugh <twaugh@redhat.com> 7.07-13
- Add fontconfig support (bug #111412).

* Thu Nov 27 2003 Tim Waugh <twaugh@redhat.com>
- Build requires libjpeg-devel (bug #110737).

* Tue Nov 11 2003 Tim Waugh <twaugh@redhat.com> 7.07-12
- Updated hpijs to 1.5 (bug #109714).

* Mon Nov 10 2003 Tim Waugh <twaugh@redhat.com>
- Updated lxm3200 patch (bug #109625).

* Tue Sep 30 2003 Tim Waugh <twaugh@redhat.com> 7.07-11
- Updated gdevcups.c from CUPS 1.1.19.
- Apply NOMEDIAATTRS patch from CUPS 1.1.19 (bug #105401).

* Thu Aug 28 2003 Tim Waugh <twaugh@redhat.com>
- Fix lips4v driver (bug #92337).

* Wed Aug 20 2003 Tim Waugh <twaugh@redhat.com> 7.07-10
- Fix compilation problems in hpijs.

* Mon Aug  4 2003 Tim Waugh <twaugh@redhat.com> 7.07-9
- Further fix from bug #100685.

* Thu Jul 31 2003 Tim Waugh <twaugh@redhat.com> 7.07-8
- Further fix from bug #100685.

* Tue Jul 29 2003 Tim Waugh <twaugh@redhat.com> 7.07-7
- Further fix from bug #100685.

* Fri Jul 25 2003 Tim Waugh <twaugh@redhat.com> 7.07-6
- Further fix from bug #100557.

* Thu Jul 24 2003 Tim Waugh <twaugh@redhat.com> 7.07-5
- Further fix from bug #100557.
- Fix bug #100685.

* Wed Jul 23 2003 Tim Waugh <twaugh@redhat.com> 7.07-4
- Fix bug #100557.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com> 7.07-3
- rebuilt

* Tue May 27 2003 Tim Waugh <twaugh@redhat.com>
- Fix sed usage in ps2epsi (bug #89300).

* Tue May 20 2003 Tim Waugh <twaugh@redhat.com> 7.07-2
- HPIJS 1.4 (bug #91219).

* Sun May 18 2003 Tim Waugh <twaugh@redhat.com> 7.07-1
- 7.07.
- Parametrize build_libgs.
- Remove Omni requirement (bug #88177).
- Fix ghostscript-gtk obsoletes: line (bug #88175).

* Thu Apr  3 2003 Tim Waugh <twaugh@redhat.com> 7.06-1
- 7.06.
- Updated config, vflib.fixup patches.
- No longer need dx6, jpeg patches.
- No longer need to add in missed GNU drivers.
- Turn off dj970 driver (hpijs drives that).

* Mon Mar 31 2003 Tim Waugh <twaugh@redhat.com> 7.05-34
- Apply fix for CJK font search method when the fonts are not available
  (bug #83516).
- The gb18030 patch no longer applies here.

* Thu Mar 27 2003 Tim Waugh <twaugh@redhat.com> 7.05-33
- Add some missing font aliases (bug #73342).
- Use the system jpeg library.
- Update hpijs to 1.3.1.
- Update gdevcups.c from cups-1.1.18.

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com> 7.05-32
- debuginfo rebuild

* Fri Feb 21 2003 Elliot Lee <sopwith@redhat.com> 7.05-31
- Add ghostscript-7.05-oob-66421.patch to fix the segfault behind #66421

* Thu Jan 30 2003 Tim Waugh <twaugh@redhat.com> 7.05-30
- Remove rss patch from hpijs (not needed).

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 7.05-29
- rebuilt

* Thu Jan 16 2003 Tim Waugh <twaugh@redhat.com> 7.05-28
- Add Korean font aliases to CIDFnmap CJK resource files (bug #81924).

* Sat Dec 14 2002 Tim Waugh <twaugh@redhat.com> 7.05-27
- Obsolete ghostscript-gtk (bug #79585).
- Omni 121002 patch.

* Tue Dec 10 2002 Tim Waugh <twaugh@redhat.com> 7.05-26
- Don't ship the shared object yet (part of bug #79340).
- Don't make the gtk package, since that needs the shared object.

* Tue Nov 26 2002 Tim Waugh <twaugh@redhat.com> 7.05-25
- Fix level 1 PostScript output (bug #78450).
- No need to carry gomni.c, since it comes from the patch.

* Mon Nov 11 2002 Tim Waugh <twaugh@redhat.com> 7.05-24
- Omni 071902 patch.

* Mon Nov 11 2002 Tim Waugh <twaugh@redhat.com> 7.05-23
- hpijs-1.3, with updated rss patch.
- Fix XLIBDIRS.

* Fri Oct 25 2002 Tim Waugh <twaugh@redhat.com> 7.05-22
- hpijs-rss 1.2.2.

* Mon Oct 14 2002 Tim Waugh <twaugh@redhat.com> 7.05-21
- Set libdir when installing.

* Thu Aug 15 2002 Tim Waugh <twaugh@redhat.com> 7.05-20
- Add cups device (bug #69573).

* Mon Aug 12 2002 Tim Waugh <twaugh@redhat.com> 7.05-19
- Fix the gb18030 patch (bug #71135, bug #71303).

* Sat Aug 10 2002 Elliot Lee <sopwith@redhat.com> 7.05-18
- rebuilt with gcc-3.2 (we hope)

* Fri Aug  9 2002 Tim Waugh <twaugh@redhat.com> 7.05-17
- Add CIDnmap for GB18030 font (bug #71135).
- Fix URL (bug #70734).

* Tue Jul 23 2002 Tim Waugh <twaugh@redhat.com> 7.05-16
- Rebuild in new environment.

* Tue Jul  9 2002 Tim Waugh <twaugh@redhat.com> 7.05-15
- Remove the chp2200 driver again, to fix cdj890 (bug #67578).

* Fri Jul  5 2002 Tim Waugh <twaugh@redhat.com> 7.05-14
- For CJK font support, use CIDFnmap instead of CIDFont
  resources (bug #68009).

* Wed Jul  3 2002 Tim Waugh <twaugh@redhat.com> 7.05-13
- Build requires unzip and gtk+-devel (bug #67799).

* Wed Jun 26 2002 Tim Waugh <twaugh@redhat.com> 7.05-12
- File list tweaking.
- More file list tweaking.

* Tue Jun 25 2002 Tim Waugh <twaugh@redhat.com> 7.05-10
- Rebuild for bootstrap.

* Wed Jun 19 2002 Tim Waugh <twaugh@redhat.com> 7.05-9
- Omni 052902 patch.

* Mon Jun 10 2002 Tim Waugh <twaugh@redhat.com> 7.05-8
- Requires recent version of patchutils (bug #65947).
- Don't ship broken man page symlinks (bug #66238).

* Wed May 29 2002 Tim Waugh <twaugh@redhat.com> 7.05-7
- Put gsx in its own package.

* Tue May 28 2002 Tim Waugh <twaugh@redhat.com> 7.05-6
- New gomni.c from IBM to fix an A4 media size problem.
- Use new Adobe CMaps (bug #65362).

* Sun May 26 2002 Tim Powers <timp@redhat.com> 7.05-5
- automated rebuild

* Wed May 22 2002 Tim Waugh <twaugh@redhat.com> 7.05-4
- New gomni.c from IBM to fix bug #65269 (again).

* Tue May 21 2002 Tim Waugh <twaugh@redhat.com> 7.05-2
- Don't apply bogus parts of vflib patch (bug #65268).
- Work around Omni -sPAPERSIZE=a4 problem (bug #65269).

* Mon May 20 2002 Tim Waugh <twaugh@redhat.com> 7.05-1
- 7.05.
- No longer need mkstemp, vflib.fixup, quoting, or PARANOIDSAFER
  patches.
- Don't apply CJK patches any more (no longer needed).
- Updated Source15, Patch0, Patch10, Patch5, Patch24, Patch14, Patch12.
- Made gdevdmpr.c compile again.
- Move gimp-print to a separate package.
- Ship the shared object too (and a .so file that is dlopened).
- Update Omni patch.  No longer need Omni_path, Omni_quiet, Omni_glib patches.
- Require Omni >= 0.6.1.
- Add patch to fix gtk+ initial window size.
- Add devel package with header files.
- Turn on IJS support.
- Update hpijs to 1.1.
- Don't ship the hpijs binary in the ghostscript package.
- Use -fPIC when building ijs.

* Wed Apr  3 2002 Tim Waugh <twaugh@redhat.com> 6.52-8
- New CIDFonts (bug #61015).

* Wed Apr  3 2002 Tim Waugh <twaugh@redhat.com> 6.52-7
- Fix release numbers of sub packages.
- Handle info files, use ldconfig (bug #62574).

* Tue Mar 19 2002 Tim Waugh <twaugh@redhat.com> 6.52-6
- Fix config patch so that gs --help displays the right thing.
- Don't ship sysvlp.sh.
- Fix some shell scripts.
- Ship escputil man page (bug #58919).

* Mon Feb 11 2002 Tim Waugh <twaugh@redhat.com> 6.52-5
- Add CHP2200 driver (bug #57516).
- Fix gimp-print-4.2.0 so that it builds without cups-config.

* Sat Feb  2 2002 Bill Nottingham <notting@redhat.com> 6.52-4
- do condrestart in %%postun, not %%post

* Fri Feb  1 2002 Bernhard Rosenkraenzer <bero@redhat.com> 6.52-3
- Restart service cups after installing gimp-print-cups

* Sun Jan 27 2002 Bernhard Rosenkraenzer <bero@redhat.com> 6.52-2
- hpijs is finally free - support it.
- Add extra package for CUPS support

* Mon Jan 21 2002 Bernhard Rosenkraenzer <bero@redhat.com> 6.52-1
- Updates:
  - ghostscript 6.52
  - hpdj 2.6 -> pcl3 3.3
  - CJK Patchlevel 3, adobe-cmaps 200109
  - gimp-print 4.2.0
- Adapt patches
- Fix various URLs
- Begin cleaning up spec file
- Fix bugs #21879 and #50923

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Oct 18 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-16
- update the Omni driver, and patch it to seek in /usr/lib/Omni/ first
- require Omni

* Mon Oct 01 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-15
- change -dPARANOIDSAFER to punch a hole for OutputFile

* Mon Sep 17 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-14
- add -dPARANOIDSAFER to let us breathe a little easier in the print spooler.

* Thu Sep 13 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-13
- apply jakub's fix to ghostscript's jmp_buf problems; #49591

* Wed Sep  5 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-12
- fix lprsetup.sh; #50925

* Fri Aug 24 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-11
- added Epson's old eplaseren drivers,
- pointed out by Till Kamppeter <till.kamppeter@gmx.net>

* Tue Aug 21 2001 Paul Howarth <paul@city-fan.org> 6.51-10
- included Samsung GDI driver for ML-4500 printer support.

* Sun Aug 19 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-9
- applied IBM's glib patches for Omni, which now works.
- BE AWARE: we now link against libstdc++ and glib for this, and use a c++
- link stage to do the dirty.
- added glib-devel buildreq and glib req, I don't think we require everything
- yet, I could pull in sasl.

* Sun Aug 19 2001 David Suffield <david_suffield@hp.com> 6.51-8
- Added gs device hpijs and updated gdevhpij.c to hpijs 0.97

* Wed Aug 15 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-7
- pull in ynakai's update to the cjk resources.

* Thu Aug  9 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-6
- turn dmprt and cdj880 back on. for some reason, they work now.
- voodoo, who knows.

* Thu Aug  9 2001 Yukihiro Nakai <ynakai@redhat.com> 6.51-5
- Add cjk resources

* Wed Aug  1 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-4
- applied drepper@redhat.com's patch for #50300
- fixed build deps on zlib-devel and libpng-devel, #49853
- made gs_init.ps a config file; #25096
- O\^/nZ the daTa directorieZ now; #50693

* Tue Jul 24 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-3
- wired up the Resource dir and the Font and CIDFont maps.

* Mon Jul 23 2001 Crutcher Dunnavant <crutcher@redhat.com> 6.51-2
- luckily, I had a spare chicken. Thanks to some work by Nakai, and one last
- desperate search through google, everything /seems/ to be working. I know
- that there are going to be problems in the japanese code, and I need to turn
- on the cjk font map from adobe, but it /works/ at the moment.

* Thu Jun 21 2001 Crutcher Dunnavant <crutcher@redhat.com>
- upgraded to 6.51, a major version upgrade
- rewrote spec file, threw out some patches
- turned on IBM's Omni print drivers interface
- turned on HP's hpijs print drivers interface
- turned on every driver that looked usable from linux
- sacrificed a chicken to integrate the old Japanese drivers
- - This didn't work. The japanese patches are turned off, pending review.
- - I can do loops with C, but the bugs are in Postscript init files

* Wed Apr 11 2001 Crutcher Dunnavant <crutcher@redhat.com>
- added P. B. West's lx5000 driver

* Tue Feb 27 2001 Crutcher Dunnavant <crutcher@redhat.com>
- added xtt-fonts requirement (for VFlib)

* Fri Feb  9 2001 Adrian Havill <havill@redhat.com>
- cmpskit removed as a build prereq

* Thu Feb  8 2001 Crutcher Dunnavant <crutcher@redhat.com>
- merged in some patches that got away:
  * Fri Sep  1 2000 Mitsuo Hamada <mhamada@redhat.com>
  - add support JIS B size
  - fix the problem of reconverting GNUPLOT output

* Thu Feb  8 2001 Crutcher Dunnavant <crutcher@redhat.com>
- switched to japanese for everybody

* Thu Feb  8 2001 Crutcher Dunnavant <crutcher@redhat.com>
- tweaked time_.h to test for linux, and include the right
- header

* Wed Feb  7 2001 Crutcher Dunnavnat <crutcher@redhat.com>
- added the lxm3200 driver

* Mon Dec 11 2000 Crutcher Dunnavant <crutcher@redhat.com>
- merged in the (accendental) branch that contained the mktemp
- and LD_RUN_PATH bug fixes.

* Tue Oct 17 2000 Jeff Johnson <jbj@redhat.com>
- tetex using xdvi with ghostscript patch (#19212).

* Tue Sep 12 2000 Michael Stefaniuc <mstefani@redhat.com>
- expanded the gcc296 patch to fix a compilation issue with the new stp
  driver

* Mon Sep 11 2000 Michael Stefaniuc <mstefani@redhat.com>
- added the stp driver from the gimp-print project.
  It supports high quality printing especialy with Epson Stylus Photo.

* Wed Aug  2 2000 Matt Wilson <msw@redhat.com>
- rebuilt against new libpng

* Wed Aug  2 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up the cdj880 patch (Bug #14978)
- Fix build with gcc 2.96

* Fri Jul 21 2000 Bill Nottingham <notting@redhat.com>
- turn off japanese support

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Fri Jul 07 2000 Trond Eivind Glomsrød <teg@redhat.com>
- fixed the broken inclusion of files in /usr/doc
- Build requires freetype-devel

* Fri Jun 16 2000 Matt Wilson <msw@redhat.com>
- build japanese support in main distribution
- FHS manpage paths

* Sun Mar 26 2000 Chris Ding <cding@redhat.com>
- enabled bmp16m driver

* Thu Mar 23 2000 Matt Wilson <msw@redhat.com>
- added a boatload of Japanese printers

* Thu Mar 16 2000 Matt Wilson <msw@redhat.com>
- add japanese support, enable_japanese macro

* Mon Feb 14 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 5.50 at last...
- hpdj 2.6
- Added 3rd party drivers:
  - Lexmark 5700 (lxm5700m)
  - Alps MD-* (md2k, md5k)
  - Lexmark 2050, 3200, 5700 and 7000 (lex2050, lex3200, lex5700, lex7000)

* Fri Feb  4 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild to compress man page
- fix gs.1 symlink

* Wed Jan 26 2000 Bill Nottingham <notting@redhat.com>
- add stylus 740 uniprint files

* Thu Jan 13 2000 Preston Brown <pbrown@redhat.com>
- add lq850 dot matrix driver (#6357)

* Thu Oct 28 1999 Bill Nottingham <notting@redhat.com>
- oops, include oki182 driver.

* Tue Aug 24 1999 Bill Nottingham <notting@redhat.com>
- don't optimize on Alpha. This way it works.

* Thu Jul 29 1999 Michael K. Johnson <johnsonm@redhat.com>
- added hpdj driver
- changed build to use tar_cat so adding new drivers is sane

* Thu Jul  1 1999 Bill Nottingham <notting@redhat.com>
- add OkiPage 4w+, HP 8xx drivers
* Mon Apr  5 1999 Bill Nottingham <notting@redhat.com>
- fix typo in config patch.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com>
- auto rebuild in the new build environment (release 6)

* Mon Mar 15 1999 Cristian Gafton <gafton@redhat.com>
- added patch from rth to fix alignement problems on the alpha.

* Wed Feb 24 1999 Preston Brown <pbrown@redhat.com>
- Injected new description and group.

* Mon Feb 08 1999 Bill Nottingham <notting@redhat.com>
- add uniprint .upp files

* Sat Feb 06 1999 Preston Brown <pbrown@redhat.com>
- fontpath update.

* Wed Dec 23 1998 Preston Brown <pbrown@redhat.com>
- updates for ghostscript 5.10

* Fri Nov 13 1998 Preston Brown <pbrown@redhat.com>
- updated to use shared urw-fonts package.
* Mon Nov 09 1998 Preston Brown <pbrown@redhat.com>
- turned on truetype (ttf) font support.

* Thu Jul  2 1998 Jeff Johnson <jbj@redhat.com>
- updated to 4.03.

* Tue May 05 1998 Cristian Gafton <gafton@redhat.com>
- enabled more printer drivers
- buildroot

* Mon Apr 27 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Mon Mar 03 1997 Erik Troan <ewt@redhat.com>
- Made /usr/share/ghostscript/3.33/Fontmap a config file.
